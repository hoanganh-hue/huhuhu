#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration settings for the BHXH Data Tools system
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Config:
    """Main configuration class."""
    
    # Project settings
    project_name: str = "BHXH Data Tools"
    version: str = "2.0.0"
    environment: str = "production"
    
    # API URLs
    check_cccd_api_url: str = "http://localhost:8000"
    check_cccd_api_key: str = "dev-api-key-123"
    
    # CCCD Generation settings
    cccd_province_code: str = "31"  # Hải Phòng
    cccd_gender: Optional[str] = "female"  # None for all, "male", "female"
    cccd_birth_year_from: int = 1965
    cccd_birth_year_to: int = 1975
    cccd_count: int = 2000
    
    # CAPTCHA settings
    captcha_api_key: str = "your_2captcha_api_key_here"
    
    # Output settings
    output_path: str = "output"
    excel_output_file: str = "bhxh_data_results.xlsx"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/system.log"
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Create output directory if it doesn't exist
        Path(self.output_path).mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)
    
    def get_output_file_path(self, filename: str) -> str:
        """Get full path for output file."""
        return str(Path(self.output_path) / filename)
    
    def get_log_file_path(self) -> str:
        """Get full path for log file."""
        return str(Path(self.log_file))
    
    def print_configuration_summary(self):
        """Print configuration summary."""
        print("=" * 80)
        print("📋 CẤU HÌNH HỆ THỐNG")
        print("=" * 80)
        print(f"🏷️  Tên dự án: {self.project_name}")
        print(f"📦 Phiên bản: {self.version}")
        print(f"🌍 Môi trường: {self.environment}")
        print(f"🔗 Check CCCD API: {self.check_cccd_api_url}")
        print(f"📍 Mã tỉnh CCCD: {self.cccd_province_code}")
        print(f"👤 Giới tính: {self.cccd_gender if self.cccd_gender else 'Tất cả'}")
        print(f"📅 Năm sinh: {self.cccd_birth_year_from} - {self.cccd_birth_year_to}")
        print(f"🔢 Số lượng CCCD: {self.cccd_count}")
        print(f"📁 Thư mục output: {self.output_path}")
        print(f"📊 File Excel: {self.excel_output_file}")
        print("=" * 80)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration settings."""
        errors = []
        warnings = []
        
        # Check API URL
        if not self.check_cccd_api_url:
            errors.append("Check CCCD API URL không được để trống")
        
        # Check CCCD settings
        if self.cccd_count <= 0:
            errors.append("Số lượng CCCD phải lớn hơn 0")
        
        if self.cccd_birth_year_from > self.cccd_birth_year_to:
            errors.append("Năm sinh từ phải nhỏ hơn hoặc bằng năm sinh đến")
        
        # Check CAPTCHA API key
        if not self.captcha_api_key or self.captcha_api_key == "your_2captcha_api_key_here":
            warnings.append("CAPTCHA API key chưa được cấu hình - BHXH lookup sẽ bị vô hiệu hóa")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# Global configuration instance
_config: Optional[Config] = None

def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config

def set_config(config: Config):
    """Set global configuration instance."""
    global _config
    _config = config

def load_config_from_env():
    """Load configuration from environment variables."""
    config = Config()
    
    # Override with environment variables if they exist
    config.check_cccd_api_url = os.getenv("CHECK_CCCD_API_URL", config.check_cccd_api_url)
    config.check_cccd_api_key = os.getenv("CHECK_CCCD_API_KEY", config.check_cccd_api_key)
    config.captcha_api_key = os.getenv("CAPTCHA_API_KEY", config.captcha_api_key)
    config.cccd_province_code = os.getenv("CCCD_PROVINCE_CODE", config.cccd_province_code)
    config.cccd_gender = os.getenv("CCCD_GENDER", config.cccd_gender)
    config.cccd_birth_year_from = int(os.getenv("CCCD_BIRTH_YEAR_FROM", config.cccd_birth_year_from))
    config.cccd_birth_year_to = int(os.getenv("CCCD_BIRTH_YEAR_TO", config.cccd_birth_year_to))
    config.cccd_count = int(os.getenv("CCCD_COUNT", config.cccd_count))
    config.output_path = os.getenv("OUTPUT_PATH", config.output_path)
    config.log_level = os.getenv("LOG_LEVEL", config.log_level)
    
    set_config(config)
    return config