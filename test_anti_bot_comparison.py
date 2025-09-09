#!/usr/bin/env python3
"""
Script so sánh hiệu quả anti-bot giữa Module 2 Enhanced V1 và V2
"""

import time
import logging
from src.modules.core.module_2_check_cccd_enhanced import Module2CheckCCCDEnhanced
from src.modules.core.module_2_check_cccd_enhanced_v2 import Module2CheckCCCDEnhancedV2

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_anti_bot_effectiveness():
    """Test hiệu quả anti-bot của cả 2 phiên bản"""
    
    # Test configuration
    config = {
        'max_retries': 2,
        'proxy_enabled': False
    }
    
    # Test CCCDs
    test_cccds = [
        "031089011929",  # CCCD thực tế có dữ liệu
        "037178000015",  # CCCD thực tế có dữ liệu
        "001087016369",  # CCCD thực tế có dữ liệu
        "001184032114",  # CCCD thực tế có dữ liệu
        "001098021288"   # CCCD thực tế có dữ liệu
    ]
    
    print("🔬 Bắt đầu test so sánh anti-bot effectiveness...")
    print("=" * 60)
    
    # Test Module 2 Enhanced V1
    print("\n📊 Testing Module 2 Enhanced V1:")
    print("-" * 40)
    
    v1_module = Module2CheckCCCDEnhanced(config)
    v1_results = []
    v1_start_time = time.time()
    
    for i, cccd in enumerate(test_cccds, 1):
        print(f"  🔍 Testing {i}/{len(test_cccds)}: {cccd}")
        result = v1_module.check_cccd(cccd)
        v1_results.append(result)
        
        print(f"    Status: {result.status}")
        print(f"    Tax Code: {result.tax_code}")
        print(f"    Response Time: {result.response_time:.2f}s" if result.response_time else "    Response Time: N/A")
        print(f"    Error: {result.error}")
        print()
    
    v1_end_time = time.time()
    v1_total_time = v1_end_time - v1_start_time
    
    # Test Module 2 Enhanced V2
    print("\n📊 Testing Module 2 Enhanced V2:")
    print("-" * 40)
    
    v2_module = Module2CheckCCCDEnhancedV2(config)
    v2_results = []
    v2_start_time = time.time()
    
    for i, cccd in enumerate(test_cccds, 1):
        print(f"  🔍 Testing {i}/{len(test_cccds)}: {cccd}")
        result = v2_module.check_cccd(cccd)
        v2_results.append(result)
        
        print(f"    Status: {result.status}")
        print(f"    Tax Code: {result.tax_code}")
        print(f"    Response Time: {result.response_time:.2f}s" if result.response_time else "    Response Time: N/A")
        print(f"    Error: {result.error}")
        print()
    
    v2_end_time = time.time()
    v2_total_time = v2_end_time - v2_start_time
    
    # So sánh kết quả
    print("\n📈 KẾT QUẢ SO SÁNH:")
    print("=" * 60)
    
    # Thống kê V1
    v1_success = sum(1 for r in v1_results if r.status == "found")
    v1_403_errors = sum(1 for r in v1_results if "403" in str(r.error))
    v1_avg_response_time = sum(r.response_time for r in v1_results if r.response_time) / len([r for r in v1_results if r.response_time])
    
    # Thống kê V2
    v2_success = sum(1 for r in v2_results if r.status == "found")
    v2_403_errors = sum(1 for r in v2_results if "403" in str(r.error))
    v2_avg_response_time = sum(r.response_time for r in v2_results if r.response_time) / len([r for r in v2_results if r.response_time])
    
    print(f"Module 2 Enhanced V1:")
    print(f"  ✅ Thành công: {v1_success}/{len(test_cccds)} ({v1_success/len(test_cccds)*100:.1f}%)")
    print(f"  ❌ 403 Errors: {v1_403_errors}/{len(test_cccds)} ({v1_403_errors/len(test_cccds)*100:.1f}%)")
    print(f"  ⏱️ Thời gian trung bình: {v1_avg_response_time:.2f}s")
    print(f"  🕐 Tổng thời gian: {v1_total_time:.2f}s")
    
    print(f"\nModule 2 Enhanced V2:")
    print(f"  ✅ Thành công: {v2_success}/{len(test_cccds)} ({v2_success/len(test_cccds)*100:.1f}%)")
    print(f"  ❌ 403 Errors: {v2_403_errors}/{len(test_cccds)} ({v2_403_errors/len(test_cccds)*100:.1f}%)")
    print(f"  ⏱️ Thời gian trung bình: {v2_avg_response_time:.2f}s")
    print(f"  🕐 Tổng thời gian: {v2_total_time:.2f}s")
    
    # Đánh giá
    print(f"\n🏆 ĐÁNH GIÁ:")
    print("-" * 30)
    
    if v2_403_errors < v1_403_errors:
        print("✅ V2 có ít lỗi 403 hơn V1 - Anti-bot protection tốt hơn")
    elif v2_403_errors > v1_403_errors:
        print("❌ V2 có nhiều lỗi 403 hơn V1 - Cần cải thiện")
    else:
        print("⚖️ V1 và V2 có cùng số lỗi 403")
    
    if v2_success > v1_success:
        print("✅ V2 có tỷ lệ thành công cao hơn V1")
    elif v2_success < v1_success:
        print("❌ V2 có tỷ lệ thành công thấp hơn V1")
    else:
        print("⚖️ V1 và V2 có cùng tỷ lệ thành công")
    
    if v2_total_time > v1_total_time:
        print(f"⏱️ V2 chậm hơn V1 {v2_total_time - v1_total_time:.2f}s (do adaptive delay)")
    else:
        print("⚡ V2 nhanh hơn hoặc bằng V1")
    
    print(f"\n💡 KHUYẾN NGHỊ:")
    if v2_403_errors < v1_403_errors and v2_success >= v1_success:
        print("✅ Sử dụng Module 2 Enhanced V2 cho production")
    else:
        print("⚠️ Cần cải thiện thêm Module 2 Enhanced V2")

if __name__ == "__main__":
    test_anti_bot_effectiveness()