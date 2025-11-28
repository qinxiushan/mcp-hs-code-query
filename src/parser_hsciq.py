"""
HS编码查询工具 - HSCIQ网站HTML解析模块
用于解析 hsciq.com 网站的搜索结果和详情页面

创建日期: 2025-11-25
网站: https://hsciq.com/HSCN/

最后更新: 2025-11-25
更新说明: 根据实际网站结构完善解析逻辑
- 搜索结果页URL: https://hsciq.com/HSCN/Search?keywords=苹果&viewtype=1&filterFailureCode=true
- 详情页URL: https://hsciq.com/HSCN/Code/0808100000
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class HTMLParserHSCIQ:
    """HSCIQ网站的HTML解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.base_url = "https://hsciq.com"
    
    def parse_search_results(self, html: str, query: str) -> List[Dict]:
        """
        解析搜索结果页面,提取商品列表
        
        根据实际页面分析,搜索结果以如下结构呈现:
        - 每个结果项包含: 申报实例、商品编码链接、出口退税率、监管条件、检验检疫、详情链接
        - HS编码在链接中: <link "0808100000" url="https://hsciq.com/HSCN/Code/0808100000">
        - 商品名称在纯文本中: "鲜苹果"
        
        Args:
            html: 搜索结果页面的HTML内容
            query: 搜索关键词
            
        Returns:
            商品列表,每个商品包含 name, url, hs_code 等信息
        """
        soup = BeautifulSoup(html, 'lxml')
        results = []
        
        try:
            # 查找所有包含HS编码链接的元素
            # 根据页面快照,HS编码链接格式为: /HSCN/Code/编码
            hs_code_links = soup.find_all('a', href=re.compile(r'/HSCN/Code/\d+'))
            
            logger.debug(f"找到 {len(hs_code_links)} 个HS编码链接")
            
            for link in hs_code_links:
                try:
                    # 提取HS编码
                    hs_code = link.get_text(strip=True)
                    detail_url = link.get('href', '')
                    
                    # 处理相对URL
                    if detail_url and not detail_url.startswith('http'):
                        detail_url = f"{self.base_url}{detail_url}"
                    
                    # 查找商品名称 - 通常在HS编码链接之后的文本节点或元素中
                    # 根据页面结构,商品名称紧跟在HS编码链接后面
                    parent = link.parent
                    if parent:
                        # 获取父元素的所有文本,去除HS编码部分
                        full_text = parent.get_text(strip=True)
                        
                        # 移除HS编码和[税目]等标记
                        product_name = full_text.replace(hs_code, '').replace('[税目]', '').strip()
                        
                        # 如果商品名称为空,尝试查找下一个兄弟元素
                        if not product_name:
                            next_elem = link.find_next_sibling(string=True)
                            if next_elem:
                                product_name = next_elem.strip()
                        
                        # 检查是否包含"已作废"等标记
                        is_obsolete = '已作废' in full_text or '过期' in full_text
                        
                        if not is_obsolete and hs_code and product_name:
                            results.append({
                                'name': product_name,
                                'url': detail_url,
                                'hs_code': hs_code,
                                'obsolete': False
                            })
                            logger.debug(f"解析到: {hs_code} - {product_name}")
                        elif is_obsolete:
                            logger.debug(f"跳过已作废商品: {product_name} ({hs_code})")
                            
                except Exception as e:
                    logger.warning(f"解析单个搜索结果失败: {e}")
                    continue
            
            logger.info(f"从HSCIQ搜索结果中提取到 {len(results)} 个有效商品")
            
        except Exception as e:
            logger.error(f"解析HSCIQ搜索结果失败: {e}")
        
        return results
    
    def parse_detail_page(self, html: str, url: str) -> Dict:
        """
        解析商品详情页面,提取完整的HS编码信息
        
        Args:
            html: 详情页HTML内容
            url: 详情页URL
            
        Returns:
            包含完整信息的字典
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 初始化结果字典
        result = {
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
            }
        }
        
        try:
            # 保存HTML用于调试
            # with open('debug_detail_page.html', 'w', encoding='utf-8') as f:
            #     f.write(html)
            
            # 1. 提取HS编码 - 通常在页面标题或h1标签中
            heading = soup.find('h1') or soup.find('h2')
            if heading:
                heading_text = heading.get_text(strip=True)
                # 提取10位数字编码
                hs_match = re.search(r'\d{10}', heading_text)
                if hs_match:
                    result['hs_code'] = self._format_hs_code(hs_match.group())
            
            # 如果标题中没有,尝试从URL提取
            if not result['hs_code']:
                url_match = re.search(r'/Code/(\d{10})', url)
                if url_match:
                    result['hs_code'] = self._format_hs_code(url_match.group(1))
            
            # 2. 构建数据字典 - 查找所有包含标签和值的结构
            data_dict = {}
            
            # 方法A: 查找所有表格行
            all_rows = soup.find_all('tr')
            for row in all_rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).replace(':', '').replace(':', '')
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        data_dict[key] = value
            
            # 方法B: 查找包含标签的div/span结构
            # 例如: <strong>商品名称:</strong> 鲜苹果
            labels = soup.find_all(['strong', 'label', 'dt'])
            for label in labels:
                label_text = label.get_text(strip=True).replace(':', '').replace(':', '')
                if label_text:
                    # 查找紧跟的值
                    value_elem = label.find_next_sibling()
                    if value_elem:
                        value = value_elem.get_text(strip=True)
                    else:
                        # 值可能在同一个父元素中
                        parent = label.parent
                        if parent:
                            value = parent.get_text(strip=True).replace(label_text, '').replace(':', '').strip()
                    
                    if value:
                        data_dict[label_text] = value
            
            # 3. 从数据字典提取各字段
            # 商品名称
            result['product_name'] = (
                data_dict.get('商品名称') or 
                data_dict.get('品名') or ''
            )
            
            # 商品描述
            result['description'] = (
                data_dict.get('商品描述') or 
                result['product_name']  # 如果没有单独的描述,使用商品名称
            )
            
            # 申报要素 - 在页面中是独立的表格
            # 查找"申报要素"标题后的表格
            decl_heading = None
            for h6 in soup.find_all('h6'):
                if '申报要素' in h6.get_text():
                    decl_heading = h6
                    break
            
            decl_elements = ''
            
            if decl_heading:
                # 找到标题后的table
                decl_table = decl_heading.find_next('table')
                if decl_table:
                    elements_list = []
                    rows = decl_table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            index = cells[0].get_text(strip=True)
                            # 第二列包含要素名称,需要清理"必填""非必填"等标记
                            element_text = cells[1].get_text(strip=True)
                            # 移除 [?] 链接和 必填/非必填 标记
                            element_text = re.sub(r'\[\?\]', '', element_text)
                            element_text = re.sub(r'(必填|非必填)$', '', element_text).strip()
                            
                            if index.isdigit() and element_text:
                                elements_list.append(f"{index}:{element_text}")
                    
                    if elements_list:
                        decl_elements = ';'.join(elements_list)
            
            result['declaration_elements'] = decl_elements
            
            # 法定单位
            result['first_unit'] = (
                data_dict.get('第一法定单位') or 
                data_dict.get('法定第一单位') or 
                data_dict.get('第一单位') or ''
            )
            
            result['second_unit'] = (
                data_dict.get('第二法定单位') or 
                data_dict.get('法定第二单位') or 
                data_dict.get('第二单位') or '无'
            )
            
            # 监管条件 - 在h6后面的表格中
            # 结构: <h6>监管条件</h6> <p></p> <table><tr><td>A</td><td>入境货物通关单</td></tr>...
            
            # 查找监管条件h6 - 使用text搜索而不是string,因为可能包含子元素
            supervision_h6 = None
            for h6 in soup.find_all('h6'):
                if '监管条件' in h6.get_text():
                    supervision_h6 = h6
                    break
            
            if supervision_h6:
                # 查找h6父元素下的table
                parent = supervision_h6.find_parent()
                if parent:
                    supervision_table = parent.find('table')
                    if supervision_table:
                        codes = []
                        details = []
                        
                        # 遍历表格行
                        for row in supervision_table.find_all('tr'):
                            tds = row.find_all('td')
                            if len(tds) >= 2:
                                code = tds[0].get_text(strip=True)
                                name = tds[1].get_text(strip=True)
                                if code and name:
                                    codes.append(code)
                                    details.append({'code': code, 'name': name})
                                    logger.debug(f"  监管条件: {code} - {name}")
                        
                        if codes:
                            result['customs_supervision_conditions']['code'] = ''.join(codes)
                            result['customs_supervision_conditions']['details'] = details
                            logger.info(f"成功提取监管条件: {result['customs_supervision_conditions']['code']}")
            
            # 查找检验检疫h6
            quarantine_h6 = None
            for h6 in soup.find_all('h6'):
                if '检验检疫' in h6.get_text():
                    quarantine_h6 = h6
                    break
            
            if quarantine_h6:
                parent = quarantine_h6.find_parent()
                if parent:
                    quarantine_table = parent.find('table')
                    if quarantine_table:
                        codes = []
                        details = []
                        
                        for row in quarantine_table.find_all('tr'):
                            tds = row.find_all('td')
                            if len(tds) >= 2:
                                code = tds[0].get_text(strip=True)
                                name = tds[1].get_text(strip=True)
                                if code and name:
                                    codes.append(code)
                                    details.append({'code': code, 'name': name})
                                    logger.debug(f"  检验检疫: {code} - {name}")
                        
                        if codes:
                            result['inspection_quarantine']['code'] = ''.join(codes)
                            result['inspection_quarantine']['details'] = details
                            logger.info(f"成功提取检验检疫: {result['inspection_quarantine']['code']}")
            
            # 验证是否解析成功
            if not result['hs_code'] and not result['product_name']:
                logger.warning(f"HSCIQ详情页解析失败,HS编码和商品名称都为空: {url}")
                return result
            
            logger.info(f"成功解析HSCIQ详情页: {result['hs_code']} - {result['product_name']}")
            
        except Exception as e:
            logger.error(f"解析HSCIQ详情页失败: {e}, URL: {url}")
        
        return result
    
    def _format_hs_code(self, hs_code: str) -> str:
        """
        格式化HS编码,为10位编码添加点号
        
        Args:
            hs_code: 原始HS编码字符串
            
        Returns:
            格式化后的HS编码
        """
        # 移除所有非数字字符
        clean_code = re.sub(r'[^\d]', '', hs_code)
        
        # 10位编码: XXXXXXXX.XX
        if len(clean_code) == 10:
            return f"{clean_code[:8]}.{clean_code[8:]}"
        # 8位编码: XXXX.XXXX
        elif len(clean_code) == 8:
            return f"{clean_code[:4]}.{clean_code[4:]}"
        else:
            return hs_code  # 保持原样
    
    def extract_supervision_details(self, code: str) -> List[Dict]:
        """
        解析监管条件代码,返回详细说明列表
        
        Args:
            code: 监管条件代码字符串,如 "AB"
            
        Returns:
            详细说明列表,每个元素包含 code 和 name
        """
        # 监管条件代码映射表
        supervision_map = {
            'A': '入境货物通关单',
            'B': '出境货物通关单',
            'C': '入境/出境货物通关单',
            '4': '出口许可证',
            '7': '自动进口许可证',
            '9': '入境货物通关单',
            'O': '自动进口许可证（机电产品）',
            # 可以继续添加更多代码
        }
        
        details = []
        for char in code:
            if char in supervision_map:
                details.append({
                    'code': char,
                    'name': supervision_map[char]
                })
        
        return details
    
    def extract_quarantine_details(self, code: str) -> List[Dict]:
        """
        解析检验检疫类别代码,返回详细说明列表
        
        Args:
            code: 检验检疫代码字符串,如 "PQ"
            
        Returns:
            详细说明列表,每个元素包含 code 和 name
        """
        # 检验检疫代码映射表
        quarantine_map = {
            'P': '进境动植物、动植物产品检疫',
            'Q': '出境动植物、动植物产品检疫',
            'R': '进口食品卫生监督检验',
            'S': '出口食品卫生监督检验',
            'M': '进口商品检验',
            'N': '出口商品检验',
            # 可以继续添加更多代码
        }
        
        details = []
        for char in code:
            if char in quarantine_map:
                details.append({
                    'code': char,
                    'name': quarantine_map[char]
                })
        
        return details
