from src.scraper import HSCodeScraper

s = HSCodeScraper()
result = s.query_by_product_name('烘干机')
print(f'\n最终结果: {result.get("hs_code")} - {result.get("product_name")}')
