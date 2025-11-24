"""
中文分词和搜索优化模块

修改历史:
- 修复 #002 (2025-11-24): 改进中文文本相似度匹配算法
  详见: docs/CHANGELOG_002_改进相似度匹配算法.md
"""
import jieba
from difflib import SequenceMatcher
from rapidfuzz import fuzz
from typing import List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MAX_SEARCH_ATTEMPTS, MIN_SIMILARITY_SCORE
from src.utils import setup_logger

logger = setup_logger(__name__)


class SearchOptimizer:
    """搜索优化器，负责分词和关键词组合"""
    
    def __init__(self):
        """初始化分词器"""
        # 初始化jieba分词
        jieba.setLogLevel(jieba.logging.INFO)
        logger.info("SearchOptimizer 初始化完成")
    
    def segment_text(self, text: str) -> List[str]:
        """
        对文本进行中文分词
        
        Args:
            text: 输入文本
            
        Returns:
            分词结果列表
        """
        if not text:
            return []
        
        # 使用jieba进行分词
        words = jieba.cut(text)
        
        # 过滤掉长度小于2的词和标点符号
        filtered_words = [
            word for word in words 
            if len(word.strip()) >= 2 and word.strip().isalnum()
        ]
        
        logger.debug(f"分词结果: {text} -> {filtered_words}")
        return filtered_words
    
    def generate_search_keywords(self, text: str, max_attempts: int = MAX_SEARCH_ATTEMPTS) -> List[str]:
        """
        生成搜索关键词组合
        策略：
        1. 原始文本
        2. 分词后的组合（从长到短）
        3. 单个词（从长到短）
        
        Args:
            text: 输入文本
            max_attempts: 最大尝试次数
            
        Returns:
            关键词列表
        """
        keywords = []
        
        # 1. 首先尝试原始文本
        keywords.append(text.strip())
        
        # 2. 分词
        words = self.segment_text(text)
        
        if not words:
            return keywords[:max_attempts]
        
        # 3. 生成不同长度的组合（从长到短）
        # 全部词组合
        if len(words) > 1:
            keywords.append(' '.join(words))
            keywords.append(''.join(words))
        
        # 4. 去掉最后一个词的组合
        if len(words) >= 3:
            keywords.append(' '.join(words[:-1]))
            keywords.append(''.join(words[:-1]))
        
        # 5. 去掉第一个词的组合
        if len(words) >= 3:
            keywords.append(' '.join(words[1:]))
            keywords.append(''.join(words[1:]))
        
        # 6. 取前两个词
        if len(words) >= 2:
            keywords.append(' '.join(words[:2]))
            keywords.append(''.join(words[:2]))
        
        # 7. 单个词（按长度排序，长的优先）
        sorted_words = sorted(words, key=len, reverse=True)
        keywords.extend(sorted_words)
        
        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw and kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        logger.info(f"为 '{text}' 生成了 {len(unique_keywords)} 个搜索关键词: {unique_keywords[:max_attempts]}")
        return unique_keywords[:max_attempts]
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        计算两个字符串的相似度（改进版 - 支持中文模糊匹配）
        
        使用多种策略组合：
        1. 完全匹配 -> 1.0
        2. 包含关系 -> 0.95
        3. 部分比率匹配（rapidfuzz.fuzz.partial_ratio）-> 适合中文子串匹配
        4. Token排序比率（rapidfuzz.fuzz.token_sort_ratio）-> 适合词序不同
        5. Token集合比率（rapidfuzz.fuzz.token_set_ratio）-> 适合部分重叠
        
        Args:
            str1: 字符串1
            str2: 字符串2
            
        Returns:
            相似度分数 (0-1)
        """
        if not str1 or not str2:
            return 0.0
        
        # 去除空格进行比较
        str1_clean = str1.strip()
        str2_clean = str2.strip()
        
        # 1. 完全匹配（忽略大小写）
        if str1_clean.lower() == str2_clean.lower():
            return 1.0
        
        # 2. 包含关系（查询词完全包含在候选词中）
        str1_lower = str1_clean.lower()
        str2_lower = str2_clean.lower()
        
        if str1_lower in str2_lower:
            # 根据长度比例调整分数
            # 例如："苹果" in "鲜苹果" -> 2/3 = 0.67，调整为 0.95
            # 例如："苹果" in "白利糖度值不超过20的苹果汁" -> 2/15 = 0.13，调整为 0.85
            length_ratio = len(str1_clean) / len(str2_clean)
            return 0.85 + (length_ratio * 0.15)  # 0.85 - 1.0
        
        if str2_lower in str1_lower:
            length_ratio = len(str2_clean) / len(str1_clean)
            return 0.85 + (length_ratio * 0.15)
        
        # 3. 使用 rapidfuzz 进行模糊匹配
        # partial_ratio: 部分匹配，适合子串查找
        partial_score = fuzz.partial_ratio(str1_clean, str2_clean) / 100.0
        
        # token_sort_ratio: 词序无关匹配
        token_sort_score = fuzz.token_sort_ratio(str1_clean, str2_clean) / 100.0
        
        # token_set_ratio: 词集合匹配
        token_set_score = fuzz.token_set_ratio(str1_clean, str2_clean) / 100.0
        
        # 取最高分
        max_score = max(partial_score, token_sort_score, token_set_score)
        
        logger.debug(
            f"相似度计算: '{str1_clean}' vs '{str2_clean}' -> "
            f"partial={partial_score:.2f}, token_sort={token_sort_score:.2f}, "
            f"token_set={token_set_score:.2f}, max={max_score:.2f}"
        )
        
        return max_score
    
    def find_best_match(
        self, 
        query: str, 
        candidates: List[str], 
        min_score: float = MIN_SIMILARITY_SCORE
    ) -> Tuple[str, float]:
        """
        从候选列表中找到最佳匹配
        
        Args:
            query: 查询字符串
            candidates: 候选字符串列表
            min_score: 最小相似度分数
            
        Returns:
            (最佳匹配字符串, 相似度分数)
        """
        if not candidates:
            return "", 0.0
        
        best_match = ""
        best_score = 0.0
        
        for candidate in candidates:
            score = self.calculate_similarity(query, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate
        
        if best_score < min_score:
            logger.warning(f"最佳匹配分数 {best_score:.2f} 低于最小阈值 {min_score}")
            return "", 0.0
        
        logger.info(f"找到最佳匹配: '{best_match}' (相似度: {best_score:.2f})")
        return best_match, best_score
