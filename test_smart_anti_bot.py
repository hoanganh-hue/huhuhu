#!/usr/bin/env python3
"""
Script test Module 2 Enhanced V3 với smart anti-bot protection
"""

import time
import logging
from src.modules.core.module_2_check_cccd_enhanced_v3 import Module2CheckCCCDEnhancedV3

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_smart_anti_bot():
    """Test smart anti-bot protection của Module 2 Enhanced V3"""
    
    # Test configuration
    config = {
        'max_retries': 2,
        'proxy_enabled': True,  # Enable proxy
        'proxy_type': 'socks5',
        'proxy_socks5_host': 'ip.mproxy.vn',
        'proxy_socks5_port': '12301',
        'proxy_socks5_username': 'beba111',
        'proxy_socks5_password': 'tDV5tkMchYUBMD'
    }
    
    # Test CCCDs (mix of real and generated)
    test_cccds = [
        "031089011929",  # Real CCCD
        "037178000015",  # Real CCCD
        "001087016369",  # Real CCCD
        "001184032114",  # Real CCCD
        "001098021288",  # Real CCCD
        "001234567890",  # Generated CCCD (should be not_found)
        "001234567891",  # Generated CCCD (should be not_found)
        "001234567892",  # Generated CCCD (should be not_found)
    ]
    
    print("🧠 Testing Module 2 Enhanced V3 - Smart Anti-bot Protection")
    print("=" * 70)
    
    # Initialize module
    module = Module2CheckCCCDEnhancedV3(config)
    
    results = []
    start_time = time.time()
    
    for i, cccd in enumerate(test_cccds, 1):
        print(f"\n🔍 Testing {i}/{len(test_cccds)}: {cccd}")
        print("-" * 50)
        
        result = module.check_cccd(cccd)
        results.append(result)
        
        print(f"  Status: {result.status}")
        print(f"  Tax Code: {result.tax_code}")
        print(f"  Name: {result.name}")
        print(f"  Response Time: {result.response_time:.2f}s" if result.response_time else "  Response Time: N/A")
        print(f"  Error: {result.error}")
        
        # Show consecutive 403 count
        print(f"  Consecutive 403 Count: {module.consecutive_403_count}")
        print(f"  Total Requests: {module.request_count}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Analyze results
    print(f"\n📊 KẾT QUẢ PHÂN TÍCH:")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r.status == "found")
    not_found_count = sum(1 for r in results if r.status == "not_found")
    error_count = sum(1 for r in results if r.status == "error")
    error_403_count = sum(1 for r in results if "403" in str(r.error))
    
    avg_response_time = sum(r.response_time for r in results if r.response_time) / len([r for r in results if r.response_time])
    
    print(f"✅ Thành công: {success_count}/{len(test_cccds)} ({success_count/len(test_cccds)*100:.1f}%)")
    print(f"❌ Không tìm thấy: {not_found_count}/{len(test_cccds)} ({not_found_count/len(test_cccds)*100:.1f}%)")
    print(f"🚫 Lỗi: {error_count}/{len(test_cccds)} ({error_count/len(test_cccds)*100:.1f}%)")
    print(f"🔒 403 Forbidden: {error_403_count}/{len(test_cccds)} ({error_403_count/len(test_cccds)*100:.1f}%)")
    print(f"⏱️ Thời gian trung bình: {avg_response_time:.2f}s")
    print(f"🕐 Tổng thời gian: {total_time:.2f}s")
    print(f"🔄 Tổng requests: {module.request_count}")
    print(f"🔒 Consecutive 403: {module.consecutive_403_count}")
    
    # Performance analysis
    print(f"\n🎯 ĐÁNH GIÁ HIỆU SUẤT:")
    print("-" * 40)
    
    if error_403_count == 0:
        print("✅ Hoàn hảo! Không có lỗi 403 Forbidden")
    elif error_403_count <= 1:
        print("✅ Tốt! Rất ít lỗi 403 Forbidden")
    elif error_403_count <= 2:
        print("⚠️ Trung bình! Có một số lỗi 403 Forbidden")
    else:
        print("❌ Cần cải thiện! Quá nhiều lỗi 403 Forbidden")
    
    if avg_response_time < 2:
        print("⚡ Tốc độ phản hồi nhanh")
    elif avg_response_time < 5:
        print("⏱️ Tốc độ phản hồi trung bình")
    else:
        print("🐌 Tốc độ phản hồi chậm")
    
    if module.consecutive_403_count == 0:
        print("🛡️ Smart delay hoạt động tốt - không có consecutive 403")
    else:
        print(f"⚠️ Có {module.consecutive_403_count} consecutive 403 - cần tăng delay")
    
    # Save results
    module.save_results(results, 'test_smart_anti_bot_results.json')
    print(f"\n💾 Kết quả đã được lưu vào: output/test_smart_anti_bot_results.json")
    
    return results

if __name__ == "__main__":
    test_smart_anti_bot()