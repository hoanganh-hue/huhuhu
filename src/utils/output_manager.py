#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output manager utilities
"""

from typing import Any, Dict, List
import json
from pathlib import Path


def get_output_manager():
    """Lấy output manager"""
    return OutputManager()


def save_to_output(data: Any, filename: str):
    """Lưu dữ liệu ra file"""
    manager = get_output_manager()
    return manager.save_data(data, filename)


def save_report(report: str, filename: str):
    """Lưu báo cáo"""
    manager = get_output_manager()
    return manager.save_report(report, filename)


def save_data(data: Any, filename: str):
    """Lưu dữ liệu"""
    return save_to_output(data, filename)


class OutputManager:
    """Quản lý output"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_data(self, data: Any, filename: str) -> str:
        """Lưu dữ liệu"""
        file_path = self.output_dir / filename
        
        if isinstance(data, (dict, list)):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        return str(file_path)
    
    def save_report(self, report: str, filename: str) -> str:
        """Lưu báo cáo"""
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        return str(file_path)