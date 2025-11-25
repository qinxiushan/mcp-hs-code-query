"""
快速测试示例
演示如何使用HS编码查询工具
"""

from src.scraper import HSCodeScraper
from src.storage import DataStorage


def test_single_query():
    """测试单个查询"""
    print("=" * 60)
    print("测试单个商品查询")
    print("=" * 60)
    
    scraper = HSCodeScraper()
    storage = DataStorage()
    
    try:
        # 查询商品
        product_name = "烘干机"
        print(f"\n查询商品: {product_name}")
        
        result = scraper.query_by_product_name(product_name)
        
        # 显示结果
        print(storage.format_result_for_display(result))
        
        # 保存结果
        if result['search_success']:
            filepath = storage.save_single_result(result)
            print(f"\n结果已保存到: {filepath}")
        
    finally:
        scraper.close()


def test_batch_query():
    """测试批量查询"""
    print("\n" + "=" * 60)
    print("测试批量商品查询")
    print("=" * 60)
    
    scraper = HSCodeScraper()
    storage = DataStorage()
    
    try:
        # 批量查询
        products = ["苹果手机", "笔记本电脑", "T恤"]
        print(f"\n查询商品列表: {products}")
        
        results = scraper.batch_query(products)
        
        # 统计
        success = sum(1 for r in results if r['search_success'])
        print(f"\n查询完成: 成功 {success}/{len(results)}")
        
        # 保存结果
        filepath = storage.save_batch_results(results)
        print(f"结果已保存到: {filepath}")
        
    finally:
        scraper.close()


def test_hs_code_query():
    """测试根据HS编码查询"""
    print("\n" + "=" * 60)
    print("测试根据HS编码直接查询")
    print("=" * 60)
    
    scraper = HSCodeScraper()
    storage = DataStorage()
    
    try:
        # 根据HS编码查询
        hs_code = "84193990.20"
        print(f"\n查询HS编码: {hs_code}")
        
        result = scraper.query_by_hs_code(hs_code)
        
        # 显示结果
        print(storage.format_result_for_display(result))
        
    finally:
        scraper.close()


if __name__ == "__main__":
    # 运行测试
    print("开始测试HS编码查询工具\n")
    
    # 选择要运行的测试
    print("请选择测试:")
    print("1. 单个查询测试")
    print("2. 批量查询测试")
    print("3. HS编码查询测试")
    print("4. 运行所有测试")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        test_single_query()
    elif choice == "2":
        test_batch_query()
    elif choice == "3":
        test_hs_code_query()
    elif choice == "4":
        test_single_query()
        test_batch_query()
        test_hs_code_query()
    else:
        print("无效选项")
    
    print("\n测试完成!")
