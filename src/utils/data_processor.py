#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xử lý dữ liệu
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class DataProcessor:
    """Class xử lý dữ liệu"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def save_to_text(self, content: str, file_path: Path):
        """Lưu nội dung vào file text"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Lỗi khi lưu file {file_path}: {e}")
    
    def save_to_json(self, data: Any, file_path: Path):
        """Lưu dữ liệu vào file JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu file JSON {file_path}: {e}")
    
    def merge_data(self, *data_sources: List[Dict]) -> List[Dict]:
        """Merge dữ liệu từ nhiều nguồn"""
        # Implementation đơn giản - có thể mở rộng sau
        merged = []
        for source in data_sources:
            merged.extend(source)
        return merged