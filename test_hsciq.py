"""
测试 HSCIQ 网站爬虫
验证 scraper_hsciq.py 和 parser_hsciq.py 的功能
"""

import sys
from src.scraper_hsciq import HSCodeScraperHSCIQ
from src.storage import DataStorage
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_single_query():
    """测试单个商品查询"""
    print("\n" + "="*60)
    print("测试1: 单个商品查询")
    print("="*60)
    
    scraper = HSCodeScraperHSCIQ()
    storage = DataStorage()
    
    # 测试商品
    product_name = "笔记本电脑"
    
    print(f"\n查询商品: {product_name}")
    result = scraper.query_by_product_name(product_name)
    
    # 显示结果
    print("\n查询结果:")
    print(storage.format_result_for_display(result))
    
    # 保存结果
    if result.get('search_success'):
        filename = storage.save_single_result(result)
        print(f"\n结果已保存到: {filename}")
    
    scraper.close()
    return result


def test_query_by_hs_code():
    """测试根据HS编码查询"""
    print("\n" + "="*60)
    print("测试2: 根据HS编码查询")
    print("="*60)
    
    scraper = HSCodeScraperHSCIQ()
    storage = DataStorage()
    
    # 测试HS编码 (从页面快照中获取的真实编码)
    hs_code = "0808100000"
    
    print(f"\n查询HS编码: {hs_code}")
    result = scraper.query_by_hs_code(hs_code)
    
    # 显示结果
    print("\n查询结果:")
    print(storage.format_result_for_display(result))
    
    scraper.close()
    return result


def test_batch_query():
    """测试批量查询"""
    print("\n" + "="*60)
    print("测试3: 批量查询")
    print("="*60)
    
    scraper = HSCodeScraperHSCIQ()
    storage = DataStorage()
    
    # 测试商品列表
    products = ["防白蚁耐候木油", "室内乳胶漆", "冰箱"]
    
    print(f"\n批量查询商品: {products}")
    results = scraper.batch_query(products)
    
    # 显示结果摘要
    print(f"\n查询完成: {len(results)} 个商品")
    for i, result in enumerate(results, 1):
        success = result.get('search_success', False)
        status = "✓" if success else "✗"
        product = result.get('query_product_name', '')
        hs_code = result.get('hs_code', '无')
        print(f"{status} {i}. {product}: {hs_code}")
    
    # 保存结果
    filename = storage.save_batch_results(results)
    print(f"\n批量结果已保存到: {filename}")
    
    scraper.close()
    return results


def test_batch_query_from_file():
    """测试从文件读取批量查询"""
    print("\n" + "="*60)
    print("测试4: 从文件批量查询")
    print("="*60)
    
    import os
    
    scraper = HSCodeScraperHSCIQ()
    storage = DataStorage()
    
    # 文件路径
    input_file = "data/input/products.txt"
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"\n错误: 文件不存在 - {input_file}")
        print("请确保 data/input/products.txt 文件存在")
        scraper.close()
        return None
    
    print(f"\n读取文件: {input_file}")
    
    # 读取商品列表
    products = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # 跳过空行和注释
                    products.append(line)
        
        print(f"成功读取 {len(products)} 个商品")
        print("\n商品列表预览 (前10个):")
        for i, product in enumerate(products[:10], 1):
            print(f"  {i}. {product}")
        if len(products) > 10:
            print(f"  ... 还有 {len(products) - 10} 个商品")
        
    except Exception as e:
        print(f"\n读取文件失败: {e}")
        scraper.close()
        return None
    
    # 确认是否继续
    print(f"\n准备查询 {len(products)} 个商品")
    user_input = input("是否继续? (y/n): ").strip().lower()
    
    if user_input != 'y':
        print("已取消批量查询")
        scraper.close()
        return None
    
    # 批量查询
    print("\n开始批量查询...")
    results = scraper.batch_query(products)
    
    # 统计结果
    success_count = sum(1 for r in results if r.get('search_success', False))
    failed_count = len(results) - success_count
    
    print(f"\n查询完成:")
    print(f"  总数: {len(results)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {failed_count}")
    print(f"  成功率: {success_count/len(results)*100:.1f}%")
    
    # 显示结果摘要
    print("\n详细结果:")
    for i, result in enumerate(results, 1):
        success = result.get('search_success', False)
        status = "✓" if success else "✗"
        product = result.get('query_product_name', '')
        hs_code = result.get('hs_code', '无')
        product_name = result.get('product_name', '')
        
        # 截断显示
        display_query = product[:30] + '...' if len(product) > 30 else product
        display_name = product_name[:30] + '...' if len(product_name) > 30 else product_name
        
        if success:
            print(f"{status} {i:3d}. {display_query:35s} -> {hs_code:15s} {display_name}")
        else:
            error_msg = result.get('error_message', '未知错误')[:40]
            print(f"{status} {i:3d}. {display_query:35s} -> 失败: {error_msg}")
    
    # 保存结果
    filename = storage.save_batch_results(results)
    print(f"\n批量结果已保存到: {filename}")
    
    # 显示失败的商品
    if failed_count > 0:
        print(f"\n失败的商品 ({failed_count}个):")
        for i, result in enumerate(results, 1):
            if not result.get('search_success', False):
                product = result.get('query_product_name', '')
                error_msg = result.get('error_message', '未知错误')
                print(f"  {i}. {product}")
                print(f"     错误: {error_msg}")
    
    scraper.close()
    return results


def main():
    """主测试函数"""
    print("="*60)
    print("HSCIQ 网站爬虫测试")
    print("="*60)
    
    # 显示测试菜单
    print("\n请选择测试类型:")
    print("  1. 单个商品查询")
    print("  2. 根据HS编码查询")
    print("  3. 批量查询 (3个商品)")
    print("  4. 从文件批量查询 (data/input/products.txt)")
    print("  5. 运行所有测试 (1-3)")
    print("  0. 退出")
    
    try:
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == '1':
            test_single_query()
        elif choice == '2':
            test_query_by_hs_code()
        elif choice == '3':
            test_batch_query()
        elif choice == '4':
            test_batch_query_from_file()
        elif choice == '5':
            # 运行所有基础测试
            test_single_query()
            test_query_by_hs_code()
            test_batch_query()
        elif choice == '0':
            print("退出测试")
            return
        else:
            print(f"无效的选项: {choice}")
            return
        
        print("\n" + "="*60)
        print("测试完成!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}", exc_info=True)
        print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
