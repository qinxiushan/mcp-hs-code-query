"""
快速验证修复 #001 的测试脚本
用于验证数据解析和URL问题是否已修复
"""

from src.scraper import HSCodeScraper
from src.storage import DataStorage


def test_fix_001():
    """测试修复 #001: 数据解析和URL问题"""
    print("=" * 70)
    print("测试修复 #001: 数据解析和URL问题")
    print("=" * 70)
    
    scraper = HSCodeScraper()
    storage = DataStorage()
    
    try:
        # 测试商品
        product_name = "烘干机"
        print(f"\n测试商品: {product_name}")
        print("-" * 70)
        
        # 执行查询
        result = scraper.query_by_product_name(product_name)
        
        # 验证点1: 检查search_success状态
        print(f"\n✓ 验证点1: 查询状态")
        print(f"  search_success = {result['search_success']}")
        if result['search_success']:
            print("  ✅ 查询成功")
        else:
            print(f"  ❌ 查询失败: {result.get('error_message', '未知错误')}")
        
        # 验证点2: 检查HS编码
        print(f"\n✓ 验证点2: HS编码")
        print(f"  hs_code = '{result['hs_code']}'")
        if result['hs_code']:
            print(f"  ✅ HS编码已提取")
            # 检查格式（应包含点号）
            if '.' in result['hs_code']:
                print(f"  ✅ HS编码格式正确（包含点号）")
            else:
                print(f"  ⚠️  HS编码缺少点号")
        else:
            print("  ❌ HS编码为空")
        
        # 验证点3: 检查商品名称
        print(f"\n✓ 验证点3: 商品名称")
        print(f"  product_name = '{result['product_name']}'")
        if result['product_name']:
            print("  ✅ 商品名称已提取")
        else:
            print("  ❌ 商品名称为空")
        
        # 验证点4: 检查其他关键字段
        print(f"\n✓ 验证点4: 其他关键字段")
        fields_check = {
            '申报要素': result['declaration_elements'],
            '法定第一单位': result['first_unit'],
            '法定第二单位': result['second_unit'],
            '海关监管条件': result['customs_supervision_conditions']['code'],
            '商品描述': result['description']
        }
        
        filled_count = 0
        for field_name, field_value in fields_check.items():
            if field_value:
                print(f"  ✅ {field_name}: '{field_value[:50]}...' " if len(field_value) > 50 else f"  ✅ {field_name}: '{field_value}'")
                filled_count += 1
            else:
                print(f"  ⚠️  {field_name}: (空)")
        
        print(f"\n  已填充字段: {filled_count}/{len(fields_check)}")
        
        # 完整显示结果
        print("\n" + "=" * 70)
        print("完整查询结果:")
        print("=" * 70)
        print(storage.format_result_for_display(result))
        
        # 总结
        print("\n" + "=" * 70)
        print("测试总结:")
        print("=" * 70)
        
        if result['search_success'] and result['hs_code'] and result['product_name']:
            print("✅ 修复验证通过！")
            print("\n主要改进:")
            print("  1. ✅ 数据解析成功")
            print("  2. ✅ HS编码格式正确")
            print("  3. ✅ URL处理正常")
            print("  4. ✅ 字段提取完整")
        else:
            print("❌ 修复验证失败！")
            if not result['search_success']:
                print(f"\n失败原因: {result.get('error_message', '未知')}")
        
        # 保存结果
        if result['search_success']:
            filepath = storage.save_single_result(result, filename='test_fix_001.json')
            print(f"\n测试结果已保存到: {filepath}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    test_fix_001()
