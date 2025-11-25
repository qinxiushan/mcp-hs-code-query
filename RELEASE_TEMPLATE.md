# Release v1.0.0 - Initial Release

## 🎉 MCP HS Code Query Server 首次发布！

这是一个基于 Model Context Protocol (MCP) 的智能海关HS编码查询服务器，可以被 Claude Desktop、ChatGPT 等 AI 智能体调用。

---

## ✨ 核心功能

- ✅ **智能查询**: 中文分词 + 相似度匹配 + 自动选择最佳结果
- ✅ **完整数据**: HS编码、申报要素、监管条件、检验检疫等完整信息
- ✅ **批量支持**: 一次查询多个商品
- ✅ **MCP标准**: 符合Model Context Protocol规范
- ✅ **一键部署**: 使用 uvx 零配置启动
- ✅ **AI就绪**: 可被Claude Desktop、ChatGPT等AI平台调用

---

## 🚀 快速开始

### 使用 uvx（推荐）

```bash
uvx mcp-hs-code-query
```

### 在 Claude Desktop 中配置

编辑配置文件 `%APPDATA%\Claude\claude_desktop_config.json`:

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

重启 Claude Desktop 后即可使用！

### 使用 pip 安装

```bash
pip install mcp-hs-code-query
mcp-hs-code-query
```

---

## 🛠️ 提供的工具

### 1. query_hs_code
根据商品名称查询HS编码及完整申报信息

**示例**:
```
查询商品：苹果
返回：HS编码 08081000.00，申报要素，监管条件等
```

### 2. batch_query_hs_codes
批量查询多个商品

**示例**:
```
查询：["苹果", "香蕉", "橙子"]
返回：所有商品的完整信息
```

### 3. query_by_code
根据HS编码查询详细信息

**示例**:
```
查询：08081000.00
返回：商品名称、申报要素等详细信息
```

---

## 📦 安装的包

- 📦 **Wheel**: `mcp_hs_code_query-1.0.0-py3-none-any.whl`
- 📦 **Source**: `mcp_hs_code_query-1.0.0.tar.gz`

---

## 🔗 链接

- **PyPI**: https://pypi.org/project/mcp-hs-code-query/
- **文档**: 查看 [README_MCP.md](README_MCP.md)
- **问题反馈**: [Issues](https://github.com/YOUR_USERNAME/mcp-hs-code-query/issues)

---

## 📝 变更日志

完整变更日志请查看 [CHANGELOG.md](CHANGELOG.md)

---

## 🙏 致谢

感谢所有使用和支持本项目的用户！

---

**如有问题或建议，欢迎提交 Issue！**
