# ngrok 内网穿透配置指南

## 1. 安装 ngrok

### Windows 安装步骤

1. **下载 ngrok**
   - 访问 [ngrok 官网](https://ngrok.com/download)
   - 选择 Windows 版本下载
   - 解压 `ngrok.exe`

2. **添加到系统路径**
   
   **方法 1：添加到系统 PATH（推荐）**
   ```cmd
   # 将 ngrok.exe 复制到 C:\Windows\System32
   # 或者将 ngrok.exe 所在目录添加到系统 PATH 环境变量
   ```

   **方法 2：放到项目目录**
   ```cmd
   # 将 ngrok.exe 复制到项目根目录
   copy ngrok.exe C:\Users\dela1\Desktop\data_search\
   ```

3. **验证安装**
   ```cmd
   ngrok version
   ```

## 2. 注册并获取认证令牌（可选但推荐）

免费版有限制，注册后可获得更多功能：

1. **注册账号**
   - 访问 [ngrok.com](https://ngrok.com/)
   - 点击 "Sign up" 注册账号（支持 GitHub/Google 登录）

2. **获取认证令牌**
   - 登录后访问 [Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
   - 复制你的 authtoken

3. **配置认证令牌**
   ```cmd
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

## 3. 启动方式

### 方式 1：使用 Python 脚本（推荐）

自动启动 API 服务和 ngrok，并显示公网地址：

```bash
python start_api_with_ngrok.py
```

### 方式 2：使用批处理脚本

双击运行 `start_ngrok.bat`，或在命令行中：

```cmd
start_ngrok.bat
```

### 方式 3：手动启动

**终端 1 - 启动 API 服务：**
```cmd
python api_server.py
```

**终端 2 - 启动 ngrok：**
```cmd
ngrok http 5000
```

## 4. 获取公网地址

启动后，你会看到类似输出：

```
ngrok                                                                (Ctrl+C to quit)

Session Status                online
Account                       your-email@example.com (Plan: Free)
Version                       3.x.x
Region                        Asia Pacific (ap)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**公网地址示例：** `https://abc123.ngrok-free.app`

## 5. 测试公网 API

使用公网地址替换 `localhost:5000`：

### 健康检查
```bash
curl https://abc123.ngrok-free.app/health
```

### 查询商品
```bash
curl -X POST https://abc123.ngrok-free.app/api/query \
  -H "Content-Type: application/json" \
  -d "{\"product_name\":\"苹果\"}"
```

### Python 调用示例
```python
import requests

# 替换为你的 ngrok 公网地址
BASE_URL = "https://abc123.ngrok-free.app"

response = requests.post(
    f'{BASE_URL}/api/query',
    json={'product_name': '苹果'}
)

print(response.json())
```

## 6. ngrok 控制面板

访问 `http://localhost:4040` 可以查看：
- 实时请求日志
- 请求/响应详情
- 流量统计
- 重放请求

## 7. 常见问题

### Q1: ngrok 命令未找到
**解决方法：**
- 确认 ngrok.exe 在系统 PATH 中
- 或使用完整路径：`C:\path\to\ngrok.exe http 5000`

### Q2: ngrok 连接失败
**可能原因：**
- 网络防火墙阻止
- 代理设置问题
- 端口被占用

**解决方法：**
```cmd
# 检查端口占用
netstat -ano | findstr :5000

# 更换端口
ngrok http 8000
```

### Q3: 免费版限制
**免费版限制：**
- 每次启动生成随机 URL
- 连接数限制
- 带宽限制

**升级方案：**
- 注册账号后获得固定域名
- 付费版获得更多功能

### Q4: 公网访问慢
**优化建议：**
- 选择最近的 ngrok 区域
- 使用付费版获得更好性能
- 考虑部署到云服务器

## 8. 安全建议

1. **不要在公网暴露敏感数据**
   - API 返回的数据是公开的
   - 生产环境建议添加认证

2. **添加 API 访问控制**
   ```python
   # 在 api_server.py 中添加
   from flask import request
   
   @app.before_request
   def check_api_key():
       api_key = request.headers.get('X-API-Key')
       if api_key != 'YOUR_SECRET_KEY':
           return jsonify({'error': 'Unauthorized'}), 401
   ```

3. **监控访问日志**
   - 定期检查 ngrok 控制面板
   - 发现异常立即停止服务

4. **临时使用**
   - ngrok 免费版适合临时测试
   - 长期使用建议部署到云服务

## 9. 替代方案

如果 ngrok 不可用，可以考虑：

1. **国内替代品**
   - natapp.cn
   - frp
   - cpolar

2. **云服务部署**
   - 阿里云
   - 腾讯云
   - AWS

3. **容器化部署**
   - Docker
   - Kubernetes

## 10. 停止服务

按 `Ctrl+C` 停止 ngrok 和 API 服务

---

## 快速参考

| 操作 | 命令 |
|------|------|
| 启动（自动） | `python start_api_with_ngrok.py` |
| 启动（批处理） | `start_ngrok.bat` |
| 查看版本 | `ngrok version` |
| 配置令牌 | `ngrok config add-authtoken TOKEN` |
| 启动隧道 | `ngrok http 5000` |
| 控制面板 | `http://localhost:4040` |
| 停止服务 | `Ctrl+C` |

---

**需要帮助？**
- ngrok 文档: https://ngrok.com/docs
- API 文档: 查看 `API_README.md`
