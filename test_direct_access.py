#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test truy cập trực tiếp masothue.com không dùng proxy
"""

import urllib.request
import time
from datetime import datetime

def test_direct_access():
    """Test truy cập trực tiếp"""
    print("🧪 TEST DIRECT ACCESS")
    print("🎯 Test truy cập trực tiếp masothue.com")
    print("=" * 50)
    
    test_cccds = [
        "001087016369",
        "001184032114", 
        "001098021288",
        "001094001628",
        "036092002342"
    ]
    
    results = []
    
    for i, cccd in enumerate(test_cccds, 1):
        print(f"\n📋 [{i}/{len(test_cccds)}] Test CCCD: {cccd}")
        print("-" * 40)
        
        try:
            # Headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Tạo request
            req = urllib.request.Request(
                "https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/",
                headers=headers
            )
            
            start_time = time.time()
            
            # Thực hiện request
            response = urllib.request.urlopen(req, timeout=30)
            
            processing_time = time.time() - start_time
            
            print(f"✅ Status: {response.status}")
            print(f"⏰ Time: {processing_time:.2f}s")
            
            if response.status == 200:
                print("🎉 Thành công!")
                results.append({
                    "cccd": cccd,
                    "status": "success",
                    "status_code": response.status,
                    "time": processing_time
                })
            else:
                print(f"⚠️ Status khác: {response.status}")
                results.append({
                    "cccd": cccd,
                    "status": "other",
                    "status_code": response.status,
                    "time": processing_time
                })
            
        except urllib.error.HTTPError as e:
            processing_time = time.time() - start_time
            print(f"🚫 HTTP Error: {e.code}")
            print(f"⏰ Time: {processing_time:.2f}s")
            
            if e.code == 403:
                print("🚫 Bị chặn (403)")
                results.append({
                    "cccd": cccd,
                    "status": "blocked",
                    "status_code": e.code,
                    "time": processing_time
                })
            else:
                results.append({
                    "cccd": cccd,
                    "status": "http_error",
                    "status_code": e.code,
                    "time": processing_time
                })
                
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            results.append({
                "cccd": cccd,
                "status": "error",
                "error": str(e)
            })
        
        # Delay giữa các request
        if i < len(test_cccds):
            print("⏳ Chờ 3s...")
            time.sleep(3)
    
    # Tổng kết
    print("\n" + "=" * 50)
    print("📊 TỔNG KẾT")
    print("=" * 50)
    
    total = len(results)
    success = len([r for r in results if r["status"] == "success"])
    blocked = len([r for r in results if r["status"] == "blocked"])
    errors = len([r for r in results if r["status"] == "error"])
    
    print(f"📋 Tổng số test: {total}")
    print(f"✅ Thành công: {success}")
    print(f"🚫 Bị chặn: {blocked}")
    print(f"❌ Lỗi: {errors}")
    
    success_rate = (success / total) * 100
    print(f"🎯 Tỷ lệ thành công: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ KẾT QUẢ: Xuất sắc!")
    elif success_rate >= 60:
        print("⚠️ KẾT QUẢ: Tốt")
    elif success_rate >= 40:
        print("⚠️ KẾT QUẢ: Trung bình")
    else:
        print("❌ KẾT QUẢ: Kém")
    
    return results

def main():
    """Main function"""
    print("🧪 TEST DIRECT ACCESS")
    print("🎯 Test truy cập trực tiếp masothue.com")
    print("=" * 50)
    
    results = test_direct_access()
    
    print(f"\n🎉 Hoàn thành test với {len(results)} kết quả")

if __name__ == "__main__":
    main()