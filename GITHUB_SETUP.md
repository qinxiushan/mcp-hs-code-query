# GitHub 仓库创建和配置指南

## 步骤 1: 在 GitHub 上创建仓库

### 1.1 访问 GitHub
1. 打开浏览器访问 https://github.com
2. 登录你的账号
3. 点击右上角的 `+` → `New repository`

### 1.2 填写仓库信息
- **Repository name**: `mcp-hs-code-query`
- **Description**: `MCP server for intelligent HS code queries - 智能海关HS编码查询服务`
- **Public/Private**: 选择 `Public`（公开仓库）
- **不要勾选** "Initialize this repository with:"
  - ❌ Add a README file
  - ❌ Add .gitignore
  - ❌ Choose a license
  
  （因为我们本地已经有这些文件了）

4. 点击 `Create repository`

---

## 步骤 2: 本地 Git 配置和推送

### 2.1 初始化本地仓库
在项目目录打开终端，运行：

```bash
cd C:\Users\dela1\Desktop\data_search

# 初始化 Git 仓库
git init

# 配置用户信息（如果还没配置）
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: MCP HS Code Query Server v1.0.0"
```

### 2.2 连接远程仓库并推送
```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/mcp-hs-code-query.git

# 推送代码
git branch -M main
git push -u origin main
```

如果提示需要认证：
- 使用 GitHub Personal Access Token（推荐）
- 或使用 GitHub Desktop

---

## 步骤 3: 创建 GitHub Release

### 3.1 在 GitHub 网页上创建 Release
1. 进入你的仓库页面
2. 点击右侧的 `Releases` → `Create a new release`
3. 填写信息：
   - **Choose a tag**: 输入 `v1.0.0`，点击 "Create new tag: v1.0.0 on publish"
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**: 

```markdown
## 🎉 Initial Release - MCP HS Code Query Server

### Features
- ✅ Intelligent HS code queries with Chinese word segmentation
- ✅ Fuzzy matching for accurate results
- ✅ Complete customs declaration information extraction
- ✅ Batch query support
- ✅ MCP protocol compatible
- ✅ One-command deployment with uvx

### Installation

**Using uvx (recommended):**
\`\`\`bash
uvx mcp-hs-code-query
\`\`\`

**Using pip:**
\`\`\`bash
pip install mcp-hs-code-query
mcp-hs-code-query
\`\`\`

**Configure in Claude Desktop:**
\`\`\`json
{
  "mcpServers": {
    "hs-code-query": {
      "command": "uvx",
      "args": ["mcp-hs-code-query"]
    }
  }
}
\`\`\`

### Links
- PyPI: https://pypi.org/project/mcp-hs-code-query/
- Documentation: See README.md
```

4. 点击 `Publish release`

---

## 步骤 4: 配置 GitHub Secrets（用于自动发布）

### 4.1 添加 PyPI Token
1. 在仓库页面，点击 `Settings`
2. 左侧菜单选择 `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 填写：
   - **Name**: `PYPI_API_TOKEN`
   - **Secret**: 粘贴你的 PyPI Token
5. 点击 `Add secret`

现在，每次创建 Release 时，GitHub Actions 会自动发布到 PyPI！

---

## 步骤 5: 更新 README 和项目链接

### 5.1 更新 README 中的链接
将 README_MCP.md 中的 GitHub 链接替换为实际地址。

### 5.2 更新 pyproject.toml
将项目 URL 更新为实际的 GitHub 地址。

---

## 步骤 6: 添加徽章到 README

在 README_MCP.md 顶部添加：

```markdown
# MCP HS Code Query Server

[![PyPI version](https://badge.fury.io/py/mcp-hs-code-query.svg)](https://pypi.org/project/mcp-hs-code-query/)
[![Downloads](https://pepy.tech/badge/mcp-hs-code-query)](https://pepy.tech/project/mcp-hs-code-query)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/mcp-hs-code-query.svg)](https://github.com/YOUR_USERNAME/mcp-hs-code-query/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## 步骤 7: 提交到 MCP 服务器列表

1. Fork 仓库：https://github.com/modelcontextprotocol/servers
2. 在 `src/servers.json` 中添加你的服务器：

```json
{
  "name": "mcp-hs-code-query",
  "displayName": "HS Code Query",
  "description": "Intelligent HS code queries with Chinese support",
  "repository": "https://github.com/YOUR_USERNAME/mcp-hs-code-query",
  "license": "MIT",
  "packageManager": "uvx",
  "packageName": "mcp-hs-code-query"
}
```

3. 提交 Pull Request

---

## 完整命令速查

```bash
# 初始化和推送
cd C:\Users\dela1\Desktop\data_search
git init
git add .
git commit -m "Initial commit: MCP HS Code Query Server v1.0.0"
git remote add origin https://github.com/YOUR_USERNAME/mcp-hs-code-query.git
git branch -M main
git push -u origin main

# 创建标签
git tag v1.0.0
git push origin v1.0.0

# 更新后推送
git add .
git commit -m "Update documentation and links"
git push
```

---

## 后续维护

### 发布新版本：
1. 更新 `pyproject.toml` 中的版本号
2. 更新 `CHANGELOG.md`
3. 提交代码
4. 在 GitHub 创建新 Release
5. GitHub Actions 会自动发布到 PyPI

---

**准备好了吗？我可以帮你生成完整的脚本来自动完成这些步骤！**
