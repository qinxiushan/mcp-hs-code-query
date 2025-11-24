#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复 #002 验证脚本 - 测试改进后的相似度匹配算法

测试场景:
1. 查询词 "苹果" 应该能匹配到 "鲜苹果"（高分）
2. 查询词 "苹果" 应该能匹配到包含"苹果"的长描述（中等分数）
3. 验证实际查询能够正确返回结果
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search_optimizer import SearchOptimizer


def test_similarity_calculation():
    """测试相似度计算函数"""
    print("=" * 60)
    print("测试 1: 相似度计算函数")
    print("=" * 60)
    
    optimizer = SearchOptimizer()
    
    # 测试用例
    test_cases = [
        # (查询词, 候选词, 预期最低分数, 说明)
        ("苹果", "苹果", 1.0, "完全匹配"),
        ("苹果", "鲜苹果", 0.85, "包含关系-短"),
        ("苹果", "白利糖度值不超过20的苹果汁", 0.70, "包含关系-长"),
        ("苹果", "苹果干", 0.85, "包含关系"),
        ("烘干机", "其他烟丝烘干机", 0.70, "包含关系-描述性"),
        ("笔记本电脑", "专用于平板电脑和笔记本电脑的带触摸屏的液晶模组", 0.65, "包含关系-长描述"),
    ]
    
    all_passed = True
    
    for query, candidate, min_expected, description in test_cases:
        score = optimizer.calculate_similarity(query, candidate)
        passed = score >= min_expected
        status = "✅ 通过" if passed else "❌ 失败"
        
        print(f"\n{status} {description}")
        print(f"  查询词: '{query}'")
        print(f"  候选词: '{candidate}'")
        print(f"  实际分数: {score:.2f}, 预期最低: {min_expected:.2f}")
        
        if not passed:
            all_passed = False
    
    return all_passed


def test_best_match():
    """测试最佳匹配查找"""
    print("\n" + "=" * 60)
    print("测试 2: 最佳匹配查找")
    print("=" * 60)
    
    optimizer = SearchOptimizer()
    
    # 模拟"苹果"的搜索结果（来自截图）
    candidates = [
        "白利糖度值不超过20的苹果汁",
        "鲜苹果",
        "白利糖度值超过20的苹果汁",
        "苹果干"
    ]
    
    query = "苹果"
    best_match, best_score = optimizer.find_best_match(query, candidates, min_score=0.6)
    
    print(f"\n查询词: '{query}'")
    print(f"候选项: {candidates}")
    print(f"最佳匹配: '{best_match}'")
    print(f"匹配分数: {best_score:.2f}")
    
    # 期望匹配到 "鲜苹果"（最短且包含查询词）
    expected = "鲜苹果"
    passed = best_match == expected and best_score >= 0.85
    
    if passed:
        print(f"✅ 通过 - 正确匹配到 '{expected}'")
    else:
        print(f"❌ 失败 - 期望匹配 '{expected}'，实际匹配 '{best_match}'")
    
    return passed


def test_actual_query():
    """测试实际查询功能"""
    print("\n" + "=" * 60)
    print("测试 3: 实际查询 '苹果'")
    print("=" * 60)
    
    from src.scraper import HSCodeScraper
    from src.storage import DataStorage
    
    scraper = HSCodeScraper()
    storage = DataStorage()
    
    # 查询"苹果"
    result = scraper.query_by_product_name("苹果")
    
    if result:
        print(f"\n✅ 查询成功!")
        print(f"HS编码: {result.get('hs_code', 'N/A')}")
        print(f"商品名称: {result.get('product_name', 'N/A')}")
        print(f"申报要素: {result.get('declaration_elements', 'N/A')[:50]}...")
        
        # 保存结果
        output_file = storage.save_single_result(result, "test_fix_002")
        print(f"\n结果已保存到: {output_file}")
        
        return True
    else:
        print("\n❌ 查询失败 - 未找到匹配结果")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("修复 #002 验证 - 改进相似度匹配算法")
    print("=" * 60)
    
    results = []
    
    # 测试1: 相似度计算
    try:
        results.append(("相似度计算", test_similarity_calculation()))
    except Exception as e:
        print(f"\n❌ 测试1失败: {e}")
        results.append(("相似度计算", False))
    
    # 测试2: 最佳匹配
    try:
        results.append(("最佳匹配查找", test_best_match()))
    except Exception as e:
        print(f"\n❌ 测试2失败: {e}")
        results.append(("最佳匹配查找", False))
    
    # 测试3: 实际查询
    try:
        results.append(("实际查询", test_actual_query()))
    except Exception as e:
        print(f"\n❌ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("实际查询", False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✅ 修复验证通过！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 部分测试失败，请检查上述输出")
        print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
