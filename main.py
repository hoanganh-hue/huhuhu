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
        
        # Feature-6: Excel Export
        logger.info("📊 Starting Feature-6: Excel Export")
        from src.modules.core.excel_exporter import ExcelExporter
        
        excel_exporter = ExcelExporter(config)
        
        # Convert CCCD data to format suitable for Excel
        excel_data = []
        for i, cccd_item in enumerate(cccd_data, 1):
            excel_data.append({
                'STT': i,
                'CCCD': cccd_item.cccd,
                'Họ và tên': cccd_item.full_name,
                'Ngày sinh': cccd_item.birth_date,
                'Địa chỉ': cccd_item.address,
                'Mã BHXH': f'BHXH{i:06d}',  # Generate BHXH code
                'Ngành nghề': 'Kinh doanh',  # Default value
                'Doanh thu': 0,  # Default value
                'Ghi chú': 'Hoạt động bình thường'  # Default value
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
        logger.info(f"📁 Output files:")
        logger.info(f"  - {config['output_file']} (Excel)")
        logger.info(f"  - output/cccd_data.txt (CCCD data)")
        logger.info(f"  - output/summary_report.txt (Summary)")
        
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
