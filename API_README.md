# HS 编码查询 API 文档 (FastAPI)

## 简介

本 API 使用 **FastAPI** 框架构建，提供海关 HS 编码查询服务，支持根据商品名称查询对应的 HS 编码及详细信息。适合 AI 智能体、自动化系统等场景调用。

## FastAPI 特性

- ✅ **自动文档**: 访问 `/docs` 查看 Swagger UI 交互式文档
- ✅ **类型验证**: Pydantic 模型自动验证请求数据
- ✅ **高性能**: 基于 Starlette 和 Uvicorn 的异步框架
- ✅ **现代化**: 完整的类型提示和异步支持

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_api.txt
```

### 2. 启动服务

```bash
python api_server.py
```

默认服务地址：`http://localhost:8000`

### 3. 访问 API 文档

启动后可访问自动生成的交互式文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API 首页**: http://localhost:8000/

### 4. 环境变量配置（可选）

```bash
# Windows CMD
set API_HOST=0.0.0.0
set API_PORT=8000

# Windows PowerShell
$env:API_HOST="0.0.0.0"
$env:API_PORT="8000"

# Linux/Mac
export API_HOST=0.0.0.0
export API_PORT=8000
```

注意：FastAPI 使用 uvicorn 作为 ASGI 服务器，配置更加灵活。

## API 接口文档

### 1. 健康检查

**请求**
```
GET /health
```

**响应示例**
```json
{
  "status": "ok"
}
```

---

### 2. 单个商品查询

根据商品名称查询 HS 编码。

**请求**
```
POST /api/query
Content-Type: application/json

{
  "product_name": "苹果"
}
```

**响应示例 - 成功**
```json
{
  "success": true,
  "data": {
    "query_product_name": "苹果",
    "hs_code": "08081000.00",
    "product_name": "鲜苹果",
    "description": "鲜苹果",
    "declaration_elements": "1:品名;2:品牌类型;3:出口享惠情况;...",
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
      "details": [
        {"code": "P", "name": "进境动植物、动植物产品检疫"},
        {"code": "Q", "name": "出境动植物、动植物产品检疫"}
      ]
    },
    "search_success": true,
    "error_message": ""
  }
}
```

**响应示例 - 失败**
```json
{
  "success": false,
  "error": "未找到匹配结果",
  "error_code": "QUERY_FAILED",
  "data": {
    "query_product_name": "不存在的商品",
    "hs_code": "",
    "search_success": false,
    "error_message": "未找到匹配结果，已尝试关键词: 不存在的商品"
  }
}
```

**错误码说明**
- `EMPTY_REQUEST`: 请求体为空
- `MISSING_PRODUCT_NAME`: 商品名称参数缺失
- `QUERY_FAILED`: 查询失败（未找到匹配）
- `INTERNAL_ERROR`: 服务器内部错误

---

### 3. 批量查询

一次查询多个商品的 HS 编码。

**请求**
```
POST /api/batch_query
Content-Type: application/json

{
  "product_names": ["苹果", "香蕉", "笔记本电脑"]
}
```

**响应示例**
```json
{
  "success": true,
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "query_product_name": "苹果",
      "hs_code": "08081000.00",
      "product_name": "鲜苹果",
      "search_success": true,
      ...
    },
    {
      "query_product_name": "香蕉",
      "hs_code": "08030012.00",
      "product_name": "鲜香蕉",
      "search_success": true,
      ...
    },
    {
      "query_product_name": "笔记本电脑",
      "hs_code": "85249190.10",
      "product_name": "专用于平板电脑和笔记本电脑的带触摸屏的液晶模组",
      "search_success": true,
      ...
    }
  ]
}
```

**限制**
- 单次批量查询最多支持 **50** 个商品

**错误码说明**
- `INVALID_PRODUCT_NAMES`: product_names 参数无效
- `TOO_MANY_PRODUCTS`: 超过批量查询数量限制

---

### 4. 根据 HS 编码查询详情

已知 HS 编码，查询详细信息。

**请求**
```
POST /api/query_by_code
Content-Type: application/json

{
  "hs_code": "08081000.00"
}
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "hs_code": "08081000.00",
    "product_name": "鲜苹果",
    "description": "鲜苹果",
    "declaration_elements": "...",
    "first_unit": "千克",
    "second_unit": "无",
    ...
  }
}
```

**错误码说明**
- `MISSING_HS_CODE`: HS编码参数缺失

---

## 使用示例

### Python 示例

```python
import requests

# 单个查询
response = requests.post(
    'http://localhost:8000/api/query',
    json={'product_name': '苹果'}
)
result = response.json()

if result['success']:
    print(f"HS编码: {result['data']['hs_code']}")
    print(f"商品名称: {result['data']['product_name']}")
else:
    print(f"查询失败: {result.get('detail', {}).get('error')}")

# 批量查询
response = requests.post(
    'http://localhost:8000/api/batch_query',
    json={'product_names': ['苹果', '香蕉', '橙子']}
)
result = response.json()

print(f"成功: {result['successful']}/{result['total']}")
for item in result['results']:
    if item['search_success']:
        print(f"{item['query_product_name']}: {item['hs_code']}")
```

### JavaScript 示例

```javascript
// 单个查询
fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    product_name: '苹果'
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('HS编码:', data.data.hs_code);
      console.log('商品名称:', data.data.product_name);
    } else {
      console.log('查询失败:', data.detail?.error || '未知错误');
    }
  });
```

### cURL 示例

```bash
# 单个查询
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"product_name":"苹果"}'

# 批量查询
curl -X POST http://localhost:8000/api/batch_query \
  -H "Content-Type: application/json" \
  -d '{"product_names":["苹果","香蕉","橙子"]}'

# 也可以使用 Swagger UI 进行测试
# 访问 http://localhost:8000/docs 进行交互式测试
```

---

## 测试

运行测试脚本：

```bash
# 先启动 API 服务
python api_server.py

# 在另一个终端运行测试
python test_api.py
```

---

## 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| query_product_name | string | 查询的商品名称 |
| hs_code | string | HS 编码 |
| product_name | string | 官方商品名称 |
| description | string | 商品描述 |
| declaration_elements | string | 申报要素 |
| first_unit | string | 法定第一单位 |
| second_unit | string | 法定第二单位 |
| customs_supervision_conditions | object | 海关监管条件 |
| inspection_quarantine | object | 检验检疫类别 |
| search_success | boolean | 查询是否成功 |
| error_message | string | 错误信息（失败时） |

---

## 性能建议

1. **单次查询延迟**：约 2-5 秒（受网络和网站响应速度影响）
2. **批量查询**：建议每批不超过 10 个商品，避免超时
3. **并发控制**：服务端自动处理，无需客户端控制
4. **缓存**：可在客户端实现缓存机制，减少重复查询

---

## 部署建议

### 使用 Uvicorn 部署（生产环境）

```bash
# 基础启动
uvicorn api_server:app --host 0.0.0.0 --port 8000

# 生产环境（多工作进程）
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4

# 使用 Gunicorn + Uvicorn workers
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 使用 Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements_api.txt

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 常见问题

**Q: API 响应很慢怎么办？**  
A: 查询速度受目标网站响应速度影响，建议客户端设置合理的超时时间（建议 30 秒）。

**Q: 可以并发调用 API 吗？**  
A: 可以，服务端会自动处理并发请求。

**Q: 已作废的 HS 编码会返回吗？**  
A: 不会，系统会自动过滤已作废的编码，返回有效的 HS 编码。

**Q: 支持 HTTPS 吗？**  
A: 需要配合 Nginx 或其他反向代理实现 HTTPS。

---

## 许可证

MIT License
