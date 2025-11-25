"""MCP Server for HS Code Queries - 智能海关HS编码查询MCP服务器

此服务提供以下工具:
1. query_hs_code - 根据商品名称查询HS编码
2. batch_query_hs_codes - 批量查询多个商品的HS编码
3. query_by_code - 根据HS编码查询详情
"""

import sys
import os
from typing import Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
import mcp.types as types
from src.scraper import HSCodeScraper
from src.storage import DataStorage

# 创建 FastMCP 服务器实例
mcp = FastMCP("hs-code-query")

# 全局实例
scraper = None
storage = DataStorage()


def get_scraper() -> HSCodeScraper:
    """获取scraper实例（延迟初始化）"""
    global scraper
    if scraper is None:
        scraper = HSCodeScraper()
    return scraper


@mcp.tool()
def query_hs_code(product_name: str) -> dict[str, Any]:
    """根据商品名称查询HS编码及完整申报信息
    
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
            "search_success": true
        }
    """
    try:
        result = get_scraper().query_by_product_name(product_name)
        return result
    except Exception as e:
        return {
            "search_success": False,
            "error_message": f"查询失败: {str(e)}",
            "product_name": product_name
        }


@mcp.tool()
def batch_query_hs_codes(product_names: list[str]) -> dict[str, Any]:
    """批量查询多个商品的HS编码
    
    Args:
        product_names: 商品名称列表，例如：["苹果", "香蕉", "橙子"]
        
    Returns:
        包含以下字段的字典：
        - total: 总查询数量
        - successful: 成功查询数量
        - failed: 失败查询数量
        - results: 查询结果列表（每个结果格式同 query_hs_code）
        
    Example:
        >>> batch_query_hs_codes(["苹果", "香蕉"])
        {
            "total": 2,
            "successful": 2,
            "failed": 0,
            "results": [
                {"hs_code": "08081000.00", "product_name": "鲜苹果", ...},
                {"hs_code": "08030012.00", "product_name": "鲜香蕉", ...}
            ]
        }
    """
    try:
        results = get_scraper().batch_query(product_names)
        successful = sum(1 for r in results if r.get('search_success', False))
        failed = len(results) - successful
        
        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    except Exception as e:
        return {
            "total": len(product_names),
            "successful": 0,
            "failed": len(product_names),
            "error_message": f"批量查询失败: {str(e)}",
            "results": []
        }


@mcp.tool()
def query_by_code(hs_code: str) -> dict[str, Any]:
    """根据已知的HS编码查询详细信息
    
    Args:
        hs_code: HS编码，例如："08081000.00" 或 "8081000"
        
    Returns:
        包含完整HS编码信息的字典（格式同 query_hs_code）
        
    Example:
        >>> query_by_code("08081000.00")
        {
            "hs_code": "08081000.00",
            "product_name": "鲜苹果",
            "description": "鲜苹果",
            ...
        }
    """
    try:
        result = get_scraper().query_by_hs_code(hs_code)
        return result
    except Exception as e:
        return {
            "search_success": False,
            "error_message": f"查询失败: {str(e)}",
            "hs_code": hs_code
        }


if __name__ == "__main__":
    # 使用stdio传输（MCP标准）
    try:
        mcp.run(transport="stdio")
    finally:
        # 清理资源
        if scraper is not None:
            scraper.close()
