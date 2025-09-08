#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data processor utility module
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

class DataProcessor:
    """Data processing utilities."""
    
    def __init__(self):
        pass
    
    def merge_data_sources(self, cccd_data: List[Dict], check_cccd_data: List[Dict], 
                          doanh_nghiep_data: List[Dict], bhxh_data: List[Dict]) -> List[Dict]:
        """Merge data from multiple sources."""
        
        merged_data = []
        
        # Create lookup dictionaries
        check_cccd_lookup = {item.get('cccd'): item for item in check_cccd_data}
        doanh_nghiep_lookup = {item.get('cccd'): item for item in doanh_nghiep_data}
        bhxh_lookup = {item.get('cccd'): item for item in bhxh_data}
        
        for cccd_item in cccd_data:
            cccd = cccd_item.get('cccd')
            
            # Merge all data sources
            merged_record = {
                'cccd': cccd,
                'check_cccd_data': check_cccd_lookup.get(cccd, {}),
                'doanh_nghiep_data': doanh_nghiep_lookup.get(cccd, {}),
                'bhxh_data': bhxh_lookup.get(cccd, {})
            }
            
            merged_data.append(merged_record)
        
        return merged_data
    
    def cross_reference_validation(self, data: List[Dict]) -> List[Dict]:
        """Perform cross-reference validation."""
        # Simple validation - in real scenario this would be more complex
        return data
    
    def validate_record(self, record: Dict) -> Dict[str, Any]:
        """Validate a single record."""
        errors = []
        
        if not record.get('cccd'):
            errors.append("CCCD is required")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'cleaned_data': record
        }
    
    def prepare_excel_data_with_deduplication(self, data: List[Dict]) -> List[Dict]:
        """Prepare data for Excel export with deduplication."""
        # Simple deduplication by CCCD
        seen_cccds = set()
        deduplicated_data = []
        
        for record in data:
            cccd = record.get('cccd')
            if cccd and cccd not in seen_cccds:
                seen_cccds.add(cccd)
                deduplicated_data.append(record)
        
        return deduplicated_data
    
    def save_to_excel(self, data: List[Dict], file_path: str) -> bool:
        """Save data to Excel file."""
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            return False
    
    def save_to_text(self, content: str, file_path: str):
        """Save content to text file."""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_summary_report(self, total_cccd: int, doanh_nghiep_found: int, 
                            bhxh_found: int, final_records: int, errors: List[str]) -> str:
        """Create summary report."""
        return f"""
BÁO CÁO TỔNG KẾT HỆ THỐNG BHXH DATA TOOLS
==========================================

Thời gian: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

THỐNG KÊ:
- Tổng số CCCD tạo: {total_cccd}
- Tìm thấy thông tin doanh nghiệp: {doanh_nghiep_found}
- Tìm thấy thông tin BHXH: {bhxh_found}
- Records cuối cùng: {final_records}
- Số lỗi: {len(errors)}

LỖI (nếu có):
{chr(10).join([f"- {error}" for error in errors]) if errors else "Không có lỗi"}

==========================================
        """.strip()
    
    def save_debug_csv(self, data: List[Dict], file_path: str):
        """Save debug CSV file."""
        try:
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8')
        except Exception as e:
            print(f"Error saving debug CSV: {e}")
    
    def save_error_logs(self, errors: List[str], file_path: str):
        """Save error logs."""
        with open(file_path, 'w', encoding='utf-8') as f:
            for error in errors:
                f.write(f"{error}\n")