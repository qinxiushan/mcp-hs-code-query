# HS Code Query MCP Server - 测试脚本
# 用于在发布前测试 MCP 服务器功能

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_hs_code_query.server import query_hs_code, batch_query_hs_codes, query_by_code


def test_single_query():
    """测试单个查询"""
    print("=" * 60)
    print("测试1: 单个查询 - 苹果")
    print("=" * 60)
    
    result = query_hs_code("苹果")
    
    if result.get('search_success'):
        print(f"✅ 查询成功!")
        print(f"   HS编码: {result.get('hs_code')}")
        print(f"   商品名称: {result.get('product_name')}")
        print(f"   申报要素: {result.get('declaration_elements', '')[:50]}...")
    else:
        print(f"❌ 查询失败: {result.get('error_message')}")
    
    print()


def test_batch_query():
    """测试批量查询"""
    print("=" * 60)
    print("测试2: 批量查询 - 苹果, 香蕉")
    print("=" * 60)
    
    result = batch_query_hs_codes(["苹果", "香蕉"])
    
    print(f"总数: {result.get('total')}")
    print(f"成功: {result.get('successful')}")
    print(f"失败: {result.get('failed')}")
    
    for item in result.get('results', []):
        if item.get('search_success'):
            print(f"  ✅ {item.get('query_product_name', 'N/A')}: {item.get('hs_code')}")
        else:
            print(f"  ❌ {item.get('query_product_name', 'N/A')}: 查询失败")
    
    print()


def test_query_by_code():
    """测试按编码查询"""
    print("=" * 60)
    print("测试3: 按编码查询 - 08081000.00")
    print("=" * 60)
    
    result = query_by_code("08081000.00")
    
    if result.get('search_success'):
        print(f"✅ 查询成功!")
        print(f"   商品名称: {result.get('product_name')}")
        print(f"   描述: {result.get('description')}")
    else:
        print(f"❌ 查询失败: {result.get('error_message')}")
    
    print()


def main():
    """主测试函数"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║   MCP HS Code Query Server - 功能测试                 ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    try:
        test_single_query()
        test_batch_query()
        test_query_by_code()
        
        print("=" * 60)
        print("✅ 所有测试完成!")
        print("=" * 60)
        print()
        print("下一步:")
        print("1. 如果测试通过，可以运行 publish.bat 发布到 PyPI")
        print("2. 或运行 'python -m build' 构建包")
        print("3. 或运行 'uvx --from . mcp-hs-code-query' 测试 uvx")
        print()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
