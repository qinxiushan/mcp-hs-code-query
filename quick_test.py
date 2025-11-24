from src.scraper import HSCodeScraper

s = HSCodeScraper()
result = s.query_by_product_name('苹果')
print(f'结果: {result.get("hs_code")} - {result.get("product_name")}')
