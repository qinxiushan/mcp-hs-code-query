"""
HTML数据解析模块

修改历史:
- 修复 #001 (2025-11-24): 改进数据解析逻辑和URL处理
  详见: docs/CHANGELOG_001_修复数据解析和URL问题.md
"""
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import setup_logger, safe_get_text, clean_text, create_empty_result

logger = setup_logger(__name__)


class DataParser:
    """HTML数据解析器"""
    
    def __init__(self):
        """初始化解析器"""
        logger.info("DataParser 初始化完成")
    
    def parse_search_results(self, html: str, query: str) -> List[Dict[str, str]]:
        """
        解析搜索结果页面，提取HS编码和商品信息
        
        Args:
            html: HTML内容
            query: 查询关键词
            
        Returns:
            搜索结果列表，每个元素包含 hs_code, product_name, detail_url
        """
        soup = BeautifulSoup(html, 'lxml')
        results = []
        
        try:
            # 方法1: 查找所有包含HS编码的链接（指向详情页的链接）
            # 排除包含#sbsl（申报实例）的链接
            detail_links = soup.find_all('a', href=re.compile(r'/hscode/detail/\d+'))
            
            for link in detail_links:
                href = link.get('href', '')
                
                # 跳过申报实例链接（包含#sbsl）
                if '#' in href:
                    continue
                    
                # 从URL中提取HS编码
                match = re.search(r'/hscode/detail/(\d+)', href)
                if match:
                    hs_code_raw = match.group(1)
                    # 格式化HS编码（添加点号）
                    if len(hs_code_raw) == 10:
                        hs_code = f"{hs_code_raw[:8]}.{hs_code_raw[8:]}"
                    elif len(hs_code_raw) == 8:
                        hs_code = f"{hs_code_raw[:4]}.{hs_code_raw[4:]}"
                    else:
                        hs_code = hs_code_raw
                    
                    # 获取商品名称
                    product_name = safe_get_text(link)
                    
                    logger.debug(f"提取到链接: href='{href}', 链接文本='{product_name}'")
                    
                    # 如果链接文本是"查看详情"等无意义文本，尝试从父元素获取商品名称
                    if product_name in ['查看详情', '详情', '']:
                        # 尝试从同一行的其他单元格获取商品名称
                        parent_row = link.find_parent('tr')
                        if parent_row:
                            cells = parent_row.find_all(['td', 'th'])
                            # 通常第二列是商品名称
                            if len(cells) >= 2:
                                product_name = safe_get_text(cells[1])
                                logger.debug(f"从表格第2列获取商品名: '{product_name}'")
                    
                    # 完整URL - 移除锚点和查询参数，只保留详情URL
                    clean_href = href.split('#')[0].split('?')[0]
                    # 判断是完整URL还是相对路径
                    if clean_href.startswith('http://') or clean_href.startswith('https://'):
                        detail_url = clean_href
                    elif clean_href.startswith('//'):
                        detail_url = f"https:{clean_href}"
                    elif clean_href.startswith('/'):
                        detail_url = f"https://www.i5a6.com{clean_href}"
                    else:
                        detail_url = f"https://www.i5a6.com/{clean_href}"
                    
                    results.append({
                        'hs_code': hs_code,
                        'product_name': clean_text(product_name),
                        'detail_url': detail_url
                    })
            
            # 方法2: 如果方法1没找到，尝试查找表格中的HS编码
            if not results:
                hs_code_pattern = re.compile(r'\d{8,10}')
                hs_elements = soup.find_all(text=hs_code_pattern)
                
                for hs_text in hs_elements:
                    parent = hs_text.parent
                    hs_match = hs_code_pattern.search(str(hs_text))
                    if not hs_match:
                        continue
                    
                    hs_code_raw = hs_match.group()
                    # 格式化HS编码
                    if len(hs_code_raw) == 10:
                        hs_code = f"{hs_code_raw[:8]}.{hs_code_raw[8:]}"
                    elif len(hs_code_raw) == 8:
                        hs_code = f"{hs_code_raw[:4]}.{hs_code_raw[4:]}"
                    else:
                        hs_code = hs_code_raw
                    
                    # 查找对应的商品名称
                    row = parent.find_parent('tr') if parent else None
                    product_name = ""
                    if row:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            product_name = safe_get_text(cells[1])
                    else:
                        product_name = safe_get_text(parent.find_next_sibling())
                    
                    # 构建详情URL（移除点号）
                    detail_url = f"https://www.i5a6.com/hscode/detail/{hs_code.replace('.', '')}"
                    
                    results.append({
                        'hs_code': hs_code,
                        'product_name': clean_text(product_name),
                        'detail_url': detail_url
                    })
            
            logger.info(f"从搜索结果中提取到 {len(results)} 条记录")
            
        except Exception as e:
            logger.error(f"解析搜索结果失败: {str(e)}")
        
        return results
    
    def parse_detail_page(self, html: str) -> Dict:
        """
        解析详情页面，提取完整的HS编码信息
        
        Args:
            html: HTML内容
            
        Returns:
            包含所有字段的字典
        """
        soup = BeautifulSoup(html, 'lxml')
        result = create_empty_result()
        
        try:
            # 查找包含数据的表格
            tables = soup.find_all('table')
            data_dict = {}
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = safe_get_text(cells[0])
                        value = safe_get_text(cells[1])
                        if key and value:
                            data_dict[key] = value
                        # 处理一行有4个单元格的情况（两对键值）
                        if len(cells) >= 4:
                            key2 = safe_get_text(cells[2])
                            value2 = safe_get_text(cells[3])
                            if key2 and value2:
                                data_dict[key2] = value2
            
            # 提取HS编码
            result['hs_code'] = data_dict.get('商品编码', '')
            
            # 提取商品名称
            result['product_name'] = data_dict.get('商品名称', '')
            
            # 提取申报要素
            result['declaration_elements'] = data_dict.get('申报要素', '')
            
            # 提取法定第一单位
            result['first_unit'] = data_dict.get('法定第一单位', '')
            
            # 提取法定第二单位
            result['second_unit'] = data_dict.get('法定第二单位', '')
            
            # 提取海关监管条件
            result['customs_supervision_conditions']['code'] = data_dict.get('海关监管条件', '')
            
            # 提取海关监管条件详情（许可证或批文）
            supervision_details = []
            permit_code_elem = soup.find(text=re.compile(r'许可证或批文代码'))
            permit_name_elem = soup.find(text=re.compile(r'许可证或批文名称'))
            
            if permit_code_elem and permit_name_elem:
                # 查找表格
                table = permit_code_elem.find_parent('table')
                if table:
                    rows = table.find_all('tr')[1:]  # 跳过标题行
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            code = safe_get_text(cells[0])
                            name = safe_get_text(cells[1])
                            if code and name:
                                supervision_details.append({
                                    'code': code,
                                    'name': name
                                })
            
            result['customs_supervision_conditions']['details'] = supervision_details
            
            # 提取检验检疫类别
            result['inspection_quarantine']['code'] = data_dict.get('检验检疫类别', '')
            
            # 提取商品描述
            result['description'] = data_dict.get('商品描述', '')
            
            # 提取检验检疫详情
            inspection_details = []
            insp_code_elem = soup.find(text=re.compile(r'检验检疫代码'))
            insp_name_elem = soup.find(text=re.compile(r'^名称$'))
            
            if insp_code_elem and insp_name_elem:
                # 查找表格
                table = insp_code_elem.find_parent('table')
                if table:
                    rows = table.find_all('tr')[1:]  # 跳过标题行
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            code = safe_get_text(cells[0])
                            name = safe_get_text(cells[1])
                            if code and name:
                                inspection_details.append({
                                    'code': code,
                                    'name': name
                                })
            
            result['inspection_quarantine']['details'] = inspection_details
            
            # 如果没有找到商品描述，尝试使用商品名称
            if not result['description'] and result['product_name']:
                result['description'] = result['product_name']
            
            # 判断是否成功解析（至少要有HS编码或商品名称）
            if result['hs_code'] or result['product_name']:
                result['search_success'] = True
            else:
                result['search_success'] = False
                result['error_message'] = "页面数据为空，可能HS编码不完整"
            logger.info(f"成功解析HS编码: {result['hs_code']} - {result['product_name']}")
            
        except Exception as e:
            logger.error(f"解析详情页面失败: {str(e)}")
            result['error_message'] = str(e)
        
        return result
    
    def extract_product_names_from_search(self, html: str) -> List[str]:
        """
        从搜索结果中提取所有商品名称，用于相似度匹配
        
        Args:
            html: HTML内容
            
        Returns:
            商品名称列表
        """
        results = self.parse_search_results(html, "")
        return [r['product_name'] for r in results if r['product_name']]
