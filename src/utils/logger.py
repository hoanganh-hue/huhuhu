#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ thống logging
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class WorkflowLogger:
    """Logger cho workflow"""
    
    def __init__(self, name: str = "workflow"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Tạo formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_file = Path("logs") / f"{name}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message)
    
    def start_step(self, step_name: str, **kwargs):
        """Bắt đầu một bước trong workflow"""
        self.logger.info(f"🚀 Bắt đầu: {step_name}")
    
    def complete_step(self, step_name: str = None, data_count: int = 0, **kwargs):
        """Hoàn thành một bước trong workflow"""
        if step_name:
            self.logger.info(f"✅ Hoàn thành: {step_name}")
        if data_count > 0:
            self.logger.info(f"📊 Số lượng dữ liệu: {data_count}")

def get_logger(name: str = "system") -> logging.Logger:
    """Lấy logger instance"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = Path("logs") / f"{name}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger