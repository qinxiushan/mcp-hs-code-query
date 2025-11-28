"""
基于嵌入向量的商品名称相似度匹配模块

使用 BGE (BAAI General Embedding) 模型进行语义相似度计算
模型: BAAI/bge-small-zh-v1.5 (中文小型模型,适合快速推理)

创建日期: 2025-11-26
更新日期: 2025-11-26 - 添加嵌入向量缓存机制
"""

import logging
from typing import List, Tuple, Optional, Dict
from functools import lru_cache
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class EmbeddingMatcher:
    """基于嵌入向量的语义相似度匹配器"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5", 
                 cache_dir: Optional[str] = None,
                 enable_cache: bool = True,
                 cache_size: int = 1000):
        """
        初始化嵌入模型
        
        Args:
            model_name: 预训练模型名称
                - BAAI/bge-small-zh-v1.5: 中文小型模型 (推荐,速度快)
                - BAAI/bge-base-zh-v1.5: 中文基础模型 (更准确,稍慢)
                - BAAI/bge-large-zh-v1.5: 中文大型模型 (最准确,最慢)
            cache_dir: 模型缓存目录,默认使用 HuggingFace 默认缓存
            enable_cache: 是否启用嵌入向量缓存 (默认True)
            cache_size: 缓存大小,最多缓存多少个文本的嵌入向量 (默认1000)
        """
        logger.info(f"正在加载嵌入模型: {model_name}")
        
        try:
            # 加载预训练模型
            self.model = SentenceTransformer(
                model_name,
                cache_folder=cache_dir,
                device='cpu'  # 使用 CPU,如果有 GPU 可改为 'cuda'
            )
            
            # 获取嵌入维度
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            # 缓存配置
            self.enable_cache = enable_cache
            self.cache_size = cache_size
            self._embedding_cache: Dict[str, np.ndarray] = {}
            self._cache_hits = 0
            self._cache_misses = 0
            
            logger.info(f"模型加载成功,嵌入维度: {self.embedding_dim}")
            if self.enable_cache:
                logger.info(f"嵌入向量缓存已启用,缓存大小: {self.cache_size}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def _get_cache_key(self, text: str) -> str:
        """
        生成文本的缓存键
        
        Args:
            text: 输入文本
            
        Returns:
            缓存键(文本的MD5哈希)
        """
        # 使用MD5哈希避免文本过长
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_from_cache(self, text: str) -> Optional[np.ndarray]:
        """
        从缓存中获取嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量,如果不存在则返回None
        """
        if not self.enable_cache:
            return None
        
        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache:
            self._cache_hits += 1
            current_hit_rate = self.get_cache_hit_rate()
            logger.debug(f"✓ 缓存命中: '{text[:20]}...' (键: {cache_key[:8]}..., 命中率: {current_hit_rate:.2%})")
            return self._embedding_cache[cache_key]
        
        self._cache_misses += 1
        logger.debug(f"✗ 缓存未命中: '{text[:20]}...' (键: {cache_key[:8]}...)")
        return None
    
    def _put_to_cache(self, text: str, embedding: np.ndarray):
        """
        将嵌入向量存入缓存
        
        Args:
            text: 输入文本
            embedding: 嵌入向量
        """
        if not self.enable_cache:
            return
        
        # 如果缓存已满,删除最早的项(FIFO策略)
        if len(self._embedding_cache) >= self.cache_size:
            # 删除第一个键
            first_key = next(iter(self._embedding_cache))
            del self._embedding_cache[first_key]
            logger.debug(f"⚠ 缓存已满,删除最早项 (当前大小: {len(self._embedding_cache)}/{self.cache_size})")
        
        cache_key = self._get_cache_key(text)
        self._embedding_cache[cache_key] = embedding
        logger.debug(f"✓ 已存入缓存: '{text[:20]}...' (键: {cache_key[:8]}..., 大小: {len(self._embedding_cache)}/{self.cache_size})")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        return {
            'enabled': self.enable_cache,
            'size': len(self._embedding_cache),
            'max_size': self.cache_size,
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_rate': self.get_cache_hit_rate(),
            'total_requests': self._cache_hits + self._cache_misses
        }
    
    def get_cache_hit_rate(self) -> float:
        """
        获取缓存命中率
        
        Returns:
            命中率 (0-1之间)
        """
        total = self._cache_hits + self._cache_misses
        return self._cache_hits / total if total > 0 else 0.0
    
    def clear_cache(self):
        """清空缓存"""
        self._embedding_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("嵌入向量缓存已清空")
    
    def encode(self, texts: List[str], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        """
        将文本列表编码为嵌入向量(支持缓存)
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
            show_progress: 是否显示进度条
            
        Returns:
            嵌入向量矩阵,形状为 (len(texts), embedding_dim)
        """
        if not texts:
            logger.debug("文本列表为空,返回空数组")
            return np.array([])
        
        # 文本预处理:去除空白
        texts = [str(text).strip() for text in texts]
        logger.debug(f"开始编码 {len(texts)} 个文本")
        
        # 检查缓存
        embeddings_list = []
        texts_to_encode = []
        text_indices = []
        
        for i, text in enumerate(texts):
            cached_embedding = self._get_from_cache(text)
            if cached_embedding is not None:
                embeddings_list.append((i, cached_embedding))
                logger.debug(f"  [{i}] 缓存命中: '{text[:30]}...'")
            else:
                texts_to_encode.append(text)
                text_indices.append(i)
                logger.debug(f"  [{i}] 需要编码: '{text[:30]}...'")
        
        # 编码未缓存的文本
        if texts_to_encode:
            logger.debug(f"开始编码 {len(texts_to_encode)} 个未缓存的文本...")
            new_embeddings = self.model.encode(
                texts_to_encode,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 归一化,用于余弦相似度
            )
            logger.debug(f"编码完成,向量维度: {new_embeddings.shape}")
            
            # 存入缓存
            for text, embedding in zip(texts_to_encode, new_embeddings):
                self._put_to_cache(text, embedding)
                logger.debug(f"  已缓存: '{text[:30]}...'")
                
            # 添加到结果列表
            for idx, embedding in zip(text_indices, new_embeddings):
                embeddings_list.append((idx, embedding))
        else:
            logger.debug("所有文本均命中缓存,无需编码")
        
        # 按原始顺序排列
        embeddings_list.sort(key=lambda x: x[0])
        embeddings = np.array([emb for _, emb in embeddings_list])
        
        logger.debug(f"编码完成,返回形状: {embeddings.shape}")
        return embeddings
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的余弦相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            余弦相似度分数 (0-1之间,越接近1越相似)
        """
        logger.debug(f"开始计算相似度:")
        logger.debug(f"  文本1: '{text1}'")
        logger.debug(f"  文本2: '{text2}'")
        
        # 编码
        logger.debug("正在编码文本...")
        embeddings = self.encode([text1, text2])
        logger.debug(f"编码完成,嵌入向量维度: {embeddings.shape}")
        
        # 计算余弦相似度
        similarity = cosine_similarity(
            embeddings[0:1],  # 第一个向量
            embeddings[1:2]   # 第二个向量
        )[0][0]
        
        logger.debug(f"相似度计算结果: {similarity:.6f}")
        logger.info(f"相似度: '{text1[:20]}...' <-> '{text2[:20]}...' = {similarity:.4f}")
        
        return float(similarity)
    
    def find_best_match(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.5
    ) -> Tuple[Optional[str], float, int]:
        """
        从候选列表中找到与查询最相似的文本
        
        Args:
            query: 查询文本
            candidates: 候选文本列表
            threshold: 最小相似度阈值
            
        Returns:
            (最佳匹配文本, 相似度分数, 索引), 如果没有匹配则返回 (None, 0.0, -1)
        """
        if not candidates:
            logger.debug("候选列表为空")
            return None, 0.0, -1
        
        logger.debug(f"开始查找最佳匹配:")
        logger.debug(f"  查询: '{query}'")
        logger.debug(f"  候选数量: {len(candidates)}")
        logger.debug(f"  相似度阈值: {threshold}")
        
        # 编码查询和所有候选
        query_embedding = self.encode([query])
        candidate_embeddings = self.encode(candidates)
        
        # 计算余弦相似度
        similarities = cosine_similarity(
            query_embedding,
            candidate_embeddings
        )[0]
        
        # 输出所有相似度分数
        logger.debug("所有候选的相似度分数:")
        for i, (candidate, score) in enumerate(zip(candidates, similarities)):
            logger.debug(f"  [{i}] {score:.6f} - '{candidate[:40]}...'")
        
        # 找到最高分数
        max_idx = int(np.argmax(similarities))
        max_score = float(similarities[max_idx])
        
        logger.debug(f"最高分数: {max_score:.6f} (索引: {max_idx})")
        
        # 检查是否超过阈值
        if max_score >= threshold:
            logger.info(f"找到最佳匹配: '{candidates[max_idx][:40]}...' (分数: {max_score:.4f})")
            return candidates[max_idx], max_score, max_idx
        else:
            logger.warning(f"最佳匹配分数 {max_score:.4f} 低于阈值 {threshold}")
            return None, max_score, max_idx
    
    def batch_similarity(
        self,
        query: str,
        candidates: List[str]
    ) -> List[Tuple[str, float]]:
        """
        计算查询文本与所有候选文本的相似度
        
        Args:
            query: 查询文本
            candidates: 候选文本列表
            
        Returns:
            [(候选文本, 相似度分数), ...] 按相似度降序排列
        """
        if not candidates:
            logger.debug("候选列表为空")
            return []
        
        logger.debug(f"批量计算相似度:")
        logger.debug(f"  查询: '{query}'")
        logger.debug(f"  候选数量: {len(candidates)}")
        
        # 编码
        query_embedding = self.encode([query])
        candidate_embeddings = self.encode(candidates)
        
        # 计算相似度
        similarities = cosine_similarity(
            query_embedding,
            candidate_embeddings
        )[0]
        
        # 输出每个候选的相似度
        logger.debug("相似度详情:")
        for i, (candidate, score) in enumerate(zip(candidates, similarities)):
            logger.debug(f"  [{i}] {score:.6f} - '{candidate[:40]}...'")
        
        # 组合结果并排序
        results = list(zip(candidates, similarities))
        results.sort(key=lambda x: x[1], reverse=True)
        
        logger.debug(f"排序后前3名:")
        for i, (text, score) in enumerate(results[:3], 1):
            logger.debug(f"  {i}. {score:.6f} - '{text[:40]}...'")
        
        return [(text, float(score)) for text, score in results]


# 全局单例模式,避免重复加载模型
_global_matcher: Optional[EmbeddingMatcher] = None


def get_embedding_matcher(
    model_name: str = "BAAI/bge-small-zh-v1.5",
    force_reload: bool = False
) -> EmbeddingMatcher:
    """
    获取全局嵌入匹配器单例
    
    Args:
        model_name: 模型名称
        force_reload: 是否强制重新加载模型
        
    Returns:
        EmbeddingMatcher 实例
    """
    global _global_matcher
    
    if _global_matcher is None or force_reload:
        _global_matcher = EmbeddingMatcher(model_name=model_name)
    
    return _global_matcher


if __name__ == "__main__":
    # 测试代码
    import time
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("BGE 嵌入向量相似度匹配测试 (带缓存)")
    print("="*60)
    
    # 初始化匹配器
    matcher = EmbeddingMatcher(enable_cache=True, cache_size=100)
    
    # 测试1: 两个文本相似度
    print("\n测试1: 文本相似度计算")
    text1 = "鲜苹果"
    text2 = "新鲜的苹果"
    text3 = "香蕉"
    
    score1 = matcher.calculate_similarity(text1, text2)
    score2 = matcher.calculate_similarity(text1, text3)
    
    print(f"'{text1}' vs '{text2}': {score1:.4f}")
    print(f"'{text1}' vs '{text3}': {score2:.4f}")
    
    # 测试2: 最佳匹配
    print("\n测试2: 从候选列表中找最佳匹配")
    query = "苹果"
    candidates = [
        "鲜苹果",
        "干苹果",
        "苹果汁",
        "香蕉",
        "橙子",
        "其他种用苗木",
        "鲜梨"
    ]
    
    best_match, score, idx = matcher.find_best_match(query, candidates, threshold=0.5)
    print(f"查询: '{query}'")
    print(f"最佳匹配: '{best_match}' (相似度: {score:.4f}, 索引: {idx})")
    
    # 测试3: 批量相似度
    print("\n测试3: 批量相似度计算")
    results = matcher.batch_similarity(query, candidates)
    print(f"查询: '{query}'")
    print("所有候选排序:")
    for i, (text, score) in enumerate(results[:5], 1):
        print(f"  {i}. '{text}': {score:.4f}")
    
    # 测试4: 缓存性能测试
    print("\n测试4: 缓存性能测试")
    test_queries = ["苹果", "香蕉", "橙子"] * 10  # 重复查询
    
    # 清空缓存,测试无缓存性能
    matcher.clear_cache()
    start_time = time.time()
    for q in test_queries:
        matcher.find_best_match(q, candidates)
    time_no_cache = time.time() - start_time
    
    # 重置缓存,测试有缓存性能
    matcher.clear_cache()
    start_time = time.time()
    for q in test_queries:
        matcher.find_best_match(q, candidates)
    time_with_cache = time.time() - start_time
    
    print(f"处理 {len(test_queries)} 个查询:")
    print(f"  第一次(无缓存): {time_no_cache:.3f}秒")
    print(f"  第二次(有缓存): {time_with_cache:.3f}秒")
    print(f"  性能提升: {time_no_cache/time_with_cache:.1f}x")
    
    # 缓存统计
    stats = matcher.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  缓存大小: {stats['size']}/{stats['max_size']}")
    print(f"  缓存命中: {stats['hits']}")
    print(f"  缓存未命中: {stats['misses']}")
    print(f"  命中率: {stats['hit_rate']:.2%}")
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
