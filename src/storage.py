"""
数据存储模块
"""
import json
import os
from datetime import datetime
from typing import Dict, List
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import OUTPUT_DIR, OUTPUT_ENCODING
from src.utils import setup_logger

logger = setup_logger(__name__)


class DataStorage:
    """数据存储类，负责将查询结果保存为JSON格式"""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        """
        初始化存储
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"DataStorage 初始化完成，输出目录: {output_dir}")
    
    def save_single_result(self, result: Dict, filename: str = None) -> str:
        """
        保存单个查询结果
        
        Args:
            result: 查询结果字典
            filename: 输出文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            # 使用HS编码或时间戳作为文件名
            hs_code = result.get('hs_code', '').replace('.', '_')
            if hs_code:
                filename = f"hs_{hs_code}.json"
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"result_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 添加元数据
        output_data = {
            'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': result
        }
        
        try:
            with open(filepath, 'w', encoding=OUTPUT_ENCODING) as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"单个结果已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存单个结果失败: {str(e)}")
            raise
    
    def save_batch_results(self, results: List[Dict], filename: str = None) -> str:
        """
        保存批量查询结果
        
        Args:
            results: 查询结果列表
            filename: 输出文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"batch_results_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 添加元数据
        output_data = {
            'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(results),
            'success_count': sum(1 for r in results if r.get('search_success', False)),
            'failed_count': sum(1 for r in results if not r.get('search_success', False)),
            'data': results
        }
        
        try:
            with open(filepath, 'w', encoding=OUTPUT_ENCODING) as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"批量结果已保存到: {filepath}")
            logger.info(f"统计: 总数={output_data['total_count']}, "
                       f"成功={output_data['success_count']}, "
                       f"失败={output_data['failed_count']}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存批量结果失败: {str(e)}")
            raise
    
    def load_results(self, filepath: str) -> Dict:
        """
        从JSON文件加载结果
        
        Args:
            filepath: 文件路径
            
        Returns:
            结果字典
        """
        try:
            with open(filepath, 'r', encoding=OUTPUT_ENCODING) as f:
                data = json.load(f)
            
            logger.info(f"从 {filepath} 加载结果成功")
            return data
            
        except Exception as e:
            logger.error(f"加载结果失败: {str(e)}")
            raise
    
    def export_to_simple_json(self, results: List[Dict], filename: str = None) -> str:
        """
        导出为简化的JSON格式（仅包含核心数据，不含元数据）
        
        Args:
            results: 查询结果列表
            filename: 输出文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"simple_results_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding=OUTPUT_ENCODING) as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"简化结果已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存简化结果失败: {str(e)}")
            raise
    
    @staticmethod
    def format_result_for_display(result: Dict) -> str:
        """
        格式化单个结果用于控制台显示
        
        Args:
            result: 查询结果字典
            
        Returns:
            格式化的字符串
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"HS编码: {result.get('hs_code', 'N/A')}")
        lines.append(f"商品名称: {result.get('product_name', 'N/A')}")
        lines.append(f"商品描述: {result.get('description', 'N/A')}")
        lines.append(f"申报要素: {result.get('declaration_elements', 'N/A')}")
        lines.append(f"法定第一单位: {result.get('first_unit', 'N/A')}")
        lines.append(f"法定第二单位: {result.get('second_unit', 'N/A')}")
        
        # 海关监管条件
        supervision = result.get('customs_supervision_conditions', {})
        lines.append(f"海关监管条件: {supervision.get('code', 'N/A')}")
        if supervision.get('details'):
            lines.append("  许可证或批文:")
            for detail in supervision['details']:
                lines.append(f"    - {detail['code']}: {detail['name']}")
        
        # 检验检疫
        inspection = result.get('inspection_quarantine', {})
        lines.append(f"检验检疫类别: {inspection.get('code', 'N/A')}")
        if inspection.get('details'):
            lines.append("  检验检疫详情:")
            for detail in inspection['details']:
                lines.append(f"    - {detail['code']}: {detail['name']}")
        
        lines.append(f"查询状态: {'成功' if result.get('search_success') else '失败'}")
        if result.get('error_message'):
            lines.append(f"错误信息: {result['error_message']}")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
