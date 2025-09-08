#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger utility module
"""

import logging
from typing import Optional

def get_logger(name: str, log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Get logger instance."""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

class WorkflowLogger:
    """Workflow logger for tracking steps."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def start_workflow(self, workflow_name: str):
        """Start workflow logging."""
        self.logger.info(f"🚀 Bắt đầu workflow: {workflow_name}")
    
    def end_workflow(self, workflow_name: str, success: bool, total_records: int = 0, error_count: int = 0):
        """End workflow logging."""
        status = "✅ Thành công" if success else "❌ Thất bại"
        self.logger.info(f"🏁 Kết thúc workflow: {workflow_name} - {status}")
        self.logger.info(f"📊 Tổng records: {total_records}, Lỗi: {error_count}")
    
    def start_step(self, step_name: str):
        """Start step logging."""
        self.logger.info(f"📋 {step_name}")
    
    def complete_step(self, data_count: int = 0):
        """Complete step logging."""
        self.logger.info(f"✅ Hoàn thành - {data_count} records")
    
    def error_step(self, error_msg: str):
        """Log step error."""
        self.logger.error(f"❌ Lỗi: {error_msg}")