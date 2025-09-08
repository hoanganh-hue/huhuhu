#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra lại 5 CCCD với module gốc
Để xem có thể lấy được dữ liệu thực tế không
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Thêm path để import module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.core.module_2_check_cccd import Module2CheckCCCD

class OriginalModuleTester:
    """Class kiểm tra với module gốc"""
    
    def __init__(self):
        self.config = {
            'timeout': 30,
            'max_retries': 3,
            'output_file': 'original_module_test_output.txt'
        }
        
        self.module = Module2CheckCCCD(self.config)
        
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
            "total_profiles": 0,
            "processing_time": 0.0
        }
    
    def run_original_module_tests(self) -> Dict[str, Any]:
        """Chạy test với module gốc"""
        print("🔍 KIỂM TRA LẠI VỚI MODULE GỐC")
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
                # Thực hiện kiểm tra với module gốc
                result = self.module.check_cccd(cccd)
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
                error_result = {
                    "cccd": cccd,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
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
    
    def print_result_details(self, result: Dict[str, Any], index: int):
        """In chi tiết kết quả"""
        print(f"🔍 Kết quả kiểm tra CCCD #{index}:")
        print(f"   CCCD: {result.get('cccd', 'N/A')}")
        print(f"   Trạng thái: {result.get('status', 'N/A')}")
        print(f"   Thông báo: {result.get('message', result.get('error', 'N/A'))}")
        print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
        
        if result.get('status') == 'found' and result.get('profiles'):
            profiles = result['profiles']
            print(f"   📊 Số kết quả tìm thấy: {len(profiles)}")
            for j, profile in enumerate(profiles, 1):
                print(f"   └─ Profile {j}:")
                print(f"      Tên: {profile.get('name', 'N/A')}")
                print(f"      Mã số thuế: {profile.get('tax_code', 'N/A')}")
                print(f"      URL: {profile.get('url', 'N/A')}")
                if profile.get('address'):
                    print(f"      Địa chỉ: {profile.get('address')}")
                if profile.get('birth_date'):
                    print(f"      Ngày sinh: {profile.get('birth_date')}")
                if profile.get('gender'):
                    print(f"      Giới tính: {profile.get('gender')}")
        elif result.get('status') == 'not_found':
            print(f"   ℹ️ Không tìm thấy thông tin mã số thuế")
        elif result.get('status') == 'error':
            print(f"   ❌ Lỗi: {result.get('error', 'Lỗi không xác định')}")
        
        # In toàn bộ result để debug
        print(f"   🔍 Raw result: {json.dumps(result, ensure_ascii=False, indent=6)}")
    
    def update_summary(self, result: Dict[str, Any]):
        """Cập nhật tổng kết"""
        status = result.get('status', 'error')
        
        if status == 'found':
            self.summary["successful"] += 1
            profiles = result.get('profiles', [])
            self.summary["total_profiles"] += len(profiles)
        elif status == 'not_found':
            self.summary["not_found"] += 1
        elif status == 'error':
            self.summary["errors"] += 1
    
    def print_summary(self):
        """In tổng kết"""
        print("\n" + "=" * 80)
        print("📊 TỔNG KẾT KIỂM TRA VỚI MODULE GỐC")
        print("=" * 80)
        
        print(f"📋 Tổng số CCCD kiểm tra: {self.summary['total_cccds']}")
        print(f"✅ Thành công: {self.summary['successful']}")
        print(f"ℹ️ Không tìm thấy: {self.summary['not_found']}")
        print(f"❌ Lỗi: {self.summary['errors']}")
        print(f"📊 Tổng số profiles tìm thấy: {self.summary['total_profiles']}")
        print(f"⏰ Thời gian xử lý tổng: {self.summary['processing_time']:.2f}s")
        
        # Tính tỷ lệ thành công
        success_rate = (self.summary['successful'] / self.summary['total_cccds']) * 100
        print(f"🎯 Tỷ lệ thành công: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ KẾT QUẢ: Xuất sắc - Module gốc hoạt động tốt")
        elif success_rate >= 60:
            print("⚠️ KẾT QUẢ: Tốt - Module gốc hoạt động ổn định")
        elif success_rate >= 40:
            print("⚠️ KẾT QUẢ: Trung bình - Cần cải thiện")
        else:
            print("❌ KẾT QUẢ: Kém - Cần sửa lỗi")
        
        print("=" * 80)
    
    def save_results(self):
        """Lưu kết quả vào file"""
        try:
            # Lưu kết quả chi tiết
            self.module.save_results(self.results, self.config['output_file'])
            
            # Lưu kết quả JSON
            json_results = {
                "test_info": {
                    "test_date": datetime.now().isoformat(),
                    "total_cccds": len(self.test_cccds),
                    "test_cccds": self.test_cccds,
                    "module_type": "original"
                },
                "summary": self.summary,
                "results": self.results
            }
            
            with open('original_module_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(json_results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Đã lưu kết quả chi tiết vào: {self.config['output_file']}")
            print(f"💾 Đã lưu kết quả JSON vào: original_module_test_results.json")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu kết quả: {str(e)}")


def main():
    """Hàm chính"""
    print("🧪 KIỂM TRA LẠI VỚI MODULE GỐC")
    print("🎯 Sử dụng 5 số CCCD thực tế để test module gốc")
    print("=" * 80)
    
    tester = OriginalModuleTester()
    results = tester.run_original_module_tests()
    
    # Kết luận
    success_rate = (results['summary']['successful'] / results['summary']['total_cccds']) * 100
    
    print(f"\n🎉 KẾT LUẬN:")
    if success_rate >= 80:
        print("✅ Module gốc hoạt động xuất sắc với dữ liệu thực tế!")
        print("✅ Tìm thấy nhiều mã số thuế, module gốc hiệu quả hơn")
    elif success_rate >= 60:
        print("⚠️ Module gốc hoạt động tốt với dữ liệu thực tế")
        print("⚠️ Tìm thấy một số mã số thuế")
    elif success_rate >= 40:
        print("⚠️ Module gốc hoạt động trung bình")
        print("⚠️ Tìm thấy ít mã số thuế")
    else:
        print("❌ Module gốc cũng gặp vấn đề tương tự")
        print("❌ Có thể do anti-bot protection")
    
    print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")
    print(f"📋 Tổng số CCCD kiểm tra: {results['summary']['total_cccds']}")
    print(f"✅ Thành công: {results['summary']['successful']}")
    print(f"📊 Tổng số profiles: {results['summary']['total_profiles']}")


if __name__ == "__main__":
    main()