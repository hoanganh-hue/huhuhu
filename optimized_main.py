#!/usr/bin/env python3
"""
Main script sử dụng dữ liệu CCCD tối ưu
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_optimized_cccd_data():
    """Load dữ liệu CCCD tối ưu"""
    try:
        with open('cccd_optimized_20250908_181028.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Loaded {len(data)} optimized CCCD records")
        return data
    except FileNotFoundError:
        logger.error("❌ Optimized CCCD data file not found")
        return None

def main():
    """Main function"""
    logger.info("🚀 STARTING OPTIMIZED CCCD LOOKUP PROJECT")
    logger.info("=" * 60)
    
    # Load optimized CCCD data
    cccd_data = load_optimized_cccd_data()
    if not cccd_data:
        logger.error("❌ Failed to load optimized CCCD data")
        return
    
    # Configuration
    config = {
        'max_retries': 3,
        'proxy_enabled': os.getenv('PROXY_ENABLED', 'false').lower() == 'true',
        'proxy_type': os.getenv('PROXY_TYPE', 'socks5'),
        'proxy_socks5_host': os.getenv('PROXY_SOCKS5_HOST', ''),
        'proxy_socks5_port': os.getenv('PROXY_SOCKS5_PORT', ''),
        'proxy_socks5_username': os.getenv('PROXY_SOCKS5_USERNAME', ''),
        'proxy_socks5_password': os.getenv('PROXY_SOCKS5_PASSWORD', ''),
        'proxy_http_host': os.getenv('PROXY_HTTP_HOST', ''),
        'proxy_http_port': os.getenv('PROXY_HTTP_PORT', ''),
        'proxy_http_username': os.getenv('PROXY_HTTP_USERNAME', ''),
        'proxy_http_password': os.getenv('PROXY_HTTP_PASSWORD', '')
    }
    
    # Feature-2: CCCD Check với Module 2 Enhanced V3 (Tra cứu dữ liệu thực tế)
    logger.info("🔍 Starting Feature-2: Optimized CCCD Check with Smart Anti-bot Protection")
    from src.modules.core.module_2_check_cccd_enhanced_v3 import Module2CheckCCCDEnhancedV3
    
    cccd_checker = Module2CheckCCCDEnhancedV3(config)
    
    # Lấy danh sách CCCD để tra cứu
    cccd_list = [item['cccd'] for item in cccd_data]
    
    # Thực hiện tra cứu hàng loạt (có thể cấu hình số lượng)
    lookup_limit = int(os.getenv('LOOKUP_LIMIT', '1000'))  # Mặc định 1000
    lookup_cccd_list = cccd_list[:lookup_limit]  # Xử lý theo giới hạn cấu hình
    logger.info(f"🔍 Performing optimized lookup for {len(lookup_cccd_list)} CCCD records")
    
    lookup_results = cccd_checker.batch_check(lookup_cccd_list)
    
    # Lưu kết quả tra cứu
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'cccd_optimized_lookup_results_{timestamp}.json'
    cccd_checker.save_results(lookup_results, output_file)
    
    logger.info(f"✅ Feature-2 completed: Optimized lookup completed for {len(lookup_results)} records")
    
    # Feature-6: Export Excel
    logger.info("📊 Starting Feature-6: Excel Export")
    from src.modules.core.excel_exporter import ExcelExporter
    
    excel_exporter = ExcelExporter()
    
    # Tạo dữ liệu cho Excel export
    excel_data = []
    for i, result in enumerate(lookup_results):
        excel_data.append({
            'STT': i + 1,
            'CCCD': result.cccd,
            'Status': result.status,
            'Company Name': result.company_name if hasattr(result, 'company_name') else '',
            'Tax Code': result.tax_code if hasattr(result, 'tax_code') else '',
            'Address': result.address if hasattr(result, 'address') else '',
            'Response Time': result.response_time if hasattr(result, 'response_time') else 0,
            'Source': result.source if hasattr(result, 'source') else '',
            'Error': result.error if hasattr(result, 'error') else ''
        })
    
    # Export to Excel
    excel_filename = f'cccd_optimized_results_{timestamp}.xlsx'
    excel_exporter.export_to_excel(excel_data, excel_filename)
    
    logger.info(f"✅ Feature-6 completed: Excel export saved to {excel_filename}")
    
    # Thống kê kết quả
    success_count = sum(1 for result in lookup_results if result.status == 'success')
    not_found_count = sum(1 for result in lookup_results if result.status == 'not_found')
    error_count = sum(1 for result in lookup_results if result.status == 'error')
    
    logger.info("📈 FINAL STATISTICS:")
    logger.info(f"  Total processed: {len(lookup_results)}")
    logger.info(f"  Success: {success_count} ({success_count/len(lookup_results)*100:.1f}%)")
    logger.info(f"  Not found: {not_found_count} ({not_found_count/len(lookup_results)*100:.1f}%)")
    logger.info(f"  Error: {error_count} ({error_count/len(lookup_results)*100:.1f}%)")
    
    logger.info("🎯 PROJECT COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()