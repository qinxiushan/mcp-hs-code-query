"""
主程序入口
提供命令行接口和API接口
"""
import sys
import os
import argparse
from typing import List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import HSCodeScraper
from src.storage import DataStorage
from src.utils import setup_logger

logger = setup_logger(__name__)


def query_single(product_name: str, save: bool = True) -> dict:
    """
    单个商品查询
    
    Args:
        product_name: 商品名称
        save: 是否保存结果
        
    Returns:
        查询结果字典
    """
    scraper = HSCodeScraper()
    storage = DataStorage()
    
    try:
        # 查询
        result = scraper.query_by_product_name(product_name)
        
        # 显示结果
        print(storage.format_result_for_display(result))
        
        # 保存结果
        if save:
            filepath = storage.save_single_result(result)
            print(f"\n结果已保存到: {filepath}")
        
        return result
        
    finally:
        scraper.close()


def query_batch(product_names: List[str], save: bool = True) -> List[dict]:
    """
    批量商品查询
    
    Args:
        product_names: 商品名称列表
        save: 是否保存结果
        
    Returns:
        查询结果列表
    """
    scraper = HSCodeScraper()
    storage = DataStorage()
    
    try:
        # 批量查询
        results = scraper.batch_query(product_names)
        
        # 显示结果
        print(f"\n批量查询完成，共 {len(results)} 个商品")
        print(f"成功: {sum(1 for r in results if r['search_success'])} 个")
        print(f"失败: {sum(1 for r in results if not r['search_success'])} 个")
        
        # 保存结果
        if save:
            filepath = storage.save_batch_results(results)
            print(f"\n结果已保存到: {filepath}")
        
        return results
        
    finally:
        scraper.close()


def query_from_file(input_file: str, save: bool = True) -> List[dict]:
    """
    从文件读取商品名称并批量查询
    
    Args:
        input_file: 输入文件路径（每行一个商品名称）
        save: 是否保存结果
        
    Returns:
        查询结果列表
    """
    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        product_names = [line.strip() for line in f if line.strip()]
    
    print(f"从文件 {input_file} 读取了 {len(product_names)} 个商品名称")
    
    # 批量查询
    return query_batch(product_names, save)


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(
        description='HS编码查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 单个商品查询
  python main.py -s "苹果手机"
  
  # 批量查询
  python main.py -b "苹果" "香蕉" "橙子"
  
  # 从文件批量查询
  python main.py -f data/input/products.txt
  
  # 查询但不保存
  python main.py -s "电脑" --no-save
        '''
    )
    
    # 查询模式
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument(
        '-s', '--single',
        type=str,
        help='单个商品查询'
    )
    query_group.add_argument(
        '-b', '--batch',
        nargs='+',
        help='批量商品查询（空格分隔）'
    )
    query_group.add_argument(
        '-f', '--file',
        type=str,
        help='从文件读取商品名称（每行一个）'
    )
    
    # 其他选项
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='不保存查询结果'
    )
    
    args = parser.parse_args()
    
    try:
        # 单个查询
        if args.single:
            query_single(args.single, save=not args.no_save)
        
        # 批量查询
        elif args.batch:
            query_batch(args.batch, save=not args.no_save)
        
        # 从文件查询
        elif args.file:
            query_from_file(args.file, save=not args.no_save)
        
        logger.info("查询完成")
        
    except KeyboardInterrupt:
        print("\n\n用户中断查询")
        logger.info("用户中断查询")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        logger.error(f"执行失败: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
