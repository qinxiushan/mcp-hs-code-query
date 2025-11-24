# HS编码查询工具 - 快速开始指南

## 一、安装依赖

打开命令提示符（cmd），进入项目目录：

```cmd
cd c:\Users\dela1\Desktop\data_search
pip install -r requirements.txt
```

## 二、使用方法

### 方法1: 命令行使用（推荐）

#### 1. 单个商品查询
```cmd
python main.py -s "烘干机"
```

#### 2. 批量查询多个商品
```cmd
python main.py -b "苹果" "香蕉" "橙子"
```

#### 3. 从文件批量查询
```cmd
python main.py -f data/input/products.txt
```

查询结果会自动保存到 `data/output/` 目录下的JSON文件中。

### 方法2: 交互式测试

运行测试示例：
```cmd
python test_example.py
```

然后按照提示选择测试类型。

### 方法3: Python代码调用

创建自己的Python脚本：

```python
from src.scraper import HSCodeScraper
from src.storage import DataStorage

# 初始化
scraper = HSCodeScraper()
storage = DataStorage()

# 查询商品
result = scraper.query_by_product_name("苹果手机")

# 显示结果
print(storage.format_result_for_display(result))

# 保存结果
storage.save_single_result(result)

# 关闭
scraper.close()
```

## 三、查看结果

### 控制台输出
查询结果会直接在控制台显示，包括：
- HS编码
- 商品名称
- 申报要素
- 法定单位
- 监管条件
- 检验检疫
- 商品描述

### JSON文件
结果自动保存在 `data/output/` 目录：
- 单个查询: `hs_编码.json`
- 批量查询: `batch_results_时间戳.json`

## 四、配置调整

如需修改配置，编辑 `config/settings.py`：

```python
# 调整重试次数
MAX_RETRIES = 5

# 调整搜索尝试次数
MAX_SEARCH_ATTEMPTS = 8

# 调整相似度阈值
MIN_SIMILARITY_SCORE = 0.5
```

## 五、常见问题

### Q1: 找不到搜索结果怎么办？
A: 尝试使用更通用的关键词，或在配置中增加搜索尝试次数。

### Q2: 如何批量查询大量商品？
A: 创建文本文件 `data/input/products.txt`，每行一个商品名称，然后使用 `-f` 参数。

### Q3: 如何更换目标网站？
A: 修改 `config/settings.py` 中的 `BASE_URL`，并根据新网站结构调整 `src/parser.py`。

## 六、输出示例

### 控制台输出示例：
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

### JSON输出示例：
```json
{
  "query_time": "2025-11-24 10:30:00",
  "data": {
    "hs_code": "84193990.20",
    "product_name": "其他烟丝烘干机",
    "search_success": true,
    ...
  }
}
```

## 七、日志查看

运行日志保存在 `logs/hs_code_scraper.log`，可以查看详细的执行过程和错误信息。

## 八、注意事项

1. ⚠️ 请遵守网站使用条款，合理控制查询频率
2. ⚠️ 查询结果仅供参考，重要数据请人工核查
3. ⚠️ 需要稳定的网络连接
4. ⚠️ 如果网站结构变化，可能需要更新解析代码

## 九、技术支持

如遇到问题：
1. 查看 `logs/hs_code_scraper.log` 日志文件
2. 检查网络连接
3. 确认目标网站是否可访问
4. 查看README.md获取更多信息
