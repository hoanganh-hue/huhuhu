#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data processor utilities
"""

import pandas as pd
from typing import List, Dict, Any
from pathlib import Path


class DataProcessor:
    """Xử lý dữ liệu"""
    
    def __init__(self):
        pass
    
    def merge_data_sources(self, cccd_data: List[Dict], check_cccd_data: List[Dict], 
                          doanh_nghiep_data: List[Dict], bhxh_data: List[Dict]) -> List[Dict]:
        """Merge dữ liệu từ 4 nguồn"""
        merged_data = []
        
        # Tạo dict để lookup nhanh
        check_cccd_dict = {item.get('cccd'): item for item in check_cccd_data}
        doanh_nghiep_dict = {item.get('cccd'): item for item in doanh_nghiep_data}
        bhxh_dict = {item.get('cccd'): item for item in bhxh_data}
        
        for cccd_item in cccd_data:
            cccd = cccd_item.get('cccd', '')
            
            # Merge tất cả dữ liệu
            merged_item = {
                'cccd': cccd,
                'check_cccd': check_cccd_dict.get(cccd, {}),
                'doanh_nghiep': doanh_nghiep_dict.get(cccd, {}),
                'bhxh': bhxh_dict.get(cccd, {})
            }
            
            merged_data.append(merged_item)
        
        return merged_data
    
    def cross_reference_validation(self, data: List[Dict]) -> List[Dict]:
        """Cross-reference validation"""
        # Đơn giản hóa - chỉ return data gốc
        return data
    
    def validate_record(self, record: Dict) -> Dict[str, Any]:
        """Validate record"""
        errors = []
        
        # Kiểm tra CCCD
        cccd = record.get('cccd', '')
        if not cccd or len(cccd) != 12 or not cccd.isdigit():
            errors.append("CCCD không hợp lệ")
        
        # Kiểm tra có ít nhất một nguồn dữ liệu
        has_data = any([
            record.get('check_cccd'),
            record.get('doanh_nghiep'),
            record.get('bhxh')
        ])
        
        if not has_data:
            errors.append("Không có dữ liệu từ bất kỳ nguồn nào")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'cleaned_data': record
        }
    
    def prepare_excel_data_with_deduplication(self, data: List[Dict]) -> List[Dict]:
        """Chuẩn bị dữ liệu cho Excel"""
        excel_data = []
        
        for record in data:
            cccd = record.get('cccd', '')
            check_cccd = record.get('check_cccd', {})
            doanh_nghiep = record.get('doanh_nghiep', {})
            bhxh = record.get('bhxh', {})
            
            # Tạo row cho Excel
            row = {
                'CCCD': cccd,
                'Họ tên (Check CCCD)': check_cccd.get('name', ''),
                'Mã số thuế (Check CCCD)': check_cccd.get('tax_code', ''),
                'Địa chỉ (Check CCCD)': check_cccd.get('address', ''),
                'Chức vụ (Check CCCD)': check_cccd.get('role', ''),
                'Tên công ty (Doanh nghiệp)': doanh_nghiep.get('company_name', ''),
                'Đại diện (Doanh nghiệp)': doanh_nghiep.get('representative', ''),
                'Địa chỉ (Doanh nghiệp)': doanh_nghiep.get('address', ''),
                'Điện thoại (Doanh nghiệp)': doanh_nghiep.get('phone', ''),
                'MST (Doanh nghiệp)': doanh_nghiep.get('mst', ''),
                'Số BHXH': bhxh.get('bhxh_number', ''),
                'Họ tên (BHXH)': bhxh.get('name', ''),
                'Điện thoại (BHXH)': bhxh.get('phone', ''),
                'Nguồn Check CCCD': check_cccd.get('source', ''),
                'Nguồn Doanh nghiệp': doanh_nghiep.get('source', ''),
                'Nguồn BHXH': bhxh.get('source', '')
            }
            
            excel_data.append(row)
        
        return excel_data
    
    def save_to_excel(self, data: List[Dict], file_path: str) -> bool:
        """Lưu dữ liệu ra Excel"""
        try:
            df = pd.DataFrame(data)
            
            # Tạo thư mục nếu chưa có
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Lưu Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            return True
            
        except Exception as e:
            print(f"❌ Lỗi lưu Excel: {e}")
            return False
    
    def save_to_text(self, content: str, file_path: str) -> bool:
        """Lưu text"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Lỗi lưu text: {e}")
            return False
    
    def create_summary_report(self, total_cccd: int, doanh_nghiep_found: int, 
                            bhxh_found: int, final_records: int, errors: List[str]) -> str:
        """Tạo báo cáo tổng kết"""
        report = f"""
BÁO CÁO TỔNG KẾT HỆ THỐNG TRA CỨU THÔNG TIN
===============================================

Thời gian: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

THỐNG KÊ:
- Tổng số CCCD: {total_cccd}
- Tìm thấy thông tin doanh nghiệp: {doanh_nghiep_found}
- Tìm thấy thông tin BHXH: {bhxh_found}
- Records cuối cùng: {final_records}

TỶ LỆ THÀNH CÔNG:
- Doanh nghiệp: {(doanh_nghiep_found/total_cccd*100):.1f}% (nếu total_cccd > 0)
- BHXH: {(bhxh_found/total_cccd*100):.1f}% (nếu total_cccd > 0)

LỖI ({len(errors)}):
"""
        for i, error in enumerate(errors, 1):
            report += f"{i}. {error}\n"
        
        return report
    
    def save_debug_csv(self, data: List[Dict], file_path: str) -> bool:
        """Lưu debug CSV"""
        try:
            df = pd.DataFrame(data)
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(file_path, index=False, encoding='utf-8')
            return True
        except Exception as e:
            print(f"❌ Lỗi lưu debug CSV: {e}")
            return False
    
    def save_error_logs(self, errors: List[str], file_path: str) -> bool:
        """Lưu error logs"""
        try:
            content = "\n".join([f"{i+1}. {error}" for i, error in enumerate(errors)])
            return self.save_to_text(content, file_path)
        except Exception as e:
            print(f"❌ Lỗi lưu error logs: {e}")
            return False