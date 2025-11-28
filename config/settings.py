"""
配置文件
"""

# 网站配置
BASE_URL = "https://www.i5a6.com"
SEARCH_URL = f"{BASE_URL}/"
DETAIL_URL_TEMPLATE = f"{BASE_URL}/hscode/detail/{{hs_code}}"

# 请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟（秒）
REQUEST_DELAY = 1  # 请求间隔（秒），避免频繁请求

# 搜索配置
MAX_SEARCH_ATTEMPTS = 5  # 分词后最大搜索尝试次数
MIN_SIMILARITY_SCORE = 0.5  # 最小相似度分数（0-1）

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# 日志配置
LOG_LEVEL = "DEBUG"  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = "logs/hs_code_scraper.log"

# 输出配置
OUTPUT_DIR = "data/output"
OUTPUT_ENCODING = "utf-8"
