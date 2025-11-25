# GitHub Copilot 项目指导文档

> **项目**: HS编码查询工具 (HS Code Query System)  
> **最后更新**: 2025-11-25  
> **版本**: v1.1.0

---

## 📋 项目概述

### 项目目标
构建一个智能的海关HS编码查询系统，支持：
1. 根据中文商品名称自动查询HS编码
2. 提供REST API供AI智能体和自动化系统调用
3. 智能中文分词和相似度匹配
4. 自动过滤已作废的HS编码
5. 完整提取海关申报所需的所有信息

### 核心价值
- **智能化**: 自动中文分词、多关键词尝试、相似度匹配
- **准确性**: 双层过滤机制确保返回有效HS编码
- **完整性**: 提取申报要素、监管条件、检验检疫等完整信息
- **易用性**: 命令行工具 + REST API + 自动文档
- **可靠性**: 重试机制、错误处理、详细日志

---

## 🏗️ 系统架构

### 技术栈
```
前端接口:
  - 命令行工具 (argparse)
  - REST API (FastAPI + Uvicorn)
  - Swagger UI 自动文档

后端核心:
  - 爬虫引擎: requests + BeautifulSoup4
  - 中文分词: jieba
  - 相似度匹配: rapidfuzz (FuzzyWuzzy)
  - 数据验证: Pydantic
  - 日志系统: logging

数据存储:
  - JSON 格式输出
  - 文件系统存储

外部集成:
  - ngrok 内网穿透
```

### 模块结构
```
data_search/
├── src/                        # 核心模块
│   ├── scraper.py             # 爬虫主逻辑 (HSCodeScraper)
│   ├── parser.py              # HTML解析 (HTMLParser)
│   ├── search_optimizer.py    # 搜索优化 (SearchOptimizer)
│   ├── storage.py             # 数据存储 (DataStorage)
│   └── utils.py               # 工具函数
├── config/
│   └── settings.py            # 配置文件
├── api_server.py              # FastAPI 服务器
├── main.py                    # 命令行入口
└── test_api.py                # API 测试
```

---

## 🔄 执行流程

### 查询流程图
```
用户输入商品名称
    ↓
SearchOptimizer.generate_search_keywords()
    ├─→ jieba 中文分词
    ├─→ 生成多个关键词组合
    └─→ 按词长度排序
    ↓
循环尝试每个关键词
    ↓
HSCodeScraper.search_products()
    ├─→ 发送搜索请求
    ├─→ 解析搜索结果页 (HTMLParser)
    ├─→ [Layer 1] 过滤"已作废"商品
    └─→ 相似度匹配选择最佳结果
    ↓
找到候选商品 → 访问详情页
    ↓
HTMLParser.parse_detail_page()
    ├─→ 提取HS编码
    ├─→ 提取申报要素
    ├─→ 提取监管条件
    ├─→ 提取检验检疫
    ├─→ [Layer 2] 检查是否作废
    └─→ 如作废，尝试下一个候选
    ↓
返回完整数据
    ↓
DataStorage.save_*() → JSON文件
```

### 关键算法

#### 1. 双层作废过滤机制
```python
# Layer 1: 搜索结果页过滤
if '已作废' in product_name:
    continue  # 跳过此结果

# Layer 2: 详情页验证 + 回退
if '已作废' in detail_page_name:
    # 尝试下一个候选商品
    for next_candidate in candidates:
        if valid(next_candidate):
            return next_candidate
```

#### 2. 相似度匹配 (rapidfuzz)
```python
from rapidfuzz import fuzz

# 使用 token_set_ratio 处理中文
score = fuzz.token_set_ratio(query, candidate)
if score >= MIN_SIMILARITY_SCORE:
    return candidate
```

#### 3. 智能关键词生成
```python
# 策略优先级:
1. 完整商品名
2. 最长词组组合
3. 单个关键词
4. 逐步减少关键词数量
```

---

## ⚙️ 配置说明

### 环境要求
```yaml
Python: >= 3.8
操作系统: Windows / Linux / macOS
网络: 需访问 https://www.i5a6.com
```

### 依赖包版本
```ini
# 核心依赖 (requirements.txt)
requests==2.31.0+
beautifulsoup4==4.12.0+
lxml==4.9.3+
jieba==0.42.1+
rapidfuzz==3.0.0+

# API 依赖 (requirements_api.txt)
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
```

### 关键配置参数
```python
# config/settings.py

# 目标网站
BASE_URL = "https://www.i5a6.com"

# 请求配置
REQUEST_TIMEOUT = 10      # 超时时间(秒)
MAX_RETRIES = 3          # 最大重试次数
REQUEST_DELAY = 1        # 请求间隔(秒)

# 搜索优化
MAX_SEARCH_ATTEMPTS = 5   # 最大搜索尝试次数
MIN_SIMILARITY_SCORE = 0.6  # 最小相似度阈值(0-1)

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8000
```

---

## ✅ 已实现功能

### 核心功能
- [x] **智能搜索**
  - 中文分词 (jieba)
  - 多关键词组合尝试
  - 相似度匹配 (rapidfuzz)
  - 自动选择最佳结果

- [x] **数据提取**
  - HS商品编码
  - 商品名称和描述
  - 申报要素
  - 法定第一/第二单位
  - 海关监管条件 (代码+名称)
  - 检验检疫类别 (代码+名称)

- [x] **质量保证**
  - 双层"已作废"过滤
  - 候选商品回退机制
  - 网络请求重试
  - 数据完整性验证

- [x] **使用接口**
  - 命令行工具 (单个/批量/文件)
  - Python API (直接调用)
  - REST API (FastAPI)
  - Swagger UI 文档

### API 端点
```
GET  /              # API 首页
GET  /health        # 健康检查
POST /api/query     # 单个商品查询
POST /api/batch_query   # 批量查询
POST /api/query_by_code # 按HS编码查询
GET  /docs          # Swagger UI 文档
GET  /redoc         # ReDoc 文档
```

### 数据格式
```json
{
  "hs_code": "08081000.00",
  "product_name": "鲜苹果",
  "description": "鲜苹果",
  "declaration_elements": "1:品名;2:品牌类型;...",
  "first_unit": "千克",
  "second_unit": "无",
  "customs_supervision_conditions": {
    "code": "AB",
    "details": [
      {"code": "A", "name": "入境货物通关单"},
      {"code": "B", "name": "出境货物通关单"}
    ]
  },
  "inspection_quarantine": {
    "code": "PQ",
    "details": [...]
  },
  "search_success": true,
  "error_message": ""
}
```

---

## 🎯 运行原则 & 最佳实践

### 代码规范
1. **类型提示**: 所有函数使用类型提示
   ```python
   def query_by_product_name(self, product_name: str) -> dict:
   ```

2. **错误处理**: 三层异常处理
   - 网络请求异常 → 重试
   - 解析失败 → 记录日志并返回错误
   - 验证失败 → 明确错误信息

3. **日志记录**: 关键步骤必须记录
   ```python
   logger.info(f"查询商品: {product_name}")
   logger.warning(f"已作废商品，尝试下一个候选")
   logger.error(f"解析失败: {e}")
   ```

4. **配置驱动**: 避免硬编码
   - 所有可调参数在 `config/settings.py`
   - 支持环境变量覆盖

### 数据处理原则
1. **防御性编程**: 假设所有外部数据可能为空
   ```python
   hs_code = data_dict.get('hs_code', '')
   if not hs_code:
       return error_result
   ```

2. **数据清洗**: 
   - 去除多余空白 (`strip()`)
   - 统一格式
   - 验证必填字段

3. **容错性**: 
   - 网络失败 → 重试
   - 第一候选作废 → 尝试下一个
   - 解析失败 → 降级返回部分数据

### 性能优化
1. **请求控制**: 
   - 延迟 1 秒避免封禁
   - 超时设置防止长时间等待
   - 会话复用减少连接开销

2. **缓存策略**: 
   - Session 对象复用
   - 相同查询可考虑缓存结果

3. **并发考虑**:
   - 当前同步实现
   - FastAPI 支持异步（可优化）

---

## 🚀 改进方向

### 优先级 P0 (立即实施)
- [ ] **异步化改造**
  - 将 scraper 改为 async/await
  - 利用 FastAPI 异步特性
  - 批量查询并发执行
  - 预期提升: 批量查询速度 3-5x

- [ ] **缓存机制**
  - Redis 缓存查询结果
  - TTL: 7天 (HS编码较稳定)
  - 缓存命中率预期: 60%+
  ```python
  @cache(ttl=604800)  # 7天
  async def query_by_product_name(name: str):
      ...
  ```

### 优先级 P1 (短期规划)
- [ ] **数据库存储**
  - SQLite / PostgreSQL 存储历史查询
  - 查询分析和统计
  - 热门商品推荐

- [ ] **Excel 导入/导出**
  - 批量导入 Excel 商品列表
  - 导出查询结果为 Excel
  - 使用 openpyxl / pandas

- [ ] **WebSocket 实时推送**
  - 批量查询进度推送
  - 适用于大批量场景
  ```python
  @app.websocket("/ws/batch")
  async def batch_query_ws(websocket: WebSocket):
      for result in batch_results:
          await websocket.send_json(result)
  ```

- [ ] **监控和告警**
  - Prometheus metrics
  - 查询成功率监控
  - 响应时间监控
  - 失败告警

### 优先级 P2 (中期规划)
- [ ] **多网站聚合**
  - 支持多个HS编码查询网站
  - 结果交叉验证
  - 自动选择最优数据源

- [ ] **机器学习优化**
  - 训练商品名称 → HS编码模型
  - 优化关键词选择策略
  - 相似度算法调优

- [ ] **GraphQL API**
  - 灵活的字段查询
  - 批量查询优化
  ```graphql
  query {
    product(name: "苹果") {
      hsCode
      declarationElements
    }
  }
  ```

- [ ] **代理池支持**
  - 避免IP封禁
  - 负载均衡
  - 自动切换代理

### 优先级 P3 (长期规划)
- [ ] **前端界面**
  - Web UI (React / Vue)
  - 拖拽上传 Excel
  - 可视化查询结果

- [ ] **移动端支持**
  - 微信小程序
  - 移动端 H5

- [ ] **企业功能**
  - 用户系统和权限
  - API 调用配额
  - 数据导出限制

---

## 📐 代码示例

### 添加新的查询来源
```python
# src/scraper.py

class HSCodeScraper:
    def query_from_source_b(self, product_name: str) -> dict:
        """从备用数据源查询"""
        # 1. 构造请求URL
        url = f"{BACKUP_URL}/search?q={product_name}"
        
        # 2. 发送请求
        response = self._make_request(url)
        
        # 3. 解析结果
        results = self.parser.parse_search_results_b(response.text)
        
        # 4. 相似度匹配
        best_match = self.optimizer.find_best_match(
            product_name, results
        )
        
        return best_match
```

### 添加缓存装饰器
```python
# src/utils.py

from functools import wraps
import json
from datetime import datetime, timedelta

def cache_result(ttl_seconds=3600):
    """缓存查询结果装饰器"""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(product_name: str):
            # 检查缓存
            if product_name in cache:
                cached_data, cached_time = cache[product_name]
                if datetime.now() - cached_time < timedelta(seconds=ttl_seconds):
                    logger.info(f"缓存命中: {product_name}")
                    return cached_data
            
            # 执行查询
            result = func(product_name)
            
            # 存入缓存
            cache[product_name] = (result, datetime.now())
            return result
        
        return wrapper
    return decorator

# 使用
@cache_result(ttl_seconds=86400)  # 24小时
def query_by_product_name(self, product_name: str) -> dict:
    ...
```

### 异步化改造
```python
# src/scraper_async.py

import asyncio
import aiohttp

class AsyncHSCodeScraper:
    async def query_by_product_name(self, product_name: str) -> dict:
        """异步查询"""
        async with aiohttp.ClientSession() as session:
            # 生成关键词
            keywords = self.optimizer.generate_search_keywords(product_name)
            
            # 并发尝试所有关键词
            tasks = [
                self._search_by_keyword(session, kw)
                for kw in keywords
            ]
            results = await asyncio.gather(*tasks)
            
            # 返回第一个成功的
            for result in results:
                if result.get('search_success'):
                    return result
            
            return error_result
    
    async def batch_query(self, product_names: list) -> list:
        """异步批量查询"""
        tasks = [
            self.query_by_product_name(name)
            for name in product_names
        ]
        return await asyncio.gather(*tasks)
```

---

## 🧪 测试指南

### 单元测试
```python
# tests/test_scraper.py

import pytest
from src.scraper import HSCodeScraper

def test_query_valid_product():
    scraper = HSCodeScraper()
    result = scraper.query_by_product_name("苹果")
    
    assert result['search_success'] == True
    assert result['hs_code'] != ''
    assert '已作废' not in result['product_name']

def test_query_invalid_product():
    scraper = HSCodeScraper()
    result = scraper.query_by_product_name("不存在的商品xyz123")
    
    assert result['search_success'] == False
    assert 'error_message' in result
```

### API 测试
```python
# tests/test_api.py

from fastapi.testclient import TestClient
from api_server import app

client = TestClient(app)

def test_query_endpoint():
    response = client.post(
        "/api/query",
        json={"product_name": "苹果"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
```

---

## 📚 参考资料

### 官方文档
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [rapidfuzz 文档](https://maxbachmann.github.io/RapidFuzz/)
- [jieba 分词](https://github.com/fxsjy/jieba)

### 项目文档
- [README.md](../README.md) - 项目说明
- [API_README.md](../API_README.md) - API 文档
- [QUICK_START.md](../QUICK_START.md) - 快速开始
- [docs/CHANGELOG.md](../docs/CHANGELOG.md) - 更新日志

### 相关技术
- [HS编码介绍](https://baike.baidu.com/item/HS%E7%BC%96%E7%A0%81)
- [海关申报要素](https://www.customs.gov.cn/)

---

## 💡 GitHub Copilot 使用建议

### 如何让 Copilot 更好地理解项目

1. **打开此文件**: 让 Copilot 读取项目上下文
   ```
   # 在编辑器中打开
   .github/copilot-instructions.md
   ```

2. **引用架构**: 编写代码时提及模块名
   ```python
   # 在 scraper.py 中添加新方法
   # 使用 SearchOptimizer 优化关键词
   ```

3. **遵循模式**: 参考现有代码风格
   ```python
   # 参考 query_by_product_name 的结构
   # 返回统一的 dict 格式
   ```

### 常用提示词

**添加新功能:**
```
"参考 query_by_product_name 方法，添加一个支持按HS编码前缀搜索的功能"
```

**重构代码:**
```
"将这个同步函数改造为异步版本，使用 aiohttp"
```

**添加测试:**
```
"为 SearchOptimizer.generate_search_keywords 方法编写单元测试"
```

**性能优化:**
```
"优化 batch_query 方法，使用并发请求提升性能"
```

### 注意事项

1. **保持一致性**: 新代码应匹配现有风格
2. **错误处理**: 参考现有的三层异常处理
3. **日志记录**: 关键操作必须记录日志
4. **类型提示**: 所有函数添加类型注解
5. **文档字符串**: 使用中文注释说明

---

## 🔖 版本历史

- **v1.1.0** (2025-11-24)
  - 迁移到 FastAPI
  - 添加 Swagger UI 自动文档
  - Pydantic 数据验证

- **v1.0.2** (2025-11-24)
  - 升级相似度算法 (rapidfuzz)
  - 改进中文匹配准确度

- **v1.0.1** (2025-11-24)
  - 修复数据解析问题
  - 修复URL重复问题
  - 添加双层作废过滤

- **v1.0.0** (2025-11-24)
  - 初始版本
  - 核心爬虫功能
  - 命令行工具

---

**维护者**: 开发团队  
**许可证**: MIT  
**最后更新**: 2025-11-25
