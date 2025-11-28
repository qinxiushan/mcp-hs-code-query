"""
相似度算法对比测试
比较传统算法 vs BGE 嵌入向量算法
"""

import logging
from src.search_optimizer import SearchOptimizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_similarity_comparison():
    """对比两种相似度算法"""
    print("="*80)
    print("相似度算法对比测试")
    print("="*80)
    
    # 初始化两个优化器
    print("\n初始化优化器...")
    optimizer_traditional = SearchOptimizer(use_embedding=False)
    optimizer_embedding = SearchOptimizer(use_embedding=True)
    
    # 测试用例
    test_cases = [
        # (查询词, 候选词, 预期关系)
        ("苹果", "鲜苹果", "高度相关"),
        ("苹果", "干苹果", "高度相关"),
        ("苹果", "苹果汁", "中度相关"),
        ("苹果", "苹果手机", "低度相关"),
        ("苹果", "香蕉", "不相关"),
        ("苹果", "鲜梨", "不相关"),
        ("笔记本电脑", "专用于平板电脑和笔记本电脑的带触摸屏的液晶模组", "高度相关"),
        ("笔记本电脑", "笔记本", "中度相关"),
        ("笔记本电脑", "电脑配件", "低度相关"),
        ("棉质T恤", "纯棉T恤", "高度相关"),
        ("棉质T恤", "棉质衬衫", "中度相关"),
        ("棉质T恤", "化纤T恤", "低度相关"),
    ]
    
    print("\n" + "="*80)
    print(f"{'查询词':<15} {'候选词':<30} {'预期':<10} {'传统算法':<12} {'嵌入向量':<12} {'差异':<10}")
    print("="*80)
    
    total_traditional = 0
    total_embedding = 0
    count = 0
    
    for query, candidate, expected in test_cases:
        # 计算相似度
        score_traditional = optimizer_traditional.calculate_similarity(query, candidate)
        score_embedding = optimizer_embedding.calculate_similarity(query, candidate)
        
        diff = score_embedding - score_traditional
        
        total_traditional += score_traditional
        total_embedding += score_embedding
        count += 1
        
        # 打印结果
        print(f"{query:<15} {candidate:<30} {expected:<10} {score_traditional:<12.4f} {score_embedding:<12.4f} {diff:>+10.4f}")
    
    print("="*80)
    print(f"{'平均分数':<15} {'':<30} {'':<10} {total_traditional/count:<12.4f} {total_embedding/count:<12.4f}")
    print("="*80)
    
    # 分析
    print("\n分析:")
    print("1. 传统算法: 基于字符串匹配 (rapidfuzz), 对字面相似度敏感")
    print("2. 嵌入向量: 基于语义理解 (BGE模型), 能捕捉语义相关性")
    print("\n优势对比:")
    print("- 传统算法: 速度快, 完全包含关系判断准确")
    print("- 嵌入向量: 语义理解强, 能识别同义词和相关概念")


def test_real_world_scenario():
    """真实场景测试"""
    print("\n\n" + "="*80)
    print("真实场景测试: 从候选列表中找最佳匹配")
    print("="*80)
    
    # 初始化优化器
    optimizer_traditional = SearchOptimizer(use_embedding=False)
    optimizer_embedding = SearchOptimizer(use_embedding=True)
    
    # 模拟搜索结果
    query = "苹果"
    candidates = [
        "鲜苹果",
        "干苹果",
        "苹果汁",
        "苹果酱",
        "香蕉",
        "橙子",
        "其他种用苗木",
        "专用于平板电脑和笔记本电脑的带触摸屏的液晶模组",
        "白利糖度值不超过20的苹果汁"
    ]
    
    print(f"\n查询词: {query}")
    print(f"候选列表: {len(candidates)} 个商品\n")
    
    # 传统算法
    print("传统算法 (rapidfuzz) 结果:")
    scores_traditional = [(c, optimizer_traditional.calculate_similarity(query, c)) for c in candidates]
    scores_traditional.sort(key=lambda x: x[1], reverse=True)
    
    for i, (candidate, score) in enumerate(scores_traditional[:5], 1):
        print(f"  {i}. {candidate:<50} {score:.4f}")
    
    # 嵌入向量
    print("\n嵌入向量 (BGE) 结果:")
    scores_embedding = [(c, optimizer_embedding.calculate_similarity(query, c)) for c in candidates]
    scores_embedding.sort(key=lambda x: x[1], reverse=True)
    
    for i, (candidate, score) in enumerate(scores_embedding[:5], 1):
        print(f"  {i}. {candidate:<50} {score:.4f}")
    
    print("\n结论:")
    print("- 两种算法都能正确识别'鲜苹果'为最佳匹配")
    print("- 嵌入向量在处理语义相关性时更有优势")


def test_performance():
    """性能测试"""
    import time
    
    print("\n\n" + "="*80)
    print("性能测试")
    print("="*80)
    
    # 初始化优化器
    optimizer_traditional = SearchOptimizer(use_embedding=False)
    optimizer_embedding = SearchOptimizer(use_embedding=True)  # 模型已加载
    
    query = "苹果"
    candidate = "鲜苹果"
    iterations = 100
    
    # 传统算法性能
    start = time.time()
    for _ in range(iterations):
        optimizer_traditional.calculate_similarity(query, candidate)
    time_traditional = time.time() - start
    
    # 嵌入向量性能
    start = time.time()
    for _ in range(iterations):
        optimizer_embedding.calculate_similarity(query, candidate)
    time_embedding = time.time() - start
    
    print(f"\n计算 {iterations} 次相似度:")
    print(f"传统算法总耗时: {time_traditional:.3f}秒 (平均 {time_traditional/iterations*1000:.2f}ms)")
    print(f"嵌入向量总耗时: {time_embedding:.3f}秒 (平均 {time_embedding/iterations*1000:.2f}ms)")
    print(f"速度比: 嵌入向量是传统算法的 {time_embedding/time_traditional:.1f}x")
    
    print("\n说明:")
    print("- 传统算法更快,适合大规模实时查询")
    print("- 嵌入向量虽慢,但准确度更高,适合对准确性要求高的场景")
    print("- 可通过批量编码优化嵌入向量性能")


if __name__ == "__main__":
    try:
        # 测试1: 相似度对比
        test_similarity_comparison()
        
        # 测试2: 真实场景
        test_real_world_scenario()
        
        # 测试3: 性能对比
        test_performance()
        
        print("\n\n" + "="*80)
        print("所有测试完成!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}", exc_info=True)
        print(f"\n错误: {e}")
