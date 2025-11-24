# HS编码查询工具 - 更新日志

所有重要的修改都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，  
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [未发布]

### 计划中
- [ ] 添加Excel导出功能
- [ ] 支持代理池
- [ ] 实现并发查询
- [ ] 添加数据缓存机制
- [ ] 支持多网站聚合查询

---

## [1.0.1] - 2025-11-24

### 🐛 修复

#### 数据解析失败问题
- **问题**: 详情页数据解析返回空值
- **原因**: 原有解析方法不够健壮，无法处理空数据页面
- **修复**: 改用表格遍历方式，构建键值对字典进行数据提取
- **文档**: [CHANGELOG_001](./CHANGELOG_001_修复数据解析和URL问题.md)

#### URL重复问题
- **问题**: 生成的详情页URL出现域名重复
  ```
  https://www.i5a6.com//www.i5a6.com/hscode/detail/8419399020#sbsl
  ```
- **原因**: 未正确处理绝对路径和相对路径
- **修复**: 添加URL清理逻辑，移除锚点和查询参数
- **文档**: [CHANGELOG_001](./CHANGELOG_001_修复数据解析和URL问题.md)

#### 搜索结果提取不准确
- **问题**: 商品名称提取为"1条"而非实际名称
- **原因**: 提取的是链接文本而非商品名称
- **修复**: 优先使用链接href提取HS编码，改进名称提取逻辑
- **文档**: [CHANGELOG_001](./CHANGELOG_001_修复数据解析和URL问题.md)

### ✨ 改进

#### 数据验证机制
- 添加解析成功判断逻辑
- 至少要有HS编码或商品名称才标记为成功
- 提供明确的错误信息

#### HS编码格式化
- 自动为10位HS编码添加点号格式化
- 支持8位和10位HS编码的自动识别
- 示例: `8419399020` → `84193990.20`

### 📝 文档

#### 新增文档
- 创建 `docs/` 目录用于存放所有修改文档
- 添加 `CHANGELOG_001_修复数据解析和URL问题.md`
- 添加 `docs/README.md` 文档索引
- 添加 `docs/TEMPLATE.md` 文档模板

#### 代码注释
- 在 `src/parser.py` 中添加修改历史引用
- 关联具体的文档编号

### 🔧 技术细节

**修改的文件**:
- `src/parser.py` - 主要修改

**修改的方法**:
- `parse_search_results()` - 搜索结果解析
- `parse_detail_page()` - 详情页数据解析

**影响的功能**:
- ✅ 单个商品查询准确性提升
- ✅ 批量查询稳定性提升
- ✅ 错误处理更完善

---

## [1.0.0] - 2025-11-24

### ✨ 新功能

#### 核心功能
- ✅ 智能搜索系统（中文分词+多关键词尝试）
- ✅ 完整数据提取（HS编码、申报要素、监管条件等）
- ✅ 单个查询和批量查询
- ✅ 从文件批量查询
- ✅ 根据HS编码直接查询
- ✅ JSON格式输出

#### 智能特性
- ✅ 自动中文分词（jieba）
- ✅ 相似度匹配算法
- ✅ 自动重试机制
- ✅ 请求延迟控制

#### 数据提取
完整提取以下字段：
- HS商品编码
- 商品名称
- 申报要素
- 法定第一单位
- 法定第二单位
- 海关监管条件（代码+详情）
- 检验检疫类别（代码+详情）
- 商品描述

#### 技术实现
- 模块化设计（scraper, parser, optimizer, storage, utils）
- 装饰器模式实现重试机制
- 日志系统（文件+控制台）
- 灵活的配置系统

### 📁 项目结构
```
data_search/
├── config/          # 配置模块
├── src/            # 源代码
├── data/           # 数据目录
├── logs/           # 日志目录
├── docs/           # 文档目录 (v1.0.1新增)
├── main.py         # 主程序
└── test_example.py # 测试示例
```

### 📚 文档
- README.md - 完整说明文档
- QUICK_START.md - 快速开始指南
- PROJECT_SUMMARY.md - 项目技术总结
- INSTALL.md - 安装使用指南
- requirements.txt - 依赖列表

### 🎯 使用方式

#### 命令行
```bash
# 单个查询
python main.py -s "商品名称"

# 批量查询
python main.py -b "商品1" "商品2" "商品3"

# 从文件查询
python main.py -f data/input/products.txt
```

#### Python API
```python
from src.scraper import HSCodeScraper
from src.storage import DataStorage

scraper = HSCodeScraper()
result = scraper.query_by_product_name("商品名称")
storage = DataStorage()
storage.save_single_result(result)
scraper.close()
```

---

## 版本说明

### 版本号规则
- **主版本号**: 重大架构变更或不兼容的API修改
- **次版本号**: 新功能添加，向后兼容
- **修订号**: Bug修复和小改进

### 修改类型标识
- ✨ `新功能` - 新增功能
- 🐛 `修复` - Bug修复
- 📝 `文档` - 文档更新
- ♻️ `重构` - 代码重构
- ⚡ `性能` - 性能优化
- 🔧 `配置` - 配置变更
- 🔒 `安全` - 安全性修复
- 🎨 `样式` - 代码格式、注释等
- 🧪 `测试` - 测试相关

---

## 链接

- [项目首页](../README.md)
- [问题追踪](https://github.com/your-repo/issues) (如有)
- [详细文档](./README.md)

---

**维护者**: 开发团队  
**最后更新**: 2025-11-24
