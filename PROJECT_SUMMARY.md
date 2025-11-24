# HS编码查询工具 - 项目实现总结

## 项目概述

本项目实现了一个完整的HS编码智能查询系统，能够从指定网站（https://www.i5a6.com/）自动抓取商品的HS编码及相关海关申报信息。

## 核心功能实现

### 1. 智能搜索系统
- **中文分词**: 使用jieba对商品名称进行智能分词
- **多策略搜索**: 生成多个关键词组合，从长到短依次尝试
- **相似度匹配**: 使用SequenceMatcher算法选择最相近的搜索结果
- **重试机制**: 超过重试次数后返回空值

### 2. 数据提取
成功提取以下所有必需字段：
- ✅ HS商品编码
- ✅ 商品名称  
- ✅ 申报要素
- ✅ 法定第一单位
- ✅ 法定第二单位
- ✅ 海关监管条件（代码 + 许可证详情）
- ✅ 检验检疫类别（代码 + 检验检疫详情）
- ✅ 商品描述

### 3. 查询模式
- ✅ 单个查询
- ✅ 批量查询
- ✅ 从文件批量查询
- ✅ 根据HS编码直接查询

### 4. 数据输出
- ✅ JSON格式保存
- ✅ 控制台格式化显示
- ✅ 包含查询时间和统计信息
- ✅ 区分成功/失败状态

## 技术架构

### 模块设计

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│              (命令行入口 & API接口)                   │
└─────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  scraper.py  │  │  parser.py   │  │  storage.py  │
│  (爬虫逻辑)   │  │  (数据解析)   │  │  (数据存储)   │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                ┌──────────────────┐
                │ search_optimizer │
                │    (智能搜索)     │
                └──────────────────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
        ┌──────────┐        ┌──────────┐
        │ utils.py │        │ settings │
        │ (工具类)  │        │  (配置)   │
        └──────────┘        └──────────┘
```

### 核心类说明

1. **HSCodeScraper** (scraper.py)
   - 负责网络请求和查询协调
   - 实现重试机制
   - 管理Session会话

2. **DataParser** (parser.py)
   - HTML解析
   - 字段提取
   - 数据清洗

3. **SearchOptimizer** (search_optimizer.py)
   - 中文分词
   - 关键词生成
   - 相似度计算

4. **DataStorage** (storage.py)
   - JSON序列化
   - 文件保存
   - 结果格式化

## 技术栈

- **Python 3.x**: 主要开发语言
- **requests**: HTTP请求
- **BeautifulSoup4 + lxml**: HTML解析
- **jieba**: 中文分词
- **difflib.SequenceMatcher**: 字符串相似度计算
- **logging**: 日志系统
- **json**: 数据序列化

## 关键特性

### 1. 智能搜索算法

```python
# 搜索策略示例
输入: "苹果手机"
生成关键词:
1. "苹果手机" (原始)
2. "苹果 手机" (分词后)
3. "苹果手机" (组合)
4. "苹果" (单词)
5. "手机" (单词)
```

### 2. 重试机制

```python
@retry_on_exception(max_retries=3, delay=2)
def _make_request(url):
    # 自动重试，失败后等待2秒
    pass
```

### 3. 数据结构

```python
{
    "hs_code": "84193990.20",
    "product_name": "其他烟丝烘干机",
    "declaration_elements": "1:品名;2:品牌类型;...",
    "first_unit": "台",
    "second_unit": "千克",
    "customs_supervision_conditions": {
        "code": "O",
        "details": [
            {"code": "O", "name": "自动进口许可证（机电产品）"}
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
```

## 项目文件清单

```
data_search/
├── config/
│   ├── __init__.py
│   └── settings.py          # 全局配置
├── src/
│   ├── __init__.py
│   ├── scraper.py           # 爬虫主逻辑 (220行)
│   ├── parser.py            # 数据解析 (200行)
│   ├── search_optimizer.py  # 搜索优化 (180行)
│   ├── storage.py           # 数据存储 (180行)
│   └── utils.py             # 工具函数 (140行)
├── data/
│   ├── input/
│   │   └── products.txt     # 示例输入
│   └── output/              # JSON输出目录
├── logs/
│   └── hs_code_scraper.log  # 运行日志
├── main.py                  # 主程序入口 (140行)
├── test_example.py          # 测试示例 (100行)
├── requirements.txt         # 依赖列表
├── README.md               # 详细文档
└── QUICK_START.md          # 快速开始指南
```

**总代码量**: 约1200行

## 使用示例

### 命令行使用
```bash
# 单个查询
python main.py -s "烘干机"

# 批量查询
python main.py -b "苹果" "香蕉" "橙子"

# 从文件查询
python main.py -f data/input/products.txt
```

### Python API使用
```python
from src.scraper import HSCodeScraper
from src.storage import DataStorage

scraper = HSCodeScraper()
storage = DataStorage()

result = scraper.query_by_product_name("烘干机")
storage.save_single_result(result)

scraper.close()
```

## 测试与验证

项目包含以下测试方式：

1. **test_example.py**: 交互式测试脚本
2. **命令行参数**: 灵活的CLI接口
3. **日志系统**: 详细的运行日志

## 扩展性

### 更换目标网站

1. 修改 `config/settings.py` 中的URL
2. 更新 `src/parser.py` 中的解析逻辑
3. 测试并调试

### 添加新字段

1. 在 `utils.create_empty_result()` 中添加字段
2. 在 `parser.parse_detail_page()` 中提取字段
3. 在 `storage.format_result_for_display()` 中显示字段

## 性能优化

- ✅ 请求延迟控制（避免被封IP）
- ✅ Session复用（减少连接开销）
- ✅ 异常捕获（保证稳定性）
- ✅ 日志系统（便于调试）

## 注意事项

1. **合法合规**: 遵守robots.txt和网站使用条款
2. **访问频率**: 内置1秒延迟，可调整
3. **错误处理**: 完善的异常处理机制
4. **数据验证**: 建议人工核查重要结果

## 后续改进方向

1. 添加代理池支持
2. 实现验证码识别
3. 支持更多输出格式（Excel、CSV）
4. 添加数据库存储
5. 开发Web界面
6. 支持多网站聚合查询

## 总结

本项目完整实现了HS编码智能查询系统的所有需求：
- ✅ 智能搜索与分词
- ✅ 完整数据提取
- ✅ 单个/批量查询
- ✅ JSON格式输出
- ✅ 重试机制
- ✅ 日志系统
- ✅ 完善文档

代码结构清晰，模块化设计，易于维护和扩展。
