# CHANGELOG #004 - 添加 HSCIQ 网站支持

**修改日期**: 2025-11-26  
**修改类型**: ✨ 新功能  
**影响范围**: 新增模块  
**修改人**: 开发团队

---

## 📋 修改概述

为 HS 编码查询工具添加了对 HSCIQ (https://hsciq.com/HSCN) 网站的支持,实现了完整的爬虫和解析功能。

---

## 🎯 修改目标

1. 支持新的 HS 编码查询网站 (HSCIQ)
2. 实现智能过滤过期编码功能
3. 提取完整的海关申报信息
4. 保持与现有系统的兼容性

---

## 🔍 网站分析

### 目标网站
- **网站名称**: 中国海关编码查询 (HSCIQ)
- **网站地址**: https://hsciq.com/HSCN
- **搜索 URL**: `https://hsciq.com/HSCN/Search?keywords={query}&viewtype=1&filterFailureCode=true`
- **详情 URL**: `https://hsciq.com/HSCN/Code/{10位HS编码}`

### 页面结构分析 (使用 Chrome DevTools MCP)

#### 搜索页面
- **搜索框**: `<input type="text" placeholder="请输入商品名称或商品编码">`
- **搜索类型**: 下拉框 (商品编码/税目税则/CIQ编码)
- **过滤选项**: `filterFailureCode=true` URL参数(不是复选框点击)
- **结果格式**: HS编码链接 + 商品名称文本
- **过滤效果**: 从 1030 条结果减少到 932 条

#### 详情页面 (以 0808100000 鲜苹果为例)

**基本信息表格**:
```html
<h6>基本信息</h6>
<table>
  <tr><td>商品编码</td><td>0808100000</td></tr>
  <tr><td>商品名称</td><td>鲜苹果</td></tr>
  <tr><td>商品描述</td><td>鲜苹果</td></tr>
  <tr><td>第一法定单位</td><td>千克</td></tr>
  <tr><td>第二法定单位</td><td>无</td></tr>
</table>
```

**申报要素表格**:
```html
<h6>申报要素</h6>
<table>
  <tr><td>0</td><td>品牌类型</td></tr>
  <tr><td>1</td><td>出口享惠情况</td></tr>
  ...
</table>
```

**监管条件**:
```html
<h6>监管条件</h6>
<table>
  <tr><td>A</td><td>入境货物通关单</td></tr>
  <tr><td>B</td><td>出境货物通关单</td></tr>
</table>
```

**检验检疫**:
```html
<h6>检验检疫类别</h6>
<table>
  <tr><td>R</td><td>进口食品卫生监督检验</td></tr>
  <tr><td>S</td><td>出口食品卫生监督检验</td></tr>
  <tr><td>P</td><td>进境动植物、动植物产品检疫</td></tr>
  <tr><td>Q</td><td>出境动植物、动植物产品检疫</td></tr>
</table>
```

---

## 📝 修改详情

### 1. 新增文件

#### `src/scraper_hsciq.py` (326 行)
HSCIQ 网站爬虫模块

**主要类**: `HSCodeScraperHSCIQ`

**核心方法**:
```python
def search_products(keyword: str, filter_obsolete: bool = True) -> List[Dict]
    # 搜索商品,自动过滤过期编码
    # URL: /HSCN/Search?keywords={keyword}&viewtype=1&filterFailureCode=true
    
def get_product_detail(url: str) -> Dict
    # 获取商品详情
    
def query_by_product_name(product_name: str) -> Dict
    # 根据商品名称查询(含分词和相似度匹配)
    
def query_by_hs_code(hs_code: str) -> Dict
    # 根据 HS 编码直接查询
    
def batch_query(product_names: List[str]) -> List[Dict]
    # 批量查询
```

**关键特性**:
- ✅ 正确的 URL 构建: `/HSCN/Search` 而不是 `/HSCN/`
- ✅ 正确的参数: `keywords`, `viewtype=1`, `filterFailureCode=true`
- ✅ 使用 `retry_on_exception` 装饰器实现重试机制
- ✅ 集成 `SearchOptimizer` 进行中文分词
- ✅ 手动计算相似度(避免类型不匹配)

#### `src/parser_hsciq.py` (300 行)
HSCIQ 网站 HTML 解析模块

**主要类**: `HTMLParserHSCIQ`

**核心方法**:
```python
def parse_search_results(html: str, query: str) -> List[Dict]
    # 解析搜索结果,提取 HS 编码链接和商品名称
    # 过滤已作废商品
    
def parse_detail_page(html: str, url: str) -> Dict
    # 解析详情页,提取所有字段
    # 支持多种查找策略(表格/标签)
    
def extract_supervision_details(code: str) -> List[Dict]
    # 解析监管条件代码
    
def extract_quarantine_details(code: str) -> List[Dict]
    # 解析检验检疫代码
```

**解析策略**:

1. **HS 编码提取**:
   - 优先从 `<h1>` 或 `<h2>` 中提取 10 位数字
   - 回退到从 URL 中提取: `/Code/(\d{10})`

2. **基本信息提取** (双层策略):
   - 方法 A: 遍历所有 `<tr>` 行,构建键值对字典
   - 方法 B: 查找 `<strong>/<label>/<dt>` 标签及其值

3. **申报要素提取**:
   - 查找包含"申报要素"的 `<h6>` 标签
   - 提取其后的表格中的所有行
   - 格式化为 `序号:内容` 形式

4. **监管条件和检验检疫提取**:
   - 查找包含"监管条件"或"检验检疫"的 `<h6>` 标签
   - 遍历其父元素下的表格行
   - 提取代码和详细说明
   - 使用映射表补充说明

#### `test_hsciq.py` (141 行)
测试脚本

**测试用例**:
1. `test_single_query()` - 单个商品查询 ("苹果")
2. `test_query_by_hs_code()` - 按 HS 编码查询 ("0808100000")
3. `test_batch_query()` - 批量查询 (["苹果", "香蕉", "橙子"])

---

## 🐛 修复的问题

### 问题 1: 导入错误
**错误**: `ImportError: cannot import name 'retry_on_failure' from 'src.utils'`

**原因**: `utils.py` 中的装饰器名称是 `retry_on_exception`,不是 `retry_on_failure`

**修复**:
```python
# 修改前
from src.utils import retry_on_failure
@retry_on_failure(max_retries=MAX_RETRIES)

# 修改后
from src.utils import retry_on_exception
@retry_on_exception(max_retries=MAX_RETRIES)
```

### 问题 2: 相似度计算类型错误
**错误**: `AttributeError: 'dict' object has no attribute 'strip'`

**原因**: `find_best_match()` 期望字符串列表,但收到的是字典列表

**修复**: 在 `scraper_hsciq.py` 中手动提取商品名称并计算相似度
```python
# 修改前
best_match = self.optimizer.find_best_match(product_name, results)

# 修改后
best_match = None
best_score = 0.0

for result in results:
    candidate_name = result.get('name', '')
    score = self.optimizer.calculate_similarity(product_name, candidate_name)
    
    if score > best_score:
        best_score = score
        best_match = result
        best_match['similarity'] = score
```

### 问题 3: 监管条件和检验检疫未提取
**错误**: 这两个字段始终为空

**根本原因**: 
1. `<h6>` 标签文本包含大量空白和换行,正则匹配失败
2. 表格不是 `<h6>` 的直接兄弟元素,而是在父元素下

**调试过程**:
1. 使用 Chrome DevTools MCP 检查实际 HTML 结构
2. 添加调试日志保存 HTML 到文件
3. 发现 `<h6>` 文本为 `"\n\n              监管条件\n              "`

**最终修复**:
```python
# 查找 h6 标签时去除所有空白
h6_elements = soup.find_all('h6')
for h6 in h6_elements:
    h6_text = h6.get_text(strip=True)  # 关键: strip=True
    
    if '监管条件' in h6_text:
        # 在 h6 的父元素下查找表格
        parent = h6.find_parent()
        if parent:
            table = parent.find('table')
            if table:
                # 提取数据
```

---

## 🧪 测试结果

### 测试环境
- Python 虚拟环境: `search`
- 测试日期: 2025-11-26
- 测试网站: https://hsciq.com/HSCN

### 测试输出

#### 单个商品查询 (苹果)
```
查询结果:
============================================================
HS编码: 08081000.00
商品名称: 鲜苹果
商品描述: 鲜苹果
申报要素: 0:品牌类型;1:出口享惠情况;2:制作或保存方法(鲜);3:种类(蛇果、加纳果、青苹果、富士等);4:等级;5:品牌(中文或外文名称);6:GTIN;7:CAS;8:其他
法定第一单位: 千克
法定第二单位: 无
海关监管条件: AB
  许可证或批文:
    - A: 入境货物通关单
    - B: 出境货物通关单
检验检疫类别: RSPQ
  检验检疫代码:
    - R: 进口食品卫生监督检验
    - S: 出口食品卫生监督检验
    - P: 进境动植物、动植物产品检疫
    - Q: 出境动植物、动植物产品检疫
查询状态: 成功
============================================================
```

✅ **所有字段提取成功**

---

## 📊 代码统计

### 新增代码
- `scraper_hsciq.py`: 326 行
- `parser_hsciq.py`: 300 行
- `test_hsciq.py`: 141 行
- **总计**: 767 行

### 修改的现有文件
无 (完全新增模块,未修改原有代码)

---

## 🔧 技术要点

### 1. Chrome DevTools MCP 的使用
使用 MCP (Model Context Protocol) Chrome DevTools 工具进行网站结构分析:

```python
# 工具调用示例
mcp_chrome-devtoo_navigate_page(url="https://hsciq.com/HSCN")
mcp_chrome-devtoo_fill(uid="6_23", value="苹果")
mcp_chrome-devtoo_click(uid="6_28")  # 点击搜索
mcp_chrome-devtoo_take_snapshot()    # 获取页面快照
```

**优势**:
- 精确识别页面元素位置
- 测试用户交互流程
- 获取真实的 HTML 结构

### 2. 双层过滤机制
```python
# Layer 1: 搜索结果页过滤
search_params = {
    'keywords': keyword,
    'viewtype': '1',
    'filterFailureCode': 'true'  # URL 参数过滤
}

# Layer 2: 详情页验证
if '已作废' not in detail.get('product_name', ''):
    return detail
else:
    continue  # 尝试下一个候选
```

### 3. 健壮的 HTML 解析
```python
# 策略 1: 表格行遍历
for row in all_rows:
    cells = row.find_all(['th', 'td'])
    if len(cells) >= 2:
        data_dict[cells[0].text.strip()] = cells[1].text.strip()

# 策略 2: 标签查找
labels = soup.find_all(['strong', 'label', 'dt'])
for label in labels:
    value = label.find_next_sibling() or label.parent

# 策略 3: 正则表达式提取
hs_match = re.search(r'\d{10}', heading_text)
```

---

## 🎓 经验教训

### 1. HTML 文本提取的陷阱
**教训**: 不要假设 `get_text()` 返回的是干净的字符串

```python
# ❌ 错误做法
if h6.get_text() == "监管条件":  # 永远不会匹配

# ✅ 正确做法
if "监管条件" in h6.get_text(strip=True):  # 去除空白后包含匹配
```

### 2. 调试技巧
**教训**: 当解析失败时,保存 HTML 到文件进行检查

```python
# 添加调试代码
debug_file = "data/output/debug_detail_page.html"
with open(debug_file, 'w', encoding='utf-8') as f:
    f.write(html)
logger.debug(f"HTML已保存到 {debug_file}")
```

### 3. 相似度匹配的灵活性
**教训**: 不同网站可能需要不同的相似度策略

```python
# 原始网站: 使用 find_best_match()
best_match = optimizer.find_best_match(query, candidates)

# HSCIQ: 手动计算(因为数据结构不同)
for result in results:
    score = optimizer.calculate_similarity(query, result['name'])
```

---

## 🚀 后续优化建议

### 优先级 P1
- [ ] 统一相似度匹配接口(支持字典列表)
- [ ] 添加缓存机制(Redis/本地)
- [ ] 异步请求支持

### 优先级 P2
- [ ] 支持更多 HSCIQ 页面字段(税率、章节信息)
- [ ] 错误重试策略优化
- [ ] 添加单元测试

### 优先级 P3
- [ ] 多网站结果对比和验证
- [ ] 自动检测网站结构变化
- [ ] 导出为 Excel 格式

---

## 📚 相关文档

- [项目 README](../README.md)
- [API 文档](../API_README.md)
- [快速开始](../QUICK_START.md)
- [总更新日志](./CHANGELOG.md)

---

## ✅ 验收标准

- [x] 支持 HSCIQ 网站搜索
- [x] 正确提取 HS 编码
- [x] 提取申报要素
- [x] 提取监管条件(代码+详情)
- [x] 提取检验检疫(代码+详情)
- [x] 过滤过期编码
- [x] 支持批量查询
- [x] 测试通过

---

**文档版本**: 1.0  
**创建日期**: 2025-11-26  
**最后更新**: 2025-11-26
