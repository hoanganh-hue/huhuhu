#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cấu hình hệ thống
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class SystemConfig:
    """Cấu hình hệ thống"""
    
    # CCCD Configuration
    cccd_province_code: str = "01"  # Hà Nội
    cccd_gender: str = "female"
    cccd_birth_year_from: int = 1965
    cccd_birth_year_to: int = 1975
    cccd_count: int = 100
    
    # API Configuration
    check_cccd_api_url: str = "http://localhost:8000"
    check_cccd_api_key: str = ""
    captcha_api_key: str = "your_2captcha_api_key_here"
    
    # Output Configuration
    output_path: str = "output"
    excel_output_file: str = "final_report.xlsx"
    log_level: str = "INFO"
    
    # System Configuration
    max_workers: int = 4
    request_timeout: int = 30
    max_retries: int = 3


def get_config() -> SystemConfig:
    """Lấy cấu hình hệ thống"""
    config = SystemConfig()
    
    # Override từ environment variables
    config.cccd_province_code = os.getenv('CCCD_PROVINCE_CODE', config.cccd_province_code)
    config.cccd_gender = os.getenv('CCCD_GENDER', config.cccd_gender)
    config.cccd_birth_year_from = int(os.getenv('CCCD_BIRTH_YEAR_FROM', config.cccd_birth_year_from))
    config.cccd_birth_year_to = int(os.getenv('CCCD_BIRTH_YEAR_TO', config.cccd_birth_year_to))
    config.cccd_count = int(os.getenv('CCCD_COUNT', config.cccd_count))
    
    config.check_cccd_api_url = os.getenv('CHECK_CCCD_API_URL', config.check_cccd_api_url)
    config.check_cccd_api_key = os.getenv('CHECK_CCCD_API_KEY', config.check_cccd_api_key)
    config.captcha_api_key = os.getenv('CAPTCHA_API_KEY', config.captcha_api_key)
    
    config.output_path = os.getenv('OUTPUT_PATH', config.output_path)
    config.excel_output_file = os.getenv('EXCEL_OUTPUT_FILE', config.excel_output_file)
    config.log_level = os.getenv('LOG_LEVEL', config.log_level)
    
    return config


def validate_configuration(config: SystemConfig) -> Dict[str, Any]:
    """Kiểm tra tính hợp lệ của cấu hình"""
    errors = []
    warnings = []
    
    # Kiểm tra mã tỉnh
    if not config.cccd_province_code or len(config.cccd_province_code) != 2:
        errors.append("Mã tỉnh/thành phải có 2 chữ số")
    
    # Kiểm tra năm sinh
    if config.cccd_birth_year_from > config.cccd_birth_year_to:
        errors.append("Năm sinh bắt đầu phải nhỏ hơn năm sinh kết thúc")
    
    if config.cccd_birth_year_from < 1900 or config.cccd_birth_year_to > 2025:
        errors.append("Năm sinh phải trong khoảng 1900-2025")
    
    # Kiểm tra số lượng CCCD
    if config.cccd_count <= 0 or config.cccd_count > 10000:
        warnings.append("Số lượng CCCD nên trong khoảng 1-10000")
    
    # Kiểm tra API key
    if config.captcha_api_key == "your_2captcha_api_key_here":
        warnings.append("CAPTCHA API key chưa được cấu hình - BHXH lookup sẽ không hoạt động")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def get_output_file_path(self, filename: str) -> str:
    """Lấy đường dẫn file output"""
    output_dir = Path(self.output_path)
    output_dir.mkdir(exist_ok=True)
    return str(output_dir / filename)


def get_log_file_path(self) -> str:
    """Lấy đường dẫn file log"""
    return get_output_file_path(self, "system.log")


def print_configuration_summary(self):
    """In tóm tắt cấu hình"""
    print("\n" + "="*60)
    print("📋 CẤU HÌNH HỆ THỐNG")
    print("="*60)
    print(f"🏛️  Mã tỉnh/thành: {self.cccd_province_code}")
    print(f"👤 Giới tính: {self.cccd_gender}")
    print(f"📅 Năm sinh: {self.cccd_birth_year_from} - {self.cccd_birth_year_to}")
    print(f"🔢 Số lượng CCCD: {self.cccd_count}")
    print(f"🌐 Check CCCD API: {self.check_cccd_api_url}")
    print(f"📁 Thư mục output: {self.output_path}")
    print(f"📊 File Excel: {self.excel_output_file}")
    print("="*60)


# Monkey patch methods to SystemConfig
SystemConfig.get_output_file_path = get_output_file_path
SystemConfig.get_log_file_path = get_log_file_path
SystemConfig.print_configuration_summary = print_configuration_summary
SystemConfig.validate_configuration = lambda self: validate_configuration(self)