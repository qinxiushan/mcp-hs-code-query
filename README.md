# HS编码查询工具

基于Python的智能HS编码查询工具，支持从指定网站自动抓取商品的HS编码及相关海关申报信息。

## 功能特性

- ✅ **单个查询**: 支持单个商品名称查询
- ✅ **批量查询**: 支持批量商品查询
- ✅ **智能搜索**: 自动中文分词，多关键词尝试
- ✅ **相似度匹配**: 自动选择最相近的搜索结果
- ✅ **重试机制**: 网络请求失败自动重试
- ✅ **完整数据**: 提取HS编码、申报要素、监管条件等完整信息
- ✅ **JSON导出**: 结果以JSON格式保存

## 提取的数据字段

- HS商品编码
- 商品名称
- 申报要素
- 法定第一单位
- 法定第二单位
- 海关监管条件（包含许可证或批文代码和名称）
- 检验检疫类别（包含检验检疫代码和名称）
- 商品描述

## 项目结构

```
data_search/
├── config/
│   └── settings.py          # 配置文件
├── src/
│   ├── scraper.py          # 爬虫主逻辑
│   ├── parser.py           # 数据解析
│   ├── search_optimizer.py # 分词和搜索优化
│   ├── storage.py          # 数据存储
│   └── utils.py            # 工具函数
├── data/
│   ├── input/              # 输入数据
│   └── output/             # 输出数据（JSON）
├── docs/                   # 📚 项目文档和修改记录
│   ├── README.md          # 文档索引
│   ├── CHANGELOG.md       # 总更新日志
│   ├── TEMPLATE.md        # 文档模板
│   └── CHANGELOG_XXX_*.md # 具体修改记录
├── logs/                   # 日志文件
├── requirements.txt        # 依赖包
├── main.py                # 主入口
└── README.md              # 说明文档
```

## 安装

### 1. 克隆或下载项目

```bash
cd data_search
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用

#### 1. 单个商品查询

```bash
python main.py -s "苹果手机"
```

#### 2. 批量查询（命令行输入）

```bash
python main.py -b "苹果" "香蕉" "橙子"
```

#### 3. 从文件批量查询

首先创建输入文件 `data/input/products.txt`，每行一个商品名称：

```
苹果手机
笔记本电脑
棉质T恤
不锈钢水杯
```

然后执行：

```bash
python main.py -f data/input/products.txt
```

#### 4. 查询但不保存结果

```bash
python main.py -s "电脑" --no-save
```

### Python API使用

```python
from src.scraper import HSCodeScraper
from src.storage import DataStorage

# 创建实例
scraper = HSCodeScraper()
storage = DataStorage()

# 单个查询
result = scraper.query_by_product_name("苹果手机")
print(storage.format_result_for_display(result))

# 保存结果
storage.save_single_result(result)

# 批量查询
products = ["苹果", "香蕉", "橙子"]
results = scraper.batch_query(products)
storage.save_batch_results(results)

# 关闭会话
scraper.close()
```

### 根据HS编码查询

```python
from src.scraper import HSCodeScraper

scraper = HSCodeScraper()
result = scraper.query_by_hs_code("84193990.20")
print(result)
scraper.close()
```

## 配置说明

在 `config/settings.py` 中可以修改以下配置：

```python
# 网站配置
BASE_URL = "https://www.i5a6.com"  # 可替换为其他HS编码查询网站

# 请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3       # 最大重试次数
REQUEST_DELAY = 1     # 请求间隔（秒）

# 搜索配置
MAX_SEARCH_ATTEMPTS = 5      # 分词后最大搜索尝试次数
MIN_SIMILARITY_SCORE = 0.6   # 最小相似度分数（0-1）
```

## 输出格式

### JSON输出示例

```json
{
  "query_time": "2025-11-24 10:30:00",
  "data": {
    "hs_code": "84193990.20",
    "product_name": "其他烟丝烘干机",
    "declaration_elements": "1:品名;2:品牌类型;3:出口享惠情况;4:用途;5:干燥材质;6:品牌;7:型号;8:GTIN;9:CAS;10:其他;",
    "first_unit": "台",
    "second_unit": "千克",
    "customs_supervision_conditions": {
      "code": "O",
      "details": [
        {
          "code": "O",
          "name": "自动进口许可证（机电产品）"
        }
      ]
    },
    "inspection_quarantine": {
      "code": "无",
      "details": []
    },
    "description": "其他烟丝烘干机",
    "search_success": true,
    "error_message": ""
  }
}
```

## 工作原理

1. **输入处理**: 接收商品名称
2. **智能分词**: 使用jieba对商品名称进行中文分词
3. **关键词生成**: 生成多个搜索关键词组合
4. **搜索尝试**: 依次尝试每个关键词进行搜索
5. **相似度匹配**: 使用SequenceMatcher选择最相近的结果
6. **数据提取**: 从详情页提取所有必需字段
7. **结果保存**: 将结果保存为JSON格式

## 注意事项

1. **合法使用**: 请遵守网站的robots.txt和使用条款
2. **访问频率**: 已内置请求延迟，避免对服务器造成压力
3. **网络环境**: 需要稳定的网络连接
4. **数据准确性**: 建议人工核查重要的查询结果
5. **网站变化**: 如果目标网站结构变化，需要更新解析逻辑

## 日志

运行日志保存在 `logs/hs_code_scraper.log`，包含：
- 查询过程
- 错误信息
- 成功/失败统计

## 故障排除

### 问题1: 找不到搜索结果

**解决方案**:
- 检查商品名称是否正确
- 尝试使用更通用的关键词
- 在 `config/settings.py` 中增加 `MAX_SEARCH_ATTEMPTS`

### 问题2: 网络请求超时

**解决方案**:
- 检查网络连接
- 增加 `REQUEST_TIMEOUT` 值
- 增加 `MAX_RETRIES` 值

### 问题3: 解析失败

**解决方案**:
- 检查目标网站是否可访问
- 网站结构可能已更改，需要更新 `parser.py`

## 更新网站

如需更换目标网站，修改 `config/settings.py`：

```python
BASE_URL = "https://新网站地址"
```

然后根据新网站的HTML结构更新 `src/parser.py` 中的解析逻辑。

## 许可证

本项目仅供学习和研究使用。

## 文档

- [完整更新日志](docs/CHANGELOG.md) - 查看所有版本的修改记录
- [文档索引](docs/README.md) - 查看所有技术文档
- [快速开始](QUICK_START.md) - 快速上手指南
- [项目总结](PROJECT_SUMMARY.md) - 技术实现总结

## 联系方式

如有问题或建议，请提交Issue。
