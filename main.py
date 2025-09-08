#!/usr/bin/env python3
"""
Hệ thống tra cứu thông tin BHXH - Production Version
Chỉ bao gồm Feature-1 (Tạo CCCD) và Feature-6 (Export Excel)
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from environment variables"""
    config = {
        'cccd_count': int(os.getenv('CCCD_COUNT', 1000)),
        'province_code': os.getenv('CCCD_PROVINCE_CODE', '001'),
        'gender': os.getenv('CCCD_GENDER', 'Nam'),
        'birth_year_from': int(os.getenv('CCCD_BIRTH_YEAR_FROM', 1990)),
        'birth_year_to': int(os.getenv('CCCD_BIRTH_YEAR_TO', 2000)),
        'output_file': os.getenv('OUTPUT_FILE', 'output.xlsx'),
        'output_sheet': os.getenv('OUTPUT_SHEET', 'Result'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    }
    return config

def main():
    """Main function - Production ready"""
    logger.info("🚀 Starting BHXH Information System - Production Mode")
    logger.info("📋 Features: CCCD Generation (Feature-1) and Excel Export (Feature-6)")
    
    try:
        # Load configuration
        config = load_config()
        logger.info(f"⚙️ Configuration loaded: {config}")
        
        # Feature-1: CCCD Generation
        logger.info("🔢 Starting Feature-1: CCCD Generation")
        from src.modules.core.cccd_generator import CCCDGenerator
        
        cccd_generator = CCCDGenerator(config)
        cccd_data = cccd_generator.generate_batch()
        
        # Save CCCD data to file
        cccd_generator.save_to_file(cccd_data, 'output/cccd_data.txt')
        
        logger.info(f"✅ Feature-1 completed: Generated {len(cccd_data)} CCCD records")
        
        # Feature-2: Data Lookup (Tra cứu dữ liệu thực tế)
        logger.info("🔍 Starting Feature-2: Data Lookup")
        from src.modules.core.data_lookup import DataLookupService
        
        lookup_service = DataLookupService(config)
        
        # Lấy danh sách CCCD để tra cứu
        cccd_list = [cccd_item.cccd for cccd_item in cccd_data]
        
        # Thực hiện tra cứu hàng loạt (giới hạn 100 để test)
        test_cccd_list = cccd_list[:100]  # Test với 100 CCCD đầu tiên
        logger.info(f"🔍 Performing lookup for {len(test_cccd_list)} CCCD records")
        
        lookup_results = lookup_service.batch_lookup(test_cccd_list)
        
        # Lưu kết quả tra cứu
        lookup_service.save_results(lookup_results, 'output/lookup_results.json')
        
        logger.info(f"✅ Feature-2 completed: Lookup completed for {len(lookup_results)} records")
        
        # Feature-6: Excel Export với dữ liệu thực tế
        logger.info("📊 Starting Feature-6: Excel Export with Real Data")
        from src.modules.core.excel_exporter import ExcelExporter
        
        excel_exporter = ExcelExporter(config)
        
        # Convert CCCD data và lookup results to format suitable for Excel
        excel_data = []
        lookup_dict = {result.cccd: result for result in lookup_results}
        
        for i, cccd_item in enumerate(cccd_data, 1):
            # Lấy thông tin tra cứu nếu có
            lookup_result = lookup_dict.get(cccd_item.cccd)
            
            excel_data.append({
                'STT': i,
                'CCCD': cccd_item.cccd,
                'Họ và tên': cccd_item.full_name,
                'Ngày sinh': cccd_item.birth_date,
                'Địa chỉ': cccd_item.address,
                'Mã số thuế': lookup_result.tax_code if lookup_result else None,
                'Tên công ty': lookup_result.company_name if lookup_result else None,
                'Người đại diện': lookup_result.representative if lookup_result else None,
                'Mã BHXH': lookup_result.bhxh_code if lookup_result else f'BHXH{i:06d}',
                'Loại hình DN': lookup_result.business_type if lookup_result else 'Chưa xác định',
                'Trạng thái': lookup_result.business_status if lookup_result else 'Chưa tra cứu',
                'Ngày đăng ký': lookup_result.registration_date if lookup_result else None,
                'Số điện thoại': lookup_result.phone if lookup_result else None,
                'Email': lookup_result.email if lookup_result else None,
                'Trạng thái tra cứu': lookup_result.status if lookup_result else 'Chưa tra cứu',
                'Nguồn dữ liệu': lookup_result.source if lookup_result else 'Generated'
            })
        
        # Export to Excel
        success = excel_exporter.export_to_excel(excel_data)
        
        if success:
            logger.info(f"✅ Feature-6 completed: Excel exported to {config['output_file']}")
            
            # Create summary report
            summary = excel_exporter.create_summary_report(excel_data)
            excel_exporter.save_summary_report(summary, 'output/summary_report.txt')
            
        else:
            logger.error("❌ Feature-6 failed: Excel export failed")
        
        logger.info("✅ System completed successfully")
        logger.info(f"📊 Total records processed: {len(cccd_data)}")
        logger.info(f"🔍 Records with lookup data: {len(lookup_results)}")
        logger.info(f"📁 Output files:")
        logger.info(f"  - {config['output_file']} (Excel with real data)")
        logger.info(f"  - output/cccd_data.txt (CCCD data)")
        logger.info(f"  - output/lookup_results.json (Lookup results)")
        logger.info(f"  - output/summary_report.txt (Summary)")
        
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
