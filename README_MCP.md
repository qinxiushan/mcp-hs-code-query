# MCP HS Code Query Server

> 🚀 智能海关HS编码查询MCP服务器 - 支持通过uvx一键部署

[![PyPI version](https://badge.fury.io/py/mcp-hs-code-query.svg)](https://pypi.org/project/mcp-hs-code-query/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Downloads](https://pepy.tech/badge/mcp-hs-code-query)](https://pepy.tech/project/mcp-hs-code-query)

## 📖 简介

基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的智能海关HS编码查询服务，支持AI智能体平台（Claude Desktop、ChatGPT等）通过 `uvx` 快速部署和调用。

### ✨ 核心特性

- ✅ **智能查询**: 中文分词 + 相似度匹配 + 自动选择最佳结果
- ✅ **完整数据**: HS编码、申报要素、监管条件、检验检疫等完整信息
- ✅ **批量支持**: 一次查询多个商品
- ✅ **MCP标准**: 符合Model Context Protocol规范
- ✅ **一键部署**: 使用 `uvx` 零配置启动
- ✅ **AI就绪**: 可被Claude Desktop、ChatGPT等AI平台调用

## 🚀 快速开始

### 方式1: 使用 uvx（推荐）

最简单的使用方式，无需安装：

```bash
# 直接运行（uvx会自动下载和运行）
uvx mcp-hs-code-query

# 或者从本地运行
uvx --from . mcp-hs-code-query
```

### 方式2: 安装后使用

```bash
# 克隆仓库
git clone <repository-url>
cd data_search

# 安装依赖（使用uv）
uv pip install -e .

# 运行服务器
uv run mcp-hs-code-query
```

### 方式3: 在Claude Desktop中配置

编辑 Claude Desktop 配置文件:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加以下配置：

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

或者从本地路径运行：

```json
{
  "mcpServers": {
    "hs-code-query": {
      "command": "uvx",
      "args": [
        "--from",
        "c:\\Users\\dela1\\Desktop\\data_search",
        "mcp-hs-code-query"
      ]
    }
  }
}
```

重启 Claude Desktop 后即可使用！

## 🛠️ 提供的工具

### 1. query_hs_code

根据商品名称查询HS编码及完整申报信息。

**参数**:
- `product_name` (string): 商品名称（中文）

**返回**: 包含HS编码、申报要素、监管条件等完整信息的字典

**示例**:
```python
query_hs_code(product_name="苹果")
# 返回:
{
  "hs_code": "08081000.00",
  "product_name": "鲜苹果",
  "description": "鲜苹果",
  "declaration_elements": "1:品名;2:品牌类型;3:出口享惠情况;...",
  "first_unit": "千克",
  "second_unit": "无",
  "customs_supervision_conditions": {...},
  "inspection_quarantine": {...},
  "search_success": true
}
```

### 2. batch_query_hs_codes

批量查询多个商品的HS编码。

**参数**:
- `product_names` (array): 商品名称列表

**返回**: 包含查询统计和所有结果的字典

**示例**:
```python
batch_query_hs_codes(product_names=["苹果", "香蕉", "橙子"])
# 返回:
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [...]
}
```

### 3. query_by_code

根据已知HS编码查询详细信息。

**参数**:
- `hs_code` (string): HS编码

**示例**:
```python
query_by_code(hs_code="08081000.00")
```

## 📋 在AI助手中使用

配置完成后，你可以在Claude Desktop中这样使用：

**示例对话**:

> **用户**: 帮我查询"苹果"的HS编码
> 
> **Claude**: 我来帮你查询... [调用 query_hs_code 工具]
> 
> 查询结果：
> - HS编码：08081000.00
> - 商品名称：鲜苹果
> - 申报要素：1:品名;2:品牌类型;3:出口享惠情况;...
> - 监管条件：AB（入境/出境货物通关单）
> - ...

> **用户**: 批量查询"苹果、香蕉、橙子"的HS编码
> 
> **Claude**: [调用 batch_query_hs_codes 工具]
> 
> 已查询3个商品，全部成功！
> 1. 苹果 - 08081000.00
> 2. 香蕉 - 08030012.00
> 3. 橙子 - 08051000.10

## 🔧 开发和测试

### 使用MCP Inspector测试

```bash
# 启动Inspector进行交互式测试
uv run mcp dev mcp_hs_code_query/server.py
```

### 单元测试

```bash
# 运行测试
uv run pytest tests/
```

### 调试

在VS Code中配置 `.vscode/mcp.json`:

```json
{
  "servers": {
    "hs-code-query": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "mcp-hs-code-query"]
    }
  }
}
```

## 📦 依赖

核心依赖：
- `mcp>=1.0.0` - Model Context Protocol SDK
- `requests>=2.31.0` - HTTP请求
- `beautifulsoup4>=4.12.0` - HTML解析
- `lxml>=4.9.3` - XML/HTML处理
- `jieba>=0.42.1` - 中文分词
- `rapidfuzz>=3.0.0` - 相似度匹配

所有依赖在 `pyproject.toml` 中定义。

## 🏗️ 项目结构

```
data_search/
├── mcp_hs_code_query/        # MCP服务器包
│   ├── __init__.py           # 包初始化
│   ├── __main__.py           # 命令行入口
│   └── server.py             # MCP服务器实现
├── src/                      # 核心业务逻辑
│   ├── scraper.py           # 爬虫引擎
│   ├── parser.py            # HTML解析
│   ├── search_optimizer.py # 搜索优化
│   ├── storage.py           # 数据存储
│   └── utils.py             # 工具函数
├── config/                   # 配置文件
│   └── settings.py
├── pyproject.toml           # 项目配置和依赖
└── README_MCP.md            # 本文档
```

## 🌐 与REST API的区别

| 特性 | MCP服务器 | REST API |
|------|-----------|----------|
| 使用场景 | AI智能体集成 | Web应用、微服务 |
| 通信方式 | stdio / SSE | HTTP |
| 部署方式 | uvx一键启动 | 需要Web服务器 |
| 调用方式 | AI自动调用 | 手动HTTP请求 |
| 文档 | 自动生成 | 需要编写 |

**两者可以共存！** 你可以同时提供MCP服务和REST API，满足不同场景的需求。

## 🔐 安全性

- ✅ 请求延迟控制（避免过载）
- ✅ 重试机制（网络容错）
- ✅ 错误处理（详细日志）
- ⚠️ 建议在生产环境中添加速率限制
- ⚠️ 建议配置代理池（避免IP封禁）

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📚 相关文档

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP 集成](https://docs.claude.com/en/docs/claude-code/mcp)
- [项目完整文档](README.md)
- [REST API 文档](API_README.md)

## 💡 常见问题

### Q: 如何在ChatGPT中使用？

A: ChatGPT目前不直接支持MCP，但你可以使用REST API（见 API_README.md）

### Q: 如何提高查询速度？

A: 1) 使用批量查询 2) 添加缓存机制 3) 使用代理池

### Q: 如何自定义目标网站？

A: 修改 `config/settings.py` 中的 `BASE_URL`

### Q: 如何调试MCP服务器？

A: 使用 `uv run mcp dev` 或在VS Code中配置断点调试

---

**维护者**: HS Code Query Team  
**最后更新**: 2025-11-25
