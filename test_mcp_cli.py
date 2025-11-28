"""
MCP 服务器命令行测试工具
用于在命令行直接测试 MCP 服务器功能（不需要 Claude Desktop）
"""

import sys
import argparse
from mcp_hs_code_query.server import (
    query_hs_code,
    batch_query_hs_codes,
    query_by_code,
    get_query_stats
)
import json


def print_result(result, title="查询结果"):
    """格式化打印结果"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("="*60)


def cmd_query(args):
    """查询商品"""
    print(f"\n🔍 查询商品: {args.product_name}")
    result = query_hs_code(args.product_name)
    print_result(result)
    
    # 显示关键信息
    if result.get('search_success'):
        print(f"\n✅ 查询成功!")
        print(f"   HS编码: {result.get('hs_code')}")
        print(f"   商品名称: {result.get('product_name')}")
        print(f"   数据来源: {result.get('data_source')}")
        print(f"   查询方式: {result.get('query_method')}")
    else:
        print(f"\n❌ 查询失败: {result.get('error_message')}")


def cmd_batch(args):
    """批量查询"""
    products = args.products
    print(f"\n🔍 批量查询 {len(products)} 个商品:")
    for i, p in enumerate(products, 1):
        print(f"   {i}. {p}")
    
    result = batch_query_hs_codes(products)
    print_result(result, "批量查询结果")
    
    # 显示统计
    print(f"\n📊 统计信息:")
    print(f"   总数: {result.get('total')}")
    print(f"   成功: {result.get('successful')}")
    print(f"   失败: {result.get('failed')}")
    print(f"   主数据源: {result.get('primary_count')}")
    print(f"   备用数据源: {result.get('fallback_count')}")


def cmd_code(args):
    """按HS编码查询"""
    print(f"\n🔍 查询HS编码: {args.hs_code}")
    result = query_by_code(args.hs_code)
    print_result(result)
    
    if result.get('search_success'):
        print(f"\n✅ 查询成功!")
        print(f"   商品名称: {result.get('product_name')}")
        print(f"   数据来源: {result.get('data_source')}")


def cmd_stats(args):
    """查询统计"""
    print("\n📊 查询统计信息:")
    result = get_query_stats()
    print_result(result, "统计信息")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='MCP HS Code Query Server - 命令行测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询单个商品
  python test_mcp_cli.py query 苹果
  
  # 批量查询
  python test_mcp_cli.py batch 苹果 香蕉 橙子
  
  # 按HS编码查询
  python test_mcp_cli.py code 0808100000
  
  # 查看统计
  python test_mcp_cli.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # query 命令
    parser_query = subparsers.add_parser('query', help='查询商品HS编码')
    parser_query.add_argument('product_name', help='商品名称')
    parser_query.set_defaults(func=cmd_query)
    
    # batch 命令
    parser_batch = subparsers.add_parser('batch', help='批量查询')
    parser_batch.add_argument('products', nargs='+', help='商品名称列表')
    parser_batch.set_defaults(func=cmd_batch)
    
    # code 命令
    parser_code = subparsers.add_parser('code', help='按HS编码查询')
    parser_code.add_argument('hs_code', help='HS编码')
    parser_code.set_defaults(func=cmd_code)
    
    # stats 命令
    parser_stats = subparsers.add_parser('stats', help='查看统计信息')
    parser_stats.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
