#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Module 7 với urllib (built-in)
"""

import urllib.request
import urllib.parse
import random
import time
from datetime import datetime

def test_urllib_with_proxy():
    """Test urllib với proxy"""
    print("🧪 TEST MODULE 7 - URLLIB VERSION")
    print("🎯 Test proxy rotation với urllib")
    print("=" * 50)
    
    # Danh sách proxy
    proxies = [
        "http://8.210.83.33:80",
        "http://47.74.152.29:8888",
        "http://103.152.112.145:80",
        "http://185.162.251.76:80",
        "http://103.152.112.162:80"
    ]
    
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
        
        # Chọn proxy ngẫu nhiên
        proxy_url = random.choice(proxies)
        print(f"🔄 Sử dụng proxy: {proxy_url}")
        
        try:
            # Tạo proxy handler
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })
            
            # Tạo opener
            opener = urllib.request.build_opener(proxy_handler)
            
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
            response = opener.open(req, timeout=30)
            
            processing_time = time.time() - start_time
            
            print(f"✅ Status: {response.status}")
            print(f"⏰ Time: {processing_time:.2f}s")
            
            if response.status == 200:
                print("🎉 Thành công!")
                results.append({
                    "cccd": cccd,
                    "status": "success",
                    "status_code": response.status,
                    "proxy": proxy_url,
                    "time": processing_time
                })
            else:
                print(f"⚠️ Status khác: {response.status}")
                results.append({
                    "cccd": cccd,
                    "status": "other",
                    "status_code": response.status,
                    "proxy": proxy_url,
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
                    "proxy": proxy_url,
                    "time": processing_time
                })
            else:
                results.append({
                    "cccd": cccd,
                    "status": "http_error",
                    "status_code": e.code,
                    "proxy": proxy_url,
                    "time": processing_time
                })
                
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            results.append({
                "cccd": cccd,
                "status": "error",
                "error": str(e),
                "proxy": proxy_url
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
    print("🧪 TEST MODULE 7 - URLLIB VERSION")
    print("🎯 Test proxy rotation với urllib")
    print("=" * 50)
    
    results = test_urllib_with_proxy()
    
    print(f"\n🎉 Hoàn thành test với {len(results)} kết quả")

if __name__ == "__main__":
    main()