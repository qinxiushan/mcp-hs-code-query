# HS编码查询工具 - 安装和使用指南

## 📋 项目已完成

✅ 所有代码已编写完成
✅ 项目结构已创建
✅ 配置文件已设置
✅ 文档已完善

## 🚀 立即开始使用

### 第一步：安装依赖

在命令提示符中执行：

```cmd
cd c:\Users\dela1\Desktop\data_search
pip install -r requirements.txt
```

### 第二步：测试运行

#### 方式1：使用测试脚本（推荐新手）

```cmd
python test_example.py
```

然后按照提示选择测试类型（1-4）

#### 方式2：命令行查询（推荐日常使用）

```cmd
# 查询单个商品
python main.py -s "烘干机"

# 批量查询
python main.py -b "苹果" "香蕉" "橙子"

# 从文件批量查询
python main.py -f data/input/products.txt
```

### 第三步：查看结果

查询结果保存在 `data/output/` 目录下的JSON文件中。

## 📁 项目结构

```
data_search/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py        # 全局配置（可修改）
├── src/                   # 源代码模块
│   ├── __init__.py
│   ├── scraper.py        # 爬虫主逻辑
│   ├── parser.py         # HTML解析
│   ├── search_optimizer.py # 智能搜索
│   ├── storage.py        # 数据存储
│   └── utils.py          # 工具函数
├── data/
│   ├── input/            # 输入文件目录
│   │   └── products.txt  # 示例输入文件
│   └── output/           # 输出JSON目录
├── logs/                 # 日志目录
│   └── hs_code_scraper.log
├── main.py              # 主程序入口
├── test_example.py      # 测试示例
├── requirements.txt     # Python依赖
├── README.md           # 详细说明文档
├── QUICK_START.md      # 快速开始指南
└── PROJECT_SUMMARY.md  # 项目实现总结
```

## 🎯 核心功能

1. **智能搜索**
   - 自动中文分词
   - 多关键词尝试
   - 相似度匹配

2. **完整数据提取**
   - HS编码
   - 商品名称
   - 申报要素
   - 法定单位
   - 监管条件（含详情）
   - 检验检疫（含详情）
   - 商品描述

3. **灵活查询**
   - 单个查询
   - 批量查询
   - 文件批量查询
   - HS编码直接查询

4. **可靠性保障**
   - 自动重试机制
   - 详细日志记录
   - 异常处理
   - 空值处理

## 🔧 配置说明

编辑 `config/settings.py` 可修改以下配置：

```python
# 目标网站（可替换）
BASE_URL = "https://www.i5a6.com"

# 重试次数
MAX_RETRIES = 3

# 搜索尝试次数
MAX_SEARCH_ATTEMPTS = 5

# 相似度阈值（0-1）
MIN_SIMILARITY_SCORE = 0.6

# 请求延迟（秒）
REQUEST_DELAY = 1
```

## 📖 使用示例

### 命令行使用

```cmd
# 单个查询
python main.py -s "苹果手机"

# 批量查询
python main.py -b "苹果" "香蕉" "橙子" "手机"

# 从文件查询（推荐大批量）
python main.py -f data/input/products.txt

# 查询但不保存
python main.py -s "电脑" --no-save
```

### Python代码调用

```python
from src.scraper import HSCodeScraper
from src.storage import DataStorage

# 初始化
scraper = HSCodeScraper()
storage = DataStorage()

# 单个查询
result = scraper.query_by_product_name("烘干机")
print(storage.format_result_for_display(result))
storage.save_single_result(result)

# 批量查询
products = ["苹果", "香蕉", "橙子"]
results = scraper.batch_query(products)
storage.save_batch_results(results)

# 关闭会话
scraper.close()
```

### 批量查询准备

创建文件 `data/input/my_products.txt`：
```
苹果手机
笔记本电脑
棉质T恤
不锈钢水杯
烘干机
```

然后执行：
```cmd
python main.py -f data/input/my_products.txt
```

## 📊 输出格式

### 控制台输出
```
============================================================
HS编码: 84193990.20
商品名称: 其他烟丝烘干机
商品描述: 其他烟丝烘干机
申报要素: 1:品名;2:品牌类型;3:出口享惠情况;...
法定第一单位: 台
法定第二单位: 千克
海关监管条件: O
  许可证或批文:
    - O: 自动进口许可证（机电产品）
检验检疫类别: 无
查询状态: 成功
============================================================
```

### JSON文件（data/output/）
```json
{
  "query_time": "2025-11-24 10:30:00",
  "total_count": 3,
  "success_count": 3,
  "failed_count": 0,
  "data": [
    {
      "hs_code": "84193990.20",
      "product_name": "其他烟丝烘干机",
      "declaration_elements": "...",
      "first_unit": "台",
      "second_unit": "千克",
      "customs_supervision_conditions": {...},
      "inspection_quarantine": {...},
      "description": "其他烟丝烘干机",
      "search_success": true,
      "error_message": ""
    }
  ]
}
```

## 🔍 日志查看

运行日志保存在 `logs/hs_code_scraper.log`

查看日志可以了解：
- 查询过程
- 搜索尝试
- 错误信息
- 成功/失败统计

## ⚠️ 注意事项

1. 遵守网站使用条款
2. 合理控制查询频率
3. 查询结果仅供参考
4. 重要数据请人工核查
5. 需要稳定的网络连接

## 🐛 故障排除

### 问题1: 找不到搜索结果
**解决方案**: 
- 使用更通用的关键词
- 增加 `MAX_SEARCH_ATTEMPTS` 配置

### 问题2: 网络请求超时
**解决方案**:
- 检查网络连接
- 增加 `REQUEST_TIMEOUT` 配置
- 增加 `MAX_RETRIES` 配置

### 问题3: 依赖安装失败
**解决方案**:
```cmd
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📚 更多文档

- `README.md` - 完整的项目说明文档
- `QUICK_START.md` - 快速开始指南
- `PROJECT_SUMMARY.md` - 项目实现总结

## 🎉 开始使用

现在你可以开始使用这个工具了！

```cmd
# 快速测试
python test_example.py

# 或直接查询
python main.py -s "你要查询的商品名称"
```

祝使用愉快！
