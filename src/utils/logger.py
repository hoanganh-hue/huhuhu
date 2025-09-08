#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger utilities
"""

import logging
import sys
from datetime import datetime
from typing import Optional


def get_logger(name: str, log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Tạo logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class WorkflowLogger:
    """Logger cho workflow"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.workflow_start_time = None
        self.step_start_time = None
    
    def start_workflow(self, workflow_name: str):
        """Bắt đầu workflow"""
        self.workflow_start_time = datetime.now()
        self.logger.info(f"🚀 Bắt đầu workflow: {workflow_name}")
    
    def end_workflow(self, workflow_name: str, success: bool, total_records: int = 0, error_count: int = 0):
        """Kết thúc workflow"""
        if self.workflow_start_time:
            duration = datetime.now() - self.workflow_start_time
            status = "✅ THÀNH CÔNG" if success else "❌ THẤT BẠI"
            self.logger.info(f"🏁 Kết thúc workflow: {workflow_name} - {status}")
            self.logger.info(f"⏱️  Thời gian thực hiện: {duration.total_seconds():.2f}s")
            self.logger.info(f"📊 Tổng records: {total_records}, Lỗi: {error_count}")
    
    def start_step(self, step_name: str):
        """Bắt đầu bước"""
        self.step_start_time = datetime.now()
        self.logger.info(f"📋 {step_name}")
    
    def complete_step(self, data_count: int = 0):
        """Hoàn thành bước"""
        if self.step_start_time:
            duration = datetime.now() - self.step_start_time
            self.logger.info(f"✅ Hoàn thành - {data_count} records ({duration.total_seconds():.2f}s)")
    
    def error_step(self, error_msg: str):
        """Lỗi trong bước"""
        if self.step_start_time:
            duration = datetime.now() - self.step_start_time
            self.logger.error(f"❌ Lỗi sau {duration.total_seconds():.2f}s: {error_msg}")