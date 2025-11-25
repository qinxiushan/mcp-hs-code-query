# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-25

### Added
- Initial release of MCP HS Code Query Server
- Intelligent HS code queries with Chinese word segmentation
- Fuzzy matching algorithm using rapidfuzz
- Batch query support for multiple products
- Query by HS code functionality
- Complete customs declaration information extraction:
  - HS code with automatic formatting
  - Product name and description
  - Declaration elements
  - Legal units (first and second)
  - Customs supervision conditions with details
  - Inspection and quarantine categories with details
- MCP protocol compatibility
- FastMCP framework integration
- Three MCP tools exposed:
  - `query_hs_code` - Single product query
  - `batch_query_hs_codes` - Batch queries
  - `query_by_code` - Query by HS code
- Automatic retry mechanism for network requests
- Request delay control to prevent rate limiting
- Comprehensive error handling and logging
- JSON data storage
- Published to PyPI for easy installation
- One-command deployment with uvx

### Documentation
- Complete README_MCP.md for users
- PUBLISH_GUIDE.md for publishing to PyPI
- QUICK_PUBLISH.md for quick reference
- API documentation
- Installation and usage examples
- Claude Desktop integration guide

### Infrastructure
- GitHub Actions workflow for automatic PyPI publishing
- MIT License
- .gitignore for Python projects
- pyproject.toml with full metadata
- MANIFEST.in for package distribution

## [Unreleased]

### Planned
- Asynchronous query support
- Caching mechanism with Redis
- Excel import/export functionality
- Multiple data source aggregation
- WebSocket real-time updates
- GraphQL API support
- Web UI interface

---

## Version History Links

- [1.0.0] - https://github.com/YOUR_USERNAME/mcp-hs-code-query/releases/tag/v1.0.0
