#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cấu hình hệ thống
"""

import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Class quản lý cấu hình hệ thống"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.output_dir = self.base_dir / "output"
        self.logs_dir = self.base_dir / "logs"
        
        # Tạo thư mục nếu chưa có
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Cấu hình các module
        self.check_cccd_api_url = "https://masothue.com"
        self.check_cccd_api_key = ""  # Không cần API key cho masothue.com
        
        # Cấu hình timeout và retry
        self.default_timeout = 30
        self.default_max_retries = 3
        
        # Cấu hình output files
        self.output_files = {
            "module_1_output": "module_1_output.txt",
            "module_2_check_cccd_output": "module_2_check_cccd_output.txt",
            "module_3_doanh_nghiep_output": "module_3_doanh_nghiep_output.txt",
            "module_4_bhxh_output": "module_4_bhxh_output.txt",
            "summary_report": "summary_report.txt",
            "excel_output": "output.xlsx"
        }
    
    def get_output_file_path(self, filename: str) -> Path:
        """Lấy đường dẫn file output"""
        return self.output_dir / filename
    
    def get_log_file_path(self, filename: str) -> Path:
        """Lấy đường dẫn file log"""
        return self.logs_dir / filename

# Instance global
config = Config()

def get_config() -> Config:
    """Lấy instance cấu hình"""
    return config