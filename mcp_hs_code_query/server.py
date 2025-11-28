"""MCP Server for HS Code Queries - 智能海关HS编码查询MCP服务器

此服务提供以下工具:
1. query_hs_code - 根据商品名称查询HS编码 (支持双数据源主备模式)
2. batch_query_hs_codes - 批量查询多个商品的HS编码
3. query_by_code - 根据HS编码查询详情
4. get_query_stats - 获取查询统计信息

数据源策略:
- 主数据源: hsciq.com (支持嵌入向量相似度匹配,准确度更高)
- 备用数据源: i5a6.com (主数据源失败时自动切换)
"""

import sys
import os
from typing import Any
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
import mcp.types as types
from src.scraper import HSCodeScraper  # i5a6.com 爬虫
from src.scraper_hsciq import HSCodeScraperHSCIQ  # hsciq.com 爬虫
from src.storage import DataStorage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastMCP 服务器实例
mcp = FastMCP("hs-code-query")

# 全局实例 - 双爬虫主备模式
scraper_primary = None    # 主爬虫 (HSCIQ)
scraper_fallback = None   # 备用爬虫 (i5a6)
storage = DataStorage()

# 查询统计
query_stats = {
    'total_queries': 0,
    'primary_success': 0,
    'fallback_success': 0,
    'total_failures': 0,
    'primary_source': 'hsciq.com',
    'fallback_source': 'i5a6.com'
}


def get_primary_scraper() -> HSCodeScraperHSCIQ:
    """获取主爬虫实例（延迟初始化）"""
    global scraper_primary
    if scraper_primary is None:
        logger.info("初始化主数据源爬虫: hsciq.com")
        scraper_primary = HSCodeScraperHSCIQ()
    return scraper_primary


def get_fallback_scraper() -> HSCodeScraper:
    """获取备用爬虫实例（延迟初始化）"""
    global scraper_fallback
    if scraper_fallback is None:
        logger.info("初始化备用数据源爬虫: i5a6.com")
        scraper_fallback = HSCodeScraper()
    return scraper_fallback


def query_with_fallback(query_func_name: str, *args, **kwargs) -> dict[str, Any]:
    """
    主备模式查询函数
    
    Args:
        query_func_name: 查询方法名称 (如 'query_by_product_name')
        *args, **kwargs: 传递给查询方法的参数
        
    Returns:
        查询结果，包含 data_source 和 query_method 字段
    """
    global query_stats
    query_stats['total_queries'] += 1
    
    # 尝试主数据源 (HSCIQ)
    try:
        logger.info(f"使用主数据源查询: {query_func_name}({args}, {kwargs})")
        primary_scraper = get_primary_scraper()
        query_method = getattr(primary_scraper, query_func_name)
        result = query_method(*args, **kwargs)
        
        if result.get('search_success', False):
            # 主数据源成功
            query_stats['primary_success'] += 1
            result['data_source'] = 'hsciq.com'
            result['query_method'] = 'primary'
            logger.info(f"主数据源查询成功")
            return result
        else:
            logger.warning(f"主数据源查询失败: {result.get('error_message', '未知错误')}")
    
    except Exception as e:
        logger.error(f"主数据源查询异常: {e}", exc_info=True)
    
    # 主数据源失败，尝试备用数据源 (i5a6)
    try:
        logger.info(f"切换到备用数据源查询")
        fallback_scraper = get_fallback_scraper()
        query_method = getattr(fallback_scraper, query_func_name)
        result = query_method(*args, **kwargs)
        
        if result.get('search_success', False):
            # 备用数据源成功
            query_stats['fallback_success'] += 1
            result['data_source'] = 'i5a6.com'
            result['query_method'] = 'fallback'
            logger.info(f"备用数据源查询成功")
            return result
        else:
            logger.warning(f"备用数据源查询失败: {result.get('error_message', '未知错误')}")
            query_stats['total_failures'] += 1
            result['data_source'] = 'none'
            result['query_method'] = 'failed'
            return result
    
    except Exception as e:
        logger.error(f"备用数据源查询异常: {e}", exc_info=True)
        query_stats['total_failures'] += 1
        return {
            'search_success': False,
            'error_message': f"所有数据源查询失败: 主={str(e)}",
            'data_source': 'none',
            'query_method': 'failed'
        }


@mcp.tool()
def query_hs_code(product_name: str) -> dict[str, Any]:
    """根据商品名称查询HS编码及完整申报信息（支持主备数据源自动切换）
    
    查询策略:
    1. 优先使用主数据源 hsciq.com (支持嵌入向量相似度,准确度更高)
    2. 主数据源失败时自动切换到备用数据源 i5a6.com
    3. 返回结果包含 data_source 和 query_method 字段标识数据来源
    
    Args:
        product_name: 商品名称（中文），例如："苹果"、"笔记本电脑"、"棉质T恤"
        
    Returns:
        包含以下字段的字典：
        - hs_code: HS商品编码
        - product_name: 官方商品名称
        - description: 商品描述
        - declaration_elements: 申报要素
        - first_unit: 法定第一单位
        - second_unit: 法定第二单位
        - customs_supervision_conditions: 海关监管条件（代码和详情）
        - inspection_quarantine: 检验检疫类别（代码和详情）
        - search_success: 查询是否成功
        - error_message: 错误信息（如果失败）
        - data_source: 数据来源 (hsciq.com/i5a6.com/none)
        - query_method: 查询方式 (primary/fallback/failed)
        
    Example:
        >>> query_hs_code("苹果")
        {
            "hs_code": "08081000.00",
            "product_name": "鲜苹果",
            "description": "鲜苹果",
            "declaration_elements": "1:品名;2:品牌类型;3:出口享惠情况;...",
            "first_unit": "千克",
            "second_unit": "无",
            "customs_supervision_conditions": {
                "code": "AB",
                "details": [...]
            },
            "inspection_quarantine": {
                "code": "PQ",
                "details": [...]
            },
            "search_success": true,
            "data_source": "hsciq.com",
            "query_method": "primary"
        }
    """
    return query_with_fallback('query_by_product_name', product_name)


@mcp.tool()
def batch_query_hs_codes(product_names: list[str]) -> dict[str, Any]:
    """批量查询多个商品的HS编码（每个商品支持主备数据源自动切换）
    
    Args:
        product_names: 商品名称列表，例如：["苹果", "香蕉", "橙子"]
        
    Returns:
        包含以下字段的字典：
        - total: 总查询数量
        - successful: 成功查询数量
        - failed: 失败查询数量
        - primary_count: 主数据源成功数量
        - fallback_count: 备用数据源成功数量
        - results: 查询结果列表（每个结果包含 data_source 和 query_method）
        
    Example:
        >>> batch_query_hs_codes(["苹果", "香蕉"])
        {
            "total": 2,
            "successful": 2,
            "failed": 0,
            "primary_count": 2,
            "fallback_count": 0,
            "results": [
                {
                    "hs_code": "08081000.00", 
                    "product_name": "鲜苹果",
                    "data_source": "hsciq.com",
                    "query_method": "primary",
                    ...
                },
                {
                    "hs_code": "08030012.00", 
                    "product_name": "鲜香蕉",
                    "data_source": "hsciq.com",
                    "query_method": "primary",
                    ...
                }
            ]
        }
    """
    results = []
    for product_name in product_names:
        result = query_with_fallback('query_by_product_name', product_name)
        results.append(result)
    
    successful = sum(1 for r in results if r.get('search_success', False))
    failed = len(results) - successful
    primary_count = sum(1 for r in results if r.get('query_method') == 'primary')
    fallback_count = sum(1 for r in results if r.get('query_method') == 'fallback')
    
    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "primary_count": primary_count,
        "fallback_count": fallback_count,
        "results": results
    }


@mcp.tool()
def query_by_code(hs_code: str) -> dict[str, Any]:
    """根据已知的HS编码查询详细信息（支持主备数据源自动切换）
    
    Args:
        hs_code: HS编码，例如："08081000.00" 或 "0808100000"
        
    Returns:
        包含完整HS编码信息的字典（包含 data_source 和 query_method）
        
    Example:
        >>> query_by_code("08081000.00")
        {
            "hs_code": "08081000.00",
            "product_name": "鲜苹果",
            "description": "鲜苹果",
            "data_source": "hsciq.com",
            "query_method": "primary",
            ...
        }
    """
    return query_with_fallback('query_by_hs_code', hs_code)


@mcp.tool()
def get_query_stats() -> dict[str, Any]:
    """获取查询统计信息
    
    返回服务启动以来的查询统计数据，包括：
    - 总查询次数
    - 主数据源成功次数
    - 备用数据源成功次数
    - 总失败次数
    - 成功率
    - 主数据源成功率
    
    Returns:
        统计信息字典
        
    Example:
        >>> get_query_stats()
        {
            "total_queries": 100,
            "primary_success": 85,
            "fallback_success": 10,
            "total_failures": 5,
            "success_rate": 0.95,
            "primary_success_rate": 0.85,
            "primary_source": "hsciq.com",
            "fallback_source": "i5a6.com"
        }
    """
    total = query_stats['total_queries']
    success = query_stats['primary_success'] + query_stats['fallback_success']
    
    return {
        **query_stats,
        'success_rate': success / total if total > 0 else 0.0,
        'primary_success_rate': query_stats['primary_success'] / total if total > 0 else 0.0,
        'fallback_success_rate': query_stats['fallback_success'] / total if total > 0 else 0.0
    }


if __name__ == "__main__":
    # 使用stdio传输（MCP标准）
    try:
        logger.info("MCP HS Code Query Server 启动")
        logger.info("数据源策略: 主=hsciq.com, 备=i5a6.com")
        mcp.run(transport="stdio")
    finally:
        # 清理资源
        logger.info("清理资源...")
        if scraper_primary is not None:
            scraper_primary.close()
        if scraper_fallback is not None:
            scraper_fallback.close()
        logger.info("服务已停止")
