#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试HTML结构"""

import requests
from bs4 import BeautifulSoup

url = "https://www.i5a6.com/hscode/key/%E8%8B%B9%E6%9E%9C"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# 找到第一个表格
table = soup.find('table')
if table:
    print("找到表格！")
    print("\n" + "="*60)
    
    # 打印前3行
    rows = table.find_all('tr')[:4]
    for i, row in enumerate(rows):
        print(f"\n第{i+1}行:")
        cells = row.find_all(['td', 'th'])
        for j, cell in enumerate(cells):
            text = cell.get_text(strip=True)
            # 查找链接
            link = cell.find('a', href=True)
            if link:
                print(f"  单元格{j+1}: '{text}' [链接: {link.get('href')}]")
            else:
                print(f"  单元格{j+1}: '{text}'")
