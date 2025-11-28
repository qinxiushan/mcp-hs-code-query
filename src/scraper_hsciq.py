"""
HS编码查询工具 - HSCIQ网站爬虫模块
用于从 hsciq.com 网站爬取HS编码数据

创建日期: 2025-11-25
最后更新: 2025-11-25
更新说明: 根据实际网站结构修正URL和参数

网站: https://hsciq.com/HSCN/
搜索URL: https://hsciq.com/HSCN/Search?keywords={query}&viewtype=1&filterFailureCode=true
详情URL: https://hsciq.com/HSCN/Code/{hs_code}

特殊要求: 
- 搜索参数: keywords (商品名), viewtype=1 (固定), filterFailureCode=true (过滤过期)
- 过滤过期编码通过URL参数实现,不需要模拟点击
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional
from src.parser_hsciq import HTMLParserHSCIQ
from src.search_optimizer import SearchOptimizer
from config.settings import (
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    REQUEST_DELAY,
    MAX_SEARCH_ATTEMPTS,
    MIN_SIMILARITY_SCORE
)
from src.utils import retry_on_exception, setup_logger, create_empty_result

logger = logging.getLogger(__name__)


class HSCodeScraperHSCIQ:
    """HSCIQ网站的HS编码爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.base_url = "https://hsciq.com"
        self.search_url = f"{self.base_url}/HSCN/Search"  # 修正搜索URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
        self.parser = HTMLParserHSCIQ()
        self.optimizer = SearchOptimizer(use_embedding=True)
        
        logger.info("HSCIQ爬虫初始化完成")
    
    @retry_on_exception(max_retries=MAX_RETRIES, exceptions=(requests.RequestException,))
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        发送HTTP请求,支持重试
        
        Args:
            url: 请求URL
            method: 请求方法 (GET/POST)
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
        time.sleep(REQUEST_DELAY)  # 请求间隔
        
        return response
    
    def search_products(self, keyword: str, filter_obsolete: bool = True) -> List[Dict]:
        """
        搜索商品,返回搜索结果列表
        
        根据实际网站分析:
        - URL: https://hsciq.com/HSCN/Search
        - 参数: keywords, viewtype=1, filterFailureCode=true
        - 方法: GET请求
        
        Args:
            keyword: 搜索关键词
            filter_obsolete: 是否过滤已作废商品 (默认True)
            
        Returns:
            商品列表,每个商品包含 name, url, hs_code 等信息
        """
        try:
            logger.info(f"在HSCIQ搜索关键词: {keyword}")
            
            # 构造搜索请求参数 (根据实际页面分析)
            search_params = {
                'keywords': keyword,  # 商品名称或HS编码
                'viewtype': '1',      # 固定参数
            }
            
            # 添加过滤过期编码参数
            if filter_obsolete:
                search_params['filterFailureCode'] = 'true'
                logger.debug("已启用过滤过期编码")
                # 这个参数名需要根据实际抓包确定
                search_params['filter_obsolete'] = '1'
                search_params['exclude_expired'] = 'true'
            
            # 发送搜索请求
            response = self._make_request(
                self.search_url,
                method='GET',
                params=search_params
            )
            
            # 解析搜索结果
            results = self.parser.parse_search_results(response.text, keyword)
            if not results:
                logger.warning(f"HSCIQ搜索无结果: {keyword}")
            else:
                logger.info(f"HSCIQ搜索到 {len(results)} 个商品")
            
            return results
            
        except Exception as e:
            logger.error(f"HSCIQ搜索失败: {keyword}, 错误: {e}")
            return []
    
    def get_product_detail(self, url: str) -> Dict:
        """
        获取商品详情
        
        Args:
            url: 商品详情页URL
            
        Returns:
            商品详细信息字典
        """
        try:
            logger.info(f"获取HSCIQ商品详情: {url}")
            
            response = self._make_request(url)
            detail = self.parser.parse_detail_page(response.text, url)
            
            return detail
            
        except Exception as e:
            logger.error(f"获取HSCIQ商品详情失败: {url}, 错误: {e}")
            return {}
    
    def query_by_product_name(self, product_name: str) -> Dict:
        """
        根据商品名称查询HS编码
        
        Args:
            product_name: 商品名称
            
        Returns:
            查询结果字典,包含HS编码和详细信息
        """
        logger.info(f"开始HSCIQ查询: {product_name}")
        
        # 生成搜索关键词
        keywords = self.optimizer.generate_search_keywords(product_name)
        logger.info(f"生成的搜索关键词: {keywords[:5]}")  # 只显示前5个
        
        # 依次尝试每个关键词
        for attempt, keyword in enumerate(keywords[:MAX_SEARCH_ATTEMPTS], 1):
            logger.info(f"尝试第 {attempt} 次搜索,使用关键词: {keyword}")
            
            # 搜索商品
            results = self.search_products(keyword, filter_obsolete=True)
            
            if not results:
                logger.debug(f"关键词 '{keyword}' 无搜索结果,尝试下一个")
                continue
            
            # 计算所有结果的相似度并找到最佳匹配
            best_match = None
            best_similarity = 0.0
            
            for item in results:
                similarity = self.optimizer.calculate_similarity(
                    product_name,
                    item['name']  # 使用搜索结果中的商品名称
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = item
            
            # 检查相似度是否满足阈值
            if best_match and best_similarity >= MIN_SIMILARITY_SCORE:
                logger.info(f"找到匹配商品: {best_match['name']} (相似度: {best_similarity:.2f})")
                
                # 获取详情
                detail_url = best_match.get('url')
                if detail_url:
                    detail = self.get_product_detail(detail_url)
                    
                    if detail and detail.get('hs_code'):
                        # 检查详情页是否标记为已作废
                        if '已作废' not in detail.get('product_name', '') and \
                           '过期' not in detail.get('product_name', ''):
                            # 添加查询相关信息
                            detail['query_product_name'] = product_name
                            detail['search_success'] = True
                            detail['error_message'] = ''
                            
                            logger.info(f"成功获取HS编码: {detail['hs_code']}")
                            return detail
                        else:
                            logger.warning(f"详情页显示商品已作废,尝试下一个候选")
                            continue
            else:
                logger.debug(f"相似度不足 ({best_match.get('similarity', 0):.2f} < {MIN_SIMILARITY_SCORE})")
        
        # 所有尝试都失败
        logger.warning(f"HSCIQ未找到匹配结果: {product_name}")
        return self._create_error_result(
            product_name,
            f"未找到匹配结果,已尝试关键词: {', '.join(keywords[:MAX_SEARCH_ATTEMPTS])}"
        )
    
    def query_by_hs_code(self, hs_code: str) -> Dict:
        """
        根据HS编码查询详细信息
        
        Args:
            hs_code: HS编码
            
        Returns:
            查询结果字典
        """
        try:
            logger.info(f"按HS编码查询HSCIQ: {hs_code}")
            
            # 构造详情页URL
            # 根据页面快照,URL格式可能是: /HSCN/Code/编码
            clean_code = hs_code.replace('.', '').replace(' ', '')
            detail_url = f"{self.base_url}/HSCN/Code/{clean_code}"
            
            # 获取详情
            detail = self.get_product_detail(detail_url)
            
            if detail and detail.get('hs_code'):
                detail['search_success'] = True
                detail['error_message'] = ''
                return detail
            else:
                return self._create_error_result(
                    hs_code,
                    "未找到该HS编码的详细信息"
                )
                
        except Exception as e:
            logger.error(f"按HS编码查询失败: {hs_code}, 错误: {e}")
            return self._create_error_result(hs_code, str(e))
    
    def batch_query(self, product_names: List[str]) -> List[Dict]:
        """
        批量查询商品
        
        Args:
            product_names: 商品名称列表
            
        Returns:
            查询结果列表
        """
        logger.info(f"开始HSCIQ批量查询,共 {len(product_names)} 个商品")
        
        results = []
        for i, product_name in enumerate(product_names, 1):
            logger.info(f"批量查询进度: {i}/{len(product_names)}")
            result = self.query_by_product_name(product_name)
            results.append(result)
            
            # 批量查询时增加延迟
            if i < len(product_names):
                time.sleep(REQUEST_DELAY * 2)
        
        logger.info(f"HSCIQ批量查询完成,成功 {sum(1 for r in results if r.get('search_success'))} 个")
        return results
    
    def _create_error_result(self, query: str, error_message: str) -> Dict:
        """
        创建错误结果字典
        
        Args:
            query: 查询关键词
            error_message: 错误信息
            
        Returns:
            错误结果字典
        """
        return {
            'query_product_name': query,
            'hs_code': '',
            'product_name': '',
            'description': '',
            'declaration_elements': '',
            'first_unit': '',
            'second_unit': '',
            'customs_supervision_conditions': {
                'code': '',
                'details': []
            },
            'inspection_quarantine': {
                'code': '',
                'details': []
            },
            'search_success': False,
            'error_message': error_message
        }
    
    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("HSCIQ爬虫会话已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
