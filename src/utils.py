"""
工具函数模块
包含日志、重试装饰器等通用功能
"""
import logging
import time
import functools
from typing import Callable, Any
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    LOG_LEVEL, LOG_FORMAT, LOG_FILE, 
    MAX_RETRIES, RETRY_DELAY
)


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 文件处理器
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        console_formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


def retry_on_exception(
    max_retries: int = MAX_RETRIES,
    delay: int = RETRY_DELAY,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    重试装饰器，当函数抛出异常时自动重试
    
    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
        exceptions: 需要捕获的异常类型
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = setup_logger(func.__module__)
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} 执行失败，已达到最大重试次数 {max_retries}: {str(e)}")
                        raise
                    else:
                        logger.warning(
                            f"{func.__name__} 执行失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}，"
                            f"{delay}秒后重试..."
                        )
                        time.sleep(delay)
            
        return wrapper
    return decorator


def safe_get_text(element, default: str = "") -> str:
    """
    安全获取元素文本内容
    
    Args:
        element: BeautifulSoup元素
        default: 默认值
        
    Returns:
        文本内容
    """
    try:
        return element.get_text(strip=True) if element else default
    except Exception:
        return default


def clean_text(text: str) -> str:
    """
    清理文本，去除多余空白字符
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 替换多个空白字符为单个空格
    import re
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def create_empty_result() -> dict:
    """
    创建空的查询结果
    
    Returns:
        包含所有字段的空字典
    """
    return {
        "hs_code": "",
        "product_name": "",
        "declaration_elements": "",
        "first_unit": "",
        "second_unit": "",
        "customs_supervision_conditions": {
            "code": "",
            "details": []
        },
        "inspection_quarantine": {
            "code": "",
            "details": []
        },
        "description": "",
        "search_success": False,
        "error_message": ""
    }
