"""
Module BHXH - Tra cứu thông tin Bảo hiểm Xã hội
Tích hợp với dữ liệu BHXH thực tế
"""

import pandas as pd
import logging
import json
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
import re

logger = logging.getLogger(__name__)

@dataclass
class BHXHResult:
    """Kết quả tra cứu BHXH"""
    ma_dinh_danh: str
    status: str  # "found", "not_found", "error"
    ho_ten: Optional[str] = None
    dia_chi: Optional[str] = None
    ma_so_thue: Optional[str] = None
    dien_thoai: Optional[str] = None
    nguoi_dai_dien: Optional[str] = None
    tinh_trang: Optional[str] = None
    loai_hinh_dn: Optional[str] = None
    ngay_hoat_dong: Optional[str] = None
    co_quan_thue: Optional[str] = None
    ngay_thay_doi: Optional[str] = None
    ghi_chu: Optional[str] = None
    error: Optional[str] = None
    source: str = "bhxh_database"
    additional_info: Dict[str, Any] = field(default_factory=dict)

class BHXHLookupService:
    """Service tra cứu thông tin BHXH"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bhxh_data_file = config.get('bhxh_data_file', 'bhxh-hn-3.xlsx')
        self.bhxh_data = None
        self._load_bhxh_data()
        logger.info("✅ BHXH Lookup Service initialized")
    
    def _load_bhxh_data(self):
        """Load dữ liệu BHXH từ file Excel"""
        try:
            if os.path.exists(self.bhxh_data_file):
                self.bhxh_data = pd.read_excel(self.bhxh_data_file)
                logger.info(f"✅ Loaded BHXH data: {len(self.bhxh_data)} records from {self.bhxh_data_file}")
            else:
                logger.warning(f"⚠️ BHXH data file not found: {self.bhxh_data_file}")
                self.bhxh_data = pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error loading BHXH data: {e}")
            self.bhxh_data = pd.DataFrame()
    
    def _clean_identifier(self, identifier: str) -> str:
        """Làm sạch mã định danh"""
        if pd.isna(identifier):
            return ""
        return str(identifier).strip().replace("'", "")
    
    def _clean_name(self, name: str) -> str:
        """Làm sạch tên"""
        if pd.isna(name):
            return ""
        return str(name).strip()
    
    def lookup_by_identifier(self, ma_dinh_danh: str) -> BHXHResult:
        """Tra cứu thông tin BHXH theo mã định danh"""
        result = BHXHResult(ma_dinh_danh=ma_dinh_danh, status="not_found")
        
        try:
            if self.bhxh_data is None or self.bhxh_data.empty:
                result.error = "BHXH data not loaded"
                result.status = "error"
                return result
            
            # Làm sạch mã định danh tìm kiếm
            search_id = self._clean_identifier(ma_dinh_danh)
            
            # Tìm kiếm chính xác
            found_records = self.bhxh_data[
                self.bhxh_data['Số CMT/Thẻ căn cước'].apply(
                    lambda x: self._clean_identifier(x) == search_id
                )
            ]
            
            if len(found_records) > 0:
                # Lấy bản ghi đầu tiên
                record = found_records.iloc[0]
                
                result.status = "found"
                result.ho_ten = self._clean_name(record.get('Tên người nộp thuế', ''))
                result.dia_chi = self._clean_name(record.get('Địa chỉ', ''))
                result.ma_so_thue = self._clean_identifier(record.get('Mã Số Thuế', ''))
                result.dien_thoai = self._clean_identifier(record.get('Điện thoại', ''))
                result.nguoi_dai_dien = self._clean_name(record.get('Người đại diện', ''))
                result.tinh_trang = self._clean_name(record.get('Tình trạng', ''))
                result.loai_hinh_dn = self._clean_name(record.get('Loại hình DN', ''))
                result.ngay_hoat_dong = self._clean_name(record.get('Ngày hoạt động', ''))
                result.co_quan_thue = self._clean_name(record.get('Cơ quan thuế', ''))
                result.ngay_thay_doi = self._clean_name(record.get('Ngày thay đổi thông tin gần nhất', ''))
                result.ghi_chu = self._clean_name(record.get('Ghi chú', ''))
                
                # Thêm thông tin bổ sung
                result.additional_info = {
                    'trụ_sở': self._clean_name(record.get('Trụ sở', '')),
                    'tên_quốc_tế': self._clean_name(record.get('Tên quốc tế', '')),
                    'ngành_nghề_chính': self._clean_name(record.get('Ngành nghề chính', '')),
                    'mã_số_doanh_nghiệp': self._clean_identifier(record.get('Mã số doanh nghiệp (Chi tiết GDT)', '')),
                    'ngày_cấp': self._clean_name(record.get('Ngày cấp (Chi tiết GDT)', '')),
                    'tên_chính_thức': self._clean_name(record.get('Tên chính thức (Chi tiết GDT)', '')),
                    'tên_giao_dịch': self._clean_name(record.get('Tên giao dịch (Chi tiết GDT)', ''))
                }
                
                logger.info(f"✅ Found BHXH info for {ma_dinh_danh}: {result.ho_ten}")
                
            else:
                # Tìm kiếm gần đúng
                partial_matches = self.bhxh_data[
                    self.bhxh_data['Số CMT/Thẻ căn cước'].apply(
                        lambda x: search_id in self._clean_identifier(x) if len(search_id) >= 6 else False
                    )
                ]
                
                if len(partial_matches) > 0:
                    result.error = f"No exact match found, but found {len(partial_matches)} partial matches"
                    result.additional_info = {
                        'partial_matches': [
                            {
                                'ma_dinh_danh': self._clean_identifier(record.get('Số CMT/Thẻ căn cước', '')),
                                'ho_ten': self._clean_name(record.get('Tên người nộp thuế', ''))
                            }
                            for _, record in partial_matches.head(3).iterrows()
                        ]
                    }
                else:
                    result.error = "No records found for this identifier"
                
                logger.warning(f"⚠️ No exact match for {ma_dinh_danh}")
                
        except Exception as e:
            result.error = f"Lookup error: {str(e)}"
            result.status = "error"
            logger.error(f"❌ Error looking up BHXH info for {ma_dinh_danh}: {e}")
        
        return result
    
    def lookup_by_name(self, ho_ten: str) -> List[BHXHResult]:
        """Tra cứu thông tin BHXH theo tên"""
        results = []
        
        try:
            if self.bhxh_data is None or self.bhxh_data.empty:
                error_result = BHXHResult(ma_dinh_danh="", status="error", error="BHXH data not loaded")
                results.append(error_result)
                return results
            
            # Làm sạch tên tìm kiếm
            search_name = self._clean_name(ho_ten).lower()
            
            # Tìm kiếm
            found_records = self.bhxh_data[
                self.bhxh_data['Tên người nộp thuế'].apply(
                    lambda x: search_name in self._clean_name(x).lower()
                )
            ]
            
            for _, record in found_records.iterrows():
                result = BHXHResult(
                    ma_dinh_danh=self._clean_identifier(record.get('Số CMT/Thẻ căn cước', '')),
                    status="found",
                    ho_ten=self._clean_name(record.get('Tên người nộp thuế', '')),
                    dia_chi=self._clean_name(record.get('Địa chỉ', '')),
                    ma_so_thue=self._clean_identifier(record.get('Mã Số Thuế', '')),
                    dien_thoai=self._clean_identifier(record.get('Điện thoại', '')),
                    nguoi_dai_dien=self._clean_name(record.get('Người đại diện', '')),
                    tinh_trang=self._clean_name(record.get('Tình trạng', '')),
                    loai_hinh_dn=self._clean_name(record.get('Loại hình DN', '')),
                    ngay_hoat_dong=self._clean_name(record.get('Ngày hoạt động', '')),
                    co_quan_thue=self._clean_name(record.get('Cơ quan thuế', '')),
                    ngay_thay_doi=self._clean_name(record.get('Ngày thay đổi thông tin gần nhất', '')),
                    ghi_chu=self._clean_name(record.get('Ghi chú', ''))
                )
                results.append(result)
            
            logger.info(f"✅ Found {len(results)} BHXH records for name: {ho_ten}")
            
        except Exception as e:
            error_result = BHXHResult(ma_dinh_danh="", status="error", error=f"Name lookup error: {str(e)}")
            results.append(error_result)
            logger.error(f"❌ Error looking up BHXH info by name {ho_ten}: {e}")
        
        return results
    
    def batch_lookup(self, identifiers: List[str]) -> List[BHXHResult]:
        """Tra cứu hàng loạt mã định danh"""
        results = []
        
        logger.info(f"🔄 Starting batch BHXH lookup for {len(identifiers)} identifiers")
        
        for i, identifier in enumerate(identifiers, 1):
            logger.info(f"🔄 Processing {i}/{len(identifiers)}: {identifier}")
            result = self.lookup_by_identifier(identifier)
            results.append(result)
        
        logger.info(f"✅ Batch BHXH lookup completed: {len(results)} results")
        return results
    
    def save_results(self, results: List[BHXHResult], output_file: str = "bhxh_lookup_results.json"):
        """Lưu kết quả tra cứu BHXH"""
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / output_file
        
        try:
            # Convert dataclass to dict for JSON serialization
            results_data = []
            for result in results:
                result_dict = {
                    'ma_dinh_danh': result.ma_dinh_danh,
                    'status': result.status,
                    'ho_ten': result.ho_ten,
                    'dia_chi': result.dia_chi,
                    'ma_so_thue': result.ma_so_thue,
                    'dien_thoai': result.dien_thoai,
                    'nguoi_dai_dien': result.nguoi_dai_dien,
                    'tinh_trang': result.tinh_trang,
                    'loai_hinh_dn': result.loai_hinh_dn,
                    'ngay_hoat_dong': result.ngay_hoat_dong,
                    'co_quan_thue': result.co_quan_thue,
                    'ngay_thay_doi': result.ngay_thay_doi,
                    'ghi_chu': result.ghi_chu,
                    'error': result.error,
                    'source': result.source,
                    'additional_info': result.additional_info
                }
                results_data.append(result_dict)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Saved {len(results)} BHXH results to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving BHXH results: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê dữ liệu BHXH"""
        if self.bhxh_data is None or self.bhxh_data.empty:
            return {"error": "No data loaded"}
        
        stats = {
            "total_records": len(self.bhxh_data),
            "columns": list(self.bhxh_data.columns),
            "sample_identifiers": self.bhxh_data['Số CMT/Thẻ căn cước'].head(5).tolist(),
            "sample_names": self.bhxh_data['Tên người nộp thuế'].head(5).tolist()
        }
        
        return stats

if __name__ == "__main__":
    # Test configuration
    test_config = {
        'bhxh_data_file': 'bhxh-hn-3.xlsx'
    }
    
    # Initialize service
    service = BHXHLookupService(test_config)
    
    # Test with sample identifier
    test_identifier = "8087485671"
    result = service.lookup_by_identifier(test_identifier)
    
    print(f"Test result for {test_identifier}:")
    print(f"Status: {result.status}")
    print(f"Họ tên: {result.ho_ten}")
    print(f"Địa chỉ: {result.dia_chi}")
    print(f"Mã số thuế: {result.ma_so_thue}")
    print(f"Error: {result.error}")