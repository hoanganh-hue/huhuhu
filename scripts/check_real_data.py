#!/usr/bin/env python3
"""
Script kiểm tra dữ liệu thực - không có mock data
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_real_data():
    """Kiểm tra dữ liệu thực"""
    logger.info("🔍 Kiểm tra dữ liệu thực...")
    
    # Kiểm tra environment variables
    mock_vars = ['USE_MOCK', 'MOCK_DATA', 'TEST_MODE']
    for var in mock_vars:
        if os.getenv(var):
            logger.error(f"❌ Tìm thấy biến môi trường mock: {var}")
            return False
    
    # Kiểm tra file source data
    data_files = ['data.csv', 'input.xlsx', 'customers.csv']
    for file in data_files:
        if Path(file).exists():
            logger.info(f"✅ Tìm thấy file dữ liệu: {file}")
            # TODO: Kiểm tra nội dung file không chứa dummy data
    
    # Kiểm tra code không có mock
    mock_keywords = ['mock', 'dummy', 'test_data', 'sample_data']
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for keyword in mock_keywords:
                            if keyword in content:
                                logger.warning(f"⚠️ Tìm thấy từ khóa mock trong {filepath}: {keyword}")
                except Exception as e:
                    logger.error(f"❌ Lỗi đọc file {filepath}: {e}")
    
    logger.info("✅ Kiểm tra dữ liệu thực hoàn thành")
    return True

if __name__ == "__main__":
    success = check_real_data()
    sys.exit(0 if success else 1)
