#!/usr/bin/env python3
"""
Script mẫu: Kiểm tra danh sách MST với API thongtindoanhnghiep.co
Dựa trên kế hoạch tích hợp vào workflow chính

Tác giả: MiniMax Agent
Ngày tạo: 2025-01-06
Phiên bản: 1.0.0
"""

import requests
import time
import pandas as pd
from typing import List, Dict, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MSTChecker:
    """
    Class kiểm tra danh sách MST với API thongtindoanhnghiep.co
    """
    
    def __init__(self, base_url: str = "https://thongtindoanhnghiep.co"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        })
    
    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def fetch_company_by_mst(self, mst: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin doanh nghiệp theo MST với retry logic
        
        Args:
            mst: Mã số thuế cần tra cứu
            
        Returns:
            Dict chứa thông tin doanh nghiệp hoặc None nếu không tìm thấy
        """
        try:
            url = f"{self.base_url}/api/company/{mst}"
            logger.info(f"🔍 Đang tra cứu MST: {mst}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Validation với trường "Title"
            if data and data.get('Title'):
                logger.info(f"✅ Tìm thấy doanh nghiệp: {data.get('Title')}")
                return data
            else:
                logger.warning(f"⚠️ MST {mst} không có trường Title hoặc dữ liệu rỗng")
                return None
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"❌ MST {mst} không tồn tại (404)")
                return None
            else:
                logger.error(f"❌ HTTP Error {e.response.status_code} cho MST {mst}: {e}")
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request Error cho MST {mst}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Lỗi không xác định cho MST {mst}: {e}")
            raise
    
    def extract_company_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trích xuất thông tin doanh nghiệp từ response API
        
        Args:
            data: Dữ liệu từ API response
            
        Returns:
            Dict chứa thông tin đã được chuẩn hóa
        """
        return {
            'mst': data.get('MaSoThue', ''),
            'company_name': data.get('Title', ''),
            'address': data.get('DiaChi', ''),
            'industry': data.get('NganhNghe', ''),
            'status': data.get('TrangThai', ''),
            'representative': data.get('DaiDienPhapLuat', ''),
            'phone': data.get('DienThoai', ''),
            'email': data.get('Email', ''),
            'website': data.get('Website', ''),
            'capital': data.get('VonDieuLe', ''),
            'establish_date': data.get('NgayCap', ''),
            'tax_office': data.get('CoQuanThue', '')
        }
    
    def process_mst_list(self, mst_list: List[str]) -> pd.DataFrame:
        """
        Xử lý danh sách MST và trả về DataFrame kết quả
        
        Args:
            mst_list: Danh sách các MST cần kiểm tra
            
        Returns:
            DataFrame chứa kết quả chi tiết
        """
        results = []
        total = len(mst_list)
        
        logger.info(f"🚀 Bắt đầu kiểm tra {total} MST...")
        
        for i, mst in enumerate(mst_list):
            logger.info(f"📊 Tiến độ: {i+1}/{total} - MST: {mst}")
            start_time = time.time()
            
            try:
                # Gọi API với retry logic
                company_data = self.fetch_company_by_mst(mst)
                response_time = (time.time() - start_time) * 1000  # ms
                
                if company_data:
                    # Trích xuất thông tin
                    company_info = self.extract_company_info(company_data)
                    company_info.update({
                        'mst_test_result': 'Found',
                        'api_response_time': response_time,
                        'validation_status': 'Success',
                        'raw_response': company_data  # Lưu raw response để debug
                    })
                    results.append(company_info)
                else:
                    # Không tìm thấy
                    results.append({
                        'mst': mst,
                        'mst_test_result': 'Not Found',
                        'api_response_time': response_time,
                        'validation_status': 'Not Found',
                        'company_name': None,
                        'address': None,
                        'industry': None,
                        'status': None,
                        'representative': None,
                        'phone': None,
                        'email': None,
                        'website': None,
                        'capital': None,
                        'establish_date': None,
                        'tax_office': None,
                        'raw_response': None
                    })
                
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                logger.error(f"💥 Lỗi khi xử lý MST {mst}: {e}")
                results.append({
                    'mst': mst,
                    'mst_test_result': 'Error',
                    'api_response_time': response_time,
                    'validation_status': 'Failed',
                    'error_message': str(e),
                    'company_name': None,
                    'address': None,
                    'industry': None,
                    'status': None,
                    'representative': None,
                    'phone': None,
                    'email': None,
                    'website': None,
                    'capital': None,
                    'establish_date': None,
                    'tax_office': None,
                    'raw_response': None
                })
            
            # Thêm delay để tránh rate limiting
            time.sleep(0.2)
        
        logger.info(f"✅ Hoàn tất kiểm tra {total} MST")
        
        # Tạo DataFrame
        df = pd.DataFrame(results)
        
        # Sắp xếp cột
        column_order = [
            'mst', 'mst_test_result', 'company_name', 'status', 
            'address', 'industry', 'representative', 'phone', 
            'email', 'website', 'capital', 'establish_date', 'tax_office',
            'api_response_time', 'validation_status', 'error_message', 'raw_response'
        ]
        
        # Chỉ lấy các cột tồn tại
        existing_columns = [col for col in column_order if col in df.columns]
        
        return df[existing_columns]
    
    def generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Tạo thống kê từ kết quả
        
        Args:
            df: DataFrame kết quả
            
        Returns:
            Dict chứa các thống kê
        """
        total = len(df)
        found = len(df[df['mst_test_result'] == 'Found'])
        not_found = len(df[df['mst_test_result'] == 'Not Found'])
        errors = len(df[df['mst_test_result'] == 'Error'])
        
        success_rate = (found / total * 100) if total > 0 else 0
        avg_response_time = df['api_response_time'].mean() if total > 0 else 0
        
        return {
            'total_processed': total,
            'found': found,
            'not_found': not_found,
            'errors': errors,
            'success_rate': round(success_rate, 2),
            'avg_response_time_ms': round(avg_response_time, 2),
            'total_time_seconds': round(df['api_response_time'].sum() / 1000, 2)
        }


def main():
    """
    Hàm main để test script
    """
    # Danh sách MST test
    test_mst_list = [
        '0101365409',  # FPT
        '0123456789',  # Test không tồn tại
        '0301234567',  # Test khác
        '0101234567',  # Test khác
        '9999999999'   # Test không tồn tại
    ]
    
    print("🚀 Bắt đầu test script check_mst_list.py")
    print("=" * 60)
    
    # Khởi tạo checker
    checker = MSTChecker()
    
    # Xử lý danh sách MST
    df_result = checker.process_mst_list(test_mst_list)
    
    # Tạo thống kê
    stats = checker.generate_statistics(df_result)
    
    # In kết quả
    print("\n📊 KẾT QUẢ CHI TIẾT:")
    print(df_result.to_string(index=False))
    
    print("\n📈 THỐNG KÊ:")
    print(f"   Tổng số MST: {stats['total_processed']}")
    print(f"   Tìm thấy: {stats['found']}")
    print(f"   Không tìm thấy: {stats['not_found']}")
    print(f"   Lỗi: {stats['errors']}")
    print(f"   Tỷ lệ thành công: {stats['success_rate']}%")
    print(f"   Thời gian phản hồi TB: {stats['avg_response_time_ms']}ms")
    print(f"   Tổng thời gian: {stats['total_time_seconds']}s")
    
    # Lưu kết quả
    output_file = 'mst_check_results.xlsx'
    df_result.to_excel(output_file, index=False)
    print(f"\n💾 Đã lưu kết quả vào: {output_file}")
    
    # Lưu CSV debug
    csv_file = 'mst_check_debug.csv'
    df_result.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"💾 Đã lưu debug CSV vào: {csv_file}")


if __name__ == "__main__":
    main()