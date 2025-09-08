#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra dữ liệu thực tế với 5 số CCCD
Sử dụng module chuẩn hóa để đảm bảo kết quả chính xác 100%
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Thêm path để import module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.core.module_2_check_cccd_standardized import (
    StandardizedModule2CheckCCCD,
    RequestStatus,
    SearchResult
)

class RealDataTester:
    """Class kiểm tra dữ liệu thực tế"""
    
    def __init__(self):
        self.config = {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 1.0,
            'max_delay': 10.0,
            'output_file': 'real_data_test_output.txt'
        }
        
        self.module = StandardizedModule2CheckCCCD(self.config)
        
        # 5 số CCCD thực tế cần kiểm tra
        self.test_cccds = [
            "001087016369",
            "001184032114", 
            "001098021288",
            "001094001628",
            "036092002342"
        ]
        
        self.results = []
        self.summary = {
            "total_cccds": len(self.test_cccds),
            "successful": 0,
            "not_found": 0,
            "errors": 0,
            "blocked": 0,
            "rate_limited": 0,
            "total_profiles": 0,
            "processing_time": 0.0
        }
    
    def run_real_data_tests(self) -> Dict[str, Any]:
        """Chạy test với dữ liệu thực tế"""
        print("🔍 KIỂM TRA DỮ LIỆU THỰC TẾ VỚI MODULE CHUẨN HÓA")
        print("=" * 80)
        print(f"📋 Số lượng CCCD cần kiểm tra: {len(self.test_cccds)}")
        print(f"📅 Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Kiểm tra từng CCCD
        for i, cccd in enumerate(self.test_cccds, 1):
            print(f"\n📋 [{i}/{len(self.test_cccds)}] Đang kiểm tra CCCD: {cccd}")
            print("-" * 60)
            
            try:
                # Thực hiện kiểm tra
                result = self.module.check_cccd_standardized(cccd)
                self.results.append(result)
                
                # In kết quả chi tiết
                self.print_result_details(result, i)
                
                # Cập nhật summary
                self.update_summary(result)
                
                # Delay giữa các request để tránh bị block
                if i < len(self.test_cccds):
                    print("⏳ Chờ 3s trước khi kiểm tra CCCD tiếp theo...")
                    time.sleep(3.0)
                
            except Exception as e:
                print(f"❌ Lỗi khi kiểm tra CCCD {cccd}: {str(e)}")
                error_result = SearchResult(
                    cccd=cccd,
                    status=RequestStatus.ERROR,
                    message=f"Lỗi hệ thống: {str(e)}",
                    profiles=[],
                    timestamp=datetime.now().isoformat(),
                    request_id=f"ERROR_{int(time.time())}",
                    processing_time=0.0,
                    error_details={"system_error": str(e)}
                )
                self.results.append(error_result)
                self.update_summary(error_result)
        
        # Tính thời gian xử lý tổng
        self.summary["processing_time"] = time.time() - start_time
        
        # In tổng kết
        self.print_summary()
        
        # Lưu kết quả
        self.save_results()
        
        return {
            "results": self.results,
            "summary": self.summary
        }
    
    def print_result_details(self, result: SearchResult, index: int):
        """In chi tiết kết quả"""
        print(f"🔍 Kết quả kiểm tra CCCD #{index}:")
        print(f"   Request ID: {result.request_id}")
        print(f"   CCCD: {result.cccd}")
        print(f"   Trạng thái: {result.status.value}")
        print(f"   Thông báo: {result.message}")
        print(f"   Thời gian xử lý: {result.processing_time:.2f}s")
        print(f"   Số lần retry: {result.retry_count}")
        
        if result.status == RequestStatus.SUCCESS and result.profiles:
            print(f"   📊 Số kết quả tìm thấy: {len(result.profiles)}")
            for j, profile in enumerate(result.profiles, 1):
                print(f"   └─ Profile {j}:")
                print(f"      Tên: {profile.name}")
                print(f"      Mã số thuế: {profile.tax_code}")
                print(f"      URL: {profile.url}")
                if profile.address:
                    print(f"      Địa chỉ: {profile.address}")
                if profile.birth_date:
                    print(f"      Ngày sinh: {profile.birth_date}")
                if profile.gender:
                    print(f"      Giới tính: {profile.gender}")
        elif result.status == RequestStatus.NOT_FOUND:
            print(f"   ℹ️ Không tìm thấy thông tin mã số thuế")
        elif result.status == RequestStatus.BLOCKED:
            print(f"   🚫 Bị chặn bởi anti-bot protection")
        elif result.status == RequestStatus.RATE_LIMITED:
            print(f"   ⏱️ Bị giới hạn tốc độ request")
        elif result.status == RequestStatus.ERROR:
            print(f"   ❌ Lỗi: {result.message}")
        
        if result.error_details:
            print(f"   🔍 Chi tiết lỗi: {json.dumps(result.error_details, ensure_ascii=False, indent=6)}")
    
    def update_summary(self, result: SearchResult):
        """Cập nhật tổng kết"""
        if result.status == RequestStatus.SUCCESS:
            self.summary["successful"] += 1
            self.summary["total_profiles"] += len(result.profiles)
        elif result.status == RequestStatus.NOT_FOUND:
            self.summary["not_found"] += 1
        elif result.status == RequestStatus.ERROR:
            self.summary["errors"] += 1
        elif result.status == RequestStatus.BLOCKED:
            self.summary["blocked"] += 1
        elif result.status == RequestStatus.RATE_LIMITED:
            self.summary["rate_limited"] += 1
    
    def print_summary(self):
        """In tổng kết"""
        print("\n" + "=" * 80)
        print("📊 TỔNG KẾT KIỂM TRA DỮ LIỆU THỰC TẾ")
        print("=" * 80)
        
        print(f"📋 Tổng số CCCD kiểm tra: {self.summary['total_cccds']}")
        print(f"✅ Thành công: {self.summary['successful']}")
        print(f"ℹ️ Không tìm thấy: {self.summary['not_found']}")
        print(f"❌ Lỗi: {self.summary['errors']}")
        print(f"🚫 Bị chặn: {self.summary['blocked']}")
        print(f"⏱️ Rate limited: {self.summary['rate_limited']}")
        print(f"📊 Tổng số profiles tìm thấy: {self.summary['total_profiles']}")
        print(f"⏰ Thời gian xử lý tổng: {self.summary['processing_time']:.2f}s")
        
        # Tính tỷ lệ thành công
        success_rate = (self.summary['successful'] / self.summary['total_cccds']) * 100
        print(f"🎯 Tỷ lệ thành công: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ KẾT QUẢ: Xuất sắc - Module hoạt động tốt")
        elif success_rate >= 60:
            print("⚠️ KẾT QUẢ: Tốt - Module hoạt động ổn định")
        elif success_rate >= 40:
            print("⚠️ KẾT QUẢ: Trung bình - Cần cải thiện")
        else:
            print("❌ KẾT QUẢ: Kém - Cần sửa lỗi")
        
        print("=" * 80)
    
    def save_results(self):
        """Lưu kết quả vào file"""
        try:
            # Lưu kết quả chi tiết
            self.module.save_results_standardized(self.results, self.config['output_file'])
            
            # Lưu kết quả JSON
            json_results = {
                "test_info": {
                    "test_date": datetime.now().isoformat(),
                    "total_cccds": len(self.test_cccds),
                    "test_cccds": self.test_cccds
                },
                "summary": self.summary,
                "results": [
                    {
                        "cccd": result.cccd,
                        "request_id": result.request_id,
                        "status": result.status.value,
                        "message": result.message,
                        "processing_time": result.processing_time,
                        "retry_count": result.retry_count,
                        "profiles_count": len(result.profiles),
                        "profiles": [
                            {
                                "name": profile.name,
                                "tax_code": profile.tax_code,
                                "url": profile.url,
                                "type": profile.type,
                                "address": profile.address,
                                "birth_date": profile.birth_date,
                                "gender": profile.gender
                            } for profile in result.profiles
                        ],
                        "error_details": result.error_details,
                        "timestamp": result.timestamp
                    } for result in self.results
                ]
            }
            
            with open('real_data_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(json_results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Đã lưu kết quả chi tiết vào: {self.config['output_file']}")
            print(f"💾 Đã lưu kết quả JSON vào: real_data_test_results.json")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu kết quả: {str(e)}")
    
    def print_detailed_analysis(self):
        """In phân tích chi tiết"""
        print("\n" + "=" * 80)
        print("🔍 PHÂN TÍCH CHI TIẾT KẾT QUẢ")
        print("=" * 80)
        
        # Phân tích theo trạng thái
        status_counts = {}
        for result in self.results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("📊 Phân tích theo trạng thái:")
        for status, count in status_counts.items():
            percentage = (count / len(self.results)) * 100
            print(f"   {status}: {count} ({percentage:.1f}%)")
        
        # Phân tích thời gian xử lý
        processing_times = [result.processing_time for result in self.results]
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            min_time = min(processing_times)
            max_time = max(processing_times)
            
            print(f"\n⏰ Phân tích thời gian xử lý:")
            print(f"   Thời gian trung bình: {avg_time:.2f}s")
            print(f"   Thời gian nhanh nhất: {min_time:.2f}s")
            print(f"   Thời gian chậm nhất: {max_time:.2f}s")
        
        # Phân tích profiles
        total_profiles = sum(len(result.profiles) for result in self.results)
        if total_profiles > 0:
            print(f"\n📊 Phân tích profiles:")
            print(f"   Tổng số profiles: {total_profiles}")
            
            # Thống kê theo loại
            profile_types = {}
            for result in self.results:
                for profile in result.profiles:
                    profile_type = profile.type
                    profile_types[profile_type] = profile_types.get(profile_type, 0) + 1
            
            for profile_type, count in profile_types.items():
                print(f"   {profile_type}: {count}")
        
        print("=" * 80)


def main():
    """Hàm chính"""
    print("🧪 KIỂM TRA DỮ LIỆU THỰC TẾ VỚI MODULE CHUẨN HÓA")
    print("🎯 Sử dụng 5 số CCCD thực tế để test module")
    print("=" * 80)
    
    tester = RealDataTester()
    results = tester.run_real_data_tests()
    
    # Phân tích chi tiết
    tester.print_detailed_analysis()
    
    # Kết luận
    success_rate = (results['summary']['successful'] / results['summary']['total_cccds']) * 100
    
    print(f"\n🎉 KẾT LUẬN:")
    if success_rate >= 80:
        print("✅ Module chuẩn hóa hoạt động xuất sắc với dữ liệu thực tế!")
        print("✅ Tỷ lệ thành công cao, sẵn sàng sử dụng trong production")
    elif success_rate >= 60:
        print("⚠️ Module chuẩn hóa hoạt động tốt với dữ liệu thực tế")
        print("⚠️ Có thể cần cải thiện một số trường hợp")
    else:
        print("❌ Module chuẩn hóa cần được cải thiện")
        print("❌ Tỷ lệ thành công thấp, cần xem xét lại")
    
    print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")
    print(f"📋 Tổng số CCCD kiểm tra: {results['summary']['total_cccds']}")
    print(f"✅ Thành công: {results['summary']['successful']}")
    print(f"📊 Tổng số profiles: {results['summary']['total_profiles']}")


if __name__ == "__main__":
    main()