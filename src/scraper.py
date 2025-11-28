"""
网络爬虫模块
"""
import requests
from urllib.parse import urlencode, quote
import time
from typing import Optional, Dict, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    BASE_URL, SEARCH_URL, DETAIL_URL_TEMPLATE,
    REQUEST_TIMEOUT, HEADERS, REQUEST_DELAY
)
from src.utils import setup_logger, retry_on_exception, create_empty_result
from src.parser import DataParser
from src.search_optimizer import SearchOptimizer

logger = setup_logger(__name__)


class HSCodeScraper:
    """HS编码爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.parser = DataParser()
        self.search_optimizer = SearchOptimizer(use_embedding=True)
        logger.info("HSCodeScraper 初始化完成")
    
    @retry_on_exception(exceptions=(requests.RequestException,))
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        发送HTTP请求（带重试机制）
        
        Args:
            url: 请求URL
            method: 请求方法
            **kwargs: 其他请求参数
            
        Returns:
            响应对象
        """
        logger.debug(f"请求 {method} {url}")
        
        if method.upper() == 'GET':
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
        elif method.upper() == 'POST':
            response = self.session.post(url, timeout=REQUEST_TIMEOUT, **kwargs)
        else:
            raise ValueError(f"不支持的请求方法: {method}")
        
        response.raise_for_status()
        
        # 延迟，避免请求过快
        time.sleep(REQUEST_DELAY)
        
        return response
    
    def search_product(self, keyword: str) -> Optional[str]:
        """
        搜索商品，返回第一个匹配结果的详情页URL
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            详情页URL，如果未找到返回None
        """
        try:
            # 构建搜索URL
            # 根据网站分析，直接访问首页并通过关键词参数搜索
            search_url = f"{BASE_URL}/hscode/key/{quote(keyword)}"
            
            logger.info(f"搜索关键词: {keyword}")
            response = self._make_request(search_url)
            
            # 解析搜索结果
            results = self.parser.parse_search_results(response.text, keyword)
            
            if results:
                # 使用相似度匹配找到最佳结果
                product_names = [r['product_name'] for r in results]
                logger.debug(f"提取到的商品名称列表: {product_names[:5]}...")  # 调试：显示前5个
                best_match, score = self.search_optimizer.find_best_match(keyword, product_names)
                
                if best_match:
                    # 找到最匹配的结果
                    for result in results:
                        if result['product_name'] == best_match:
                            logger.info(f"找到匹配结果: {result['hs_code']} - {result['product_name']}")
                            return result['detail_url']
                
                # 如果没有找到相似度足够高的，返回第一个结果
                logger.info(f"使用第一个搜索结果: {results[0]['hs_code']} - {results[0]['product_name']}")
                return results[0]['detail_url']
            else:
                logger.warning(f"关键词 '{keyword}' 未找到搜索结果")
                return None
                
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return None
    
    def get_hs_code_detail(self, detail_url: str) -> Dict:
        """
        获取HS编码详细信息
        
        Args:
            detail_url: 详情页URL
            
        Returns:
            包含所有信息的字典
        """
        try:
            logger.info(f"获取详情: {detail_url}")
            response = self._make_request(detail_url)
            
            # 解析详情页
            result = self.parser.parse_detail_page(response.text)
            return result
            
        except Exception as e:
            logger.error(f"获取详情失败: {str(e)}")
            result = create_empty_result()
            result['error_message'] = str(e)
            return result
    
    def query_by_product_name(self, product_name: str) -> Dict:
        """
        根据商品名称查询HS编码（带智能搜索）
        
        Args:
            product_name: 商品名称
            
        Returns:
            包含所有信息的字典
        """
        logger.info(f"开始查询商品: {product_name}")
        
        # 生成搜索关键词列表
        keywords = self.search_optimizer.generate_search_keywords(product_name)
        
        # 依次尝试每个关键词
        for idx, keyword in enumerate(keywords, 1):
            logger.info(f"尝试关键词 {idx}/{len(keywords)}: {keyword}")
            
            # 搜索并获取所有匹配结果（按相似度排序）
            search_results = self._search_with_all_candidates(keyword, product_name)
            
            if search_results:
                # 尝试每个候选结果（从相似度最高的开始）
                for candidate_idx, (detail_url, similarity, matched_name) in enumerate(search_results, 1):
                    logger.debug(f"尝试候选 {candidate_idx}/{len(search_results)}: {matched_name} (相似度: {similarity:.2f})")
                    
                    # 获取详情
                    result = self.get_hs_code_detail(detail_url)
                    
                    # 检查是否成功且未作废
                    if result['search_success']:
                        result['query_product_name'] = product_name  # 添加原始查询商品名
                        logger.info(f"查询成功: {product_name} -> {result['hs_code']}")
                        return result
                    elif '已作废' in result.get('error_message', ''):
                        logger.debug(f"候选 {candidate_idx} 已作废，尝试下一个")
                        continue
        
        # 所有关键词和候选都未找到有效结果
        logger.warning(f"查询失败: {product_name}，已尝试 {len(keywords)} 个关键词")
        result = create_empty_result()
        result['query_product_name'] = product_name  # 添加原始查询商品名
        result['error_message'] = f"未找到匹配结果，已尝试关键词: {', '.join(keywords)}"
        return result
    
    def _search_with_all_candidates(self, keyword: str, product_name: str) -> List[tuple]:
        """
        搜索并返回所有候选结果（按相似度排序）
        
        Args:
            keyword: 搜索关键词
            product_name: 原始商品名称
            
        Returns:
            [(detail_url, similarity, matched_name), ...] 按相似度降序排列
        """
        try:
            logger.info(f"搜索关键词: {keyword}")
            
            # 构建搜索URL
            search_url = f"{BASE_URL}/hscode/key/{quote(keyword)}"
            response = self._make_request(search_url)
            
            # 解析搜索结果
            results = self.parser.parse_search_results(response.text, product_name)
            
            if results:
                logger.debug(f"提取到的商品名称列表: {[r['product_name'] for r in results][:5]}...")
                
                # 计算所有结果的相似度并排序
                candidates = []
                for item in results:
                    similarity = self.search_optimizer.calculate_similarity(
                        product_name, 
                        item['product_name']
                    )
                    candidates.append((item['detail_url'], similarity, item['product_name']))
                
                # 按相似度降序排序
                candidates.sort(key=lambda x: x[1], reverse=True)
                
                # 记录最佳匹配
                if candidates:
                    best_match = candidates[0]
                    logger.info(f"找到最佳匹配: '{best_match[2]}' (相似度: {best_match[1]:.2f})")
                
                return candidates
            else:
                logger.warning(f"关键词 '{keyword}' 未找到搜索结果")
                return []
                
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    def query_by_hs_code(self, hs_code: str) -> Dict:
        """
        根据HS编码直接查询
        
        Args:
            hs_code: HS编码
            
        Returns:
            包含所有信息的字典
        """
        logger.info(f"根据HS编码查询: {hs_code}")
        
        # 移除HS编码中的点号
        clean_code = hs_code.replace('.', '').replace(' ', '')
        
        # 构建详情URL
        detail_url = DETAIL_URL_TEMPLATE.format(hs_code=clean_code)
        
        # 获取详情
        return self.get_hs_code_detail(detail_url)
    
    def batch_query(self, product_names: List[str]) -> List[Dict]:
        """
        批量查询商品
        
        Args:
            product_names: 商品名称列表
            
        Returns:
            结果列表
        """
        logger.info(f"开始批量查询，共 {len(product_names)} 个商品")
        
        results = []
        for idx, name in enumerate(product_names, 1):
            logger.info(f"处理 {idx}/{len(product_names)}: {name}")
            result = self.query_by_product_name(name)
            results.append(result)
        
        success_count = sum(1 for r in results if r['search_success'])
        logger.info(f"批量查询完成，成功: {success_count}/{len(product_names)}")
        
        return results
    
    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("会话已关闭")
