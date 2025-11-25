# 发布 MCP HS Code Query Server 到 PyPI

## 📦 发布流程概述

要让其他人通过 `uvx mcp-hs-code-query` 直接使用，你需要将这个包发布到 **PyPI (Python Package Index)**。

---

## 🚀 完整发布步骤

### 步骤 1: 准备发布文件

#### 1.1 确保项目结构正确 ✅

你的项目已经具备以下必要文件：
- ✅ `pyproject.toml` - 包配置和依赖
- ✅ `mcp_hs_code_query/__init__.py` - 包初始化
- ✅ `mcp_hs_code_query/__main__.py` - 命令行入口
- ✅ `mcp_hs_code_query/server.py` - MCP服务器
- ✅ `README_MCP.md` - 文档

#### 1.2 创建额外必要文件

需要添加以下文件：

**LICENSE** 文件（MIT许可证）：
```
MIT License

Copyright (c) 2025 HS Code Query Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
（完整MIT许可证文本）
```

**MANIFEST.in** 文件（包含额外文件）：
```
include README_MCP.md
include LICENSE
include requirements.txt
recursive-include src *.py
recursive-include config *.py
```

#### 1.3 更新 `pyproject.toml`

确保包含正确的元数据：
```toml
[project]
name = "mcp-hs-code-query"
version = "1.0.0"  # 遵循语义化版本
description = "MCP server for intelligent HS code queries"
readme = "README_MCP.md"
```

---

### 步骤 2: 注册 PyPI 账号

#### 2.1 注册账号
1. 访问 https://pypi.org/account/register/
2. 注册一个账号
3. 验证邮箱

#### 2.2 生成 API Token（推荐）
1. 登录 PyPI
2. 访问 https://pypi.org/manage/account/token/
3. 创建新 Token
4. 保存 Token（只显示一次）

#### 2.3 配置本地认证

创建 `~/.pypirc` 文件（Windows: `%USERPROFILE%\.pypirc`）：
```ini
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-AgE...你的token...
```

---

### 步骤 3: 构建发布包

#### 3.1 安装构建工具

```bash
# 安装 build 工具
pip install build twine

# 或使用 uv
uv pip install build twine
```

#### 3.2 构建分发包

```bash
# 清理旧的构建文件
rmdir /s /q dist build mcp_hs_code_query.egg-info

# 构建包
python -m build
```

这会在 `dist/` 目录生成：
- `mcp-hs-code-query-1.0.0.tar.gz` (源代码分发)
- `mcp_hs_code_query-1.0.0-py3-none-any.whl` (wheel包)

---

### 步骤 4: 测试本地安装

#### 4.1 在测试环境中安装

```bash
# 创建新的虚拟环境测试
python -m venv test_env
test_env\Scripts\activate

# 从本地安装
pip install dist/mcp_hs_code_query-1.0.0-py3-none-any.whl

# 测试运行
mcp-hs-code-query
```

#### 4.2 测试 uvx 本地运行

```bash
# 测试 uvx 从本地路径运行
uvx --from dist/mcp_hs_code_query-1.0.0-py3-none-any.whl mcp-hs-code-query
```

---

### 步骤 5: 发布到 PyPI

#### 5.1 先发布到 TestPyPI（推荐）

TestPyPI 是测试用的 PyPI 镜像：

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ mcp-hs-code-query
```

#### 5.2 发布到正式 PyPI

确认无误后，发布到正式 PyPI：

```bash
# 上传到 PyPI
twine upload dist/*

# 输入用户名: __token__
# 输入密码: 你的 PyPI token
```

#### 5.3 验证发布成功

```bash
# 等待几分钟后测试
uvx mcp-hs-code-query

# 或者安装
pip install mcp-hs-code-query
```

---

### 步骤 6: 发布后的工作

#### 6.1 创建 GitHub Release

1. 在 GitHub 上创建仓库
2. 推送代码到 GitHub
3. 创建 Release 标签（如 `v1.0.0`）
4. 在 Release 说明中包含：
   - 安装方法
   - 使用示例
   - 更新日志

#### 6.2 更新文档

在 README_MCP.md 中更新：
```markdown
## 快速安装

其他用户可以直接使用 uvx 一键部署：

\`\`\`bash
# 无需安装，直接运行
uvx mcp-hs-code-query

# 在 Claude Desktop 中配置
{
  "mcpServers": {
    "hs-code-query": {
      "command": "uvx",
      "args": ["mcp-hs-code-query"]
    }
  }
}
\`\`\`
```

#### 6.3 添加徽章

在 README 顶部添加：
```markdown
[![PyPI version](https://badge.fury.io/py/mcp-hs-code-query.svg)](https://badge.fury.io/py/mcp-hs-code-query)
[![Downloads](https://pepy.tech/badge/mcp-hs-code-query)](https://pepy.tech/project/mcp-hs-code-query)
```

---

## 🔄 版本更新流程

当你需要发布新版本时：

```bash
# 1. 更新版本号（pyproject.toml）
[project]
version = "1.1.0"  # 遵循语义化版本

# 2. 更新 CHANGELOG
# 记录新功能和修复

# 3. 重新构建
python -m build

# 4. 上传新版本
twine upload dist/*

# 5. 创建 Git 标签
git tag v1.1.0
git push origin v1.1.0
```

---

## 📝 语义化版本规则

- **主版本号** (1.x.x): 不兼容的API变更
- **次版本号** (x.1.x): 向后兼容的新功能
- **修订号** (x.x.1): 向后兼容的bug修复

示例：
- `1.0.0` - 初始版本
- `1.0.1` - 修复bug
- `1.1.0` - 添加新功能
- `2.0.0` - 重大变更

---

## 🌍 推广你的包

### 1. 添加到 MCP 服务器列表

Model Context Protocol 官方维护了服务器列表，提交PR添加你的服务器：
- 仓库: https://github.com/modelcontextprotocol/servers
- 提交你的服务器信息

### 2. 社区分享

- 在 MCP Discord/论坛分享
- 发布博客文章介绍使用方法
- 制作使用视频教程

### 3. 文档网站

考虑使用以下工具创建文档网站：
- MkDocs
- Sphinx
- GitHub Pages

---

## ✅ 发布前检查清单

- [ ] `pyproject.toml` 配置正确
- [ ] 包含 LICENSE 文件
- [ ] README_MCP.md 完整详细
- [ ] 版本号遵循语义化版本
- [ ] 所有依赖在 `dependencies` 中声明
- [ ] 测试所有工具功能正常
- [ ] 在 TestPyPI 测试通过
- [ ] GitHub 仓库已创建
- [ ] .gitignore 排除不必要文件

---

## 🔧 故障排除

### 问题1: 包名已存在
**解决**: 在 PyPI 搜索，确认名称未被占用。如果被占用，修改包名。

### 问题2: 上传失败
**解决**: 检查 `~/.pypirc` 配置，确认 Token 正确。

### 问题3: uvx 找不到包
**解决**: 等待几分钟（PyPI 同步需要时间），或清除 uv 缓存：
```bash
uv cache clean
```

### 问题4: 导入错误
**解决**: 检查 `pyproject.toml` 中的 `packages` 配置，确保包含所有必要模块。

---

## 📚 参考资源

- [PyPI 官方文档](https://packaging.python.org/)
- [Python 打包指南](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 文档](https://twine.readthedocs.io/)
- [语义化版本](https://semver.org/lang/zh-CN/)
- [MCP 服务器开发指南](https://modelcontextprotocol.io/)

---

## 💡 最佳实践

1. **版本管理**: 每次发布都打 Git 标签
2. **变更日志**: 维护详细的 CHANGELOG.md
3. **测试**: 发布前在 TestPyPI 充分测试
4. **文档**: 保持 README 和示例代码最新
5. **依赖**: 明确依赖版本范围，避免破坏性更新
6. **安全**: 不要在代码中硬编码密钥
7. **CI/CD**: 使用 GitHub Actions 自动化发布流程

---

**准备好发布了吗？** 按照上述步骤，你的 MCP 服务器很快就能被全世界的 AI 智能体使用！ 🚀
