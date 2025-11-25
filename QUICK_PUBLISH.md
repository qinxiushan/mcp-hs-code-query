# 🚀 MCP HS Code Query - 快速发布指南

## 📋 当前状态

✅ 所有必要文件已创建:
- `pyproject.toml` - 包配置
- `mcp_hs_code_query/` - MCP服务器包
- `LICENSE` - MIT许可证
- `MANIFEST.in` - 包含文件清单
- `README_MCP.md` - 用户文档
- `.gitignore` - Git忽略文件
- `.github/workflows/publish.yml` - 自动发布工作流

## 🎯 发布到 PyPI 的三种方式

### 方式1: 使用辅助脚本（最简单）⭐

```cmd
publish.bat
```

按照菜单提示操作：
1. 安装构建工具
2. 本地构建测试
3. 发布到 TestPyPI（测试）
4. 发布到正式 PyPI

---

### 方式2: 手动命令行（推荐学习）

#### 步骤1: 安装工具
```cmd
pip install build twine
```

#### 步骤2: 构建包
```cmd
python -m build
```

#### 步骤3: 检查包
```cmd
twine check dist/*
```

#### 步骤4: 发布到 TestPyPI（测试）
```cmd
twine upload --repository testpypi dist/*
```

#### 步骤5: 测试安装
```cmd
pip install --index-url https://test.pypi.org/simple/ mcp-hs-code-query
```

#### 步骤6: 发布到正式 PyPI
```cmd
twine upload dist/*
```

---

### 方式3: GitHub Actions 自动发布（最专业）

1. **推送代码到 GitHub**:
```cmd
git init
git add .
git commit -m "Initial commit: MCP HS Code Query Server"
git remote add origin https://github.com/yourusername/mcp-hs-code-query.git
git push -u origin main
```

2. **在 GitHub 设置中添加 PyPI Token**:
   - Settings → Secrets and variables → Actions
   - 新建 Secret: `PYPI_API_TOKEN`
   - 粘贴你的 PyPI Token

3. **创建 GitHub Release**:
   - 在 GitHub 仓库点击 "Releases"
   - "Create a new release"
   - Tag version: `v1.0.0`
   - Release title: `v1.0.0 - Initial Release`
   - 点击 "Publish release"

4. **自动触发发布**:
   - GitHub Actions 会自动构建和发布到 PyPI

---

## 🔑 配置 PyPI 认证

### 注册 PyPI 账号
1. 访问 https://pypi.org/account/register/
2. 注册并验证邮箱

### 生成 API Token
1. 登录 PyPI
2. Account settings → API tokens
3. "Add API token"
4. Scope: "Entire account" (或特定项目)
5. 保存 Token（只显示一次！）

### 配置本地认证

创建 `%USERPROFILE%\.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgE...你的token...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgE...你的testpypi-token...
```

---

## ✅ 发布前检查清单

运行测试：
```cmd
python test_mcp_server.py
```

检查项目：
- [ ] 所有测试通过
- [ ] 版本号正确（`pyproject.toml`）
- [ ] README_MCP.md 文档完整
- [ ] LICENSE 文件存在
- [ ] 依赖列表完整
- [ ] .gitignore 配置正确
- [ ] 已在 TestPyPI 测试过

---

## 🌍 发布后的工作

### 1. 验证发布
```cmd
# 等待几分钟，然后测试
uvx mcp-hs-code-query
```

### 2. 更新 GitHub
```cmd
git tag v1.0.0
git push origin v1.0.0
```

### 3. 宣传你的项目
- 添加到 [MCP 服务器列表](https://github.com/modelcontextprotocol/servers)
- 分享到社交媒体
- 撰写博客文章

---

## 📚 其他用户如何使用

发布后，其他用户可以：

### 在 Claude Desktop 中使用
```json
{
  "mcpServers": {
    "hs-code-query": {
      "command": "uvx",
      "args": ["mcp-hs-code-query"]
    }
  }
}
```

### 直接运行
```cmd
uvx mcp-hs-code-query
```

### 安装使用
```cmd
pip install mcp-hs-code-query
mcp-hs-code-query
```

---

## 🔄 版本更新

当需要发布新版本时：

1. **更新版本号**（`pyproject.toml`）:
```toml
version = "1.1.0"
```

2. **更新文档**（`README_MCP.md` 和 `CHANGELOG.md`）

3. **重新构建和发布**:
```cmd
python -m build
twine upload dist/*
```

4. **创建 Git 标签**:
```cmd
git tag v1.1.0
git push origin v1.1.0
```

---

## 🆘 常见问题

### Q: 包名已被占用怎么办？
A: 在 https://pypi.org 搜索，确认可用后修改 `pyproject.toml` 中的 `name`

### Q: 上传失败怎么办？
A: 检查 `.pypirc` 配置，确认 Token 正确且有效

### Q: uvx 找不到包？
A: 等待5-10分钟（PyPI 需要同步），或清除缓存：`uv cache clean`

### Q: 如何撤回发布？
A: PyPI 不允许删除已发布版本，只能发布新版本

---

## 📞 需要帮助？

- 查看完整指南: [PUBLISH_GUIDE.md](PUBLISH_GUIDE.md)
- PyPI 文档: https://packaging.python.org/
- MCP 文档: https://modelcontextprotocol.io/

---

**准备好了吗？运行 `publish.bat` 开始发布！** 🚀
