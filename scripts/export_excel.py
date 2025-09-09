#!/usr/bin/env python3
"""
Script export Excel - Feature-6
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def export_excel(output_file="result.xlsx"):
    """Export dữ liệu ra file Excel"""
    logger.info(f"📊 Export Excel: {output_file}")
    
    try:
        # Tạo dữ liệu mẫu (sẽ được thay thế bằng dữ liệu thực)
        data = {
            'STT': [1, 2, 3],
            'CCCD': ['031089011929', '001087016369', '001184032114'],
            'Họ và tên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C'],
            'Ngày sinh': ['1990-01-01', '1985-05-15', '1992-12-25'],
            'Địa chỉ': ['Hà Nội', 'TP.HCM', 'Đà Nẵng'],
            'Mã BHXH': ['BHXH001', 'BHXH002', 'BHXH003']
        }
        
        # Tạo DataFrame
        df = pd.DataFrame(data)
        
        # Export Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Result', index=False)
        
        logger.info(f"✅ Export Excel thành công: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Lỗi export Excel: {e}")
        return False

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "result.xlsx"
    success = export_excel(output_file)
    sys.exit(0 if success else 1)
