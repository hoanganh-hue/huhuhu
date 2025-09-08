#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Module 7 - Fixed Version
Test với httpx proxy support đã sửa
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Thêm path để import module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.core.module_7_advanced_api_client import AdvancedAPIClient, ProxyManager
from modules.core.module_7_wrapper import Module7Wrapper

class Module7FixedTester:
    """Class test Module 7 - Fixed Version"""
    
    def __init__(self):
        self.test_cccds = [
            "001087016369",
            "001184032114", 
            "001098021288",
            "001094001628",
            "036092002342"
        ]
        
        self.results = []
        self.summary = {
            "total_requests": 0,
            "successful": 0,
            "blocked": 0,
            "errors": 0,
            "proxy_rotations": 0,
            "total_profiles": 0,
            "processing_time": 0.0
        }
    
    async def test_fixed_advanced_api_client(self) -> Dict[str, Any]:
        """Test Advanced API Client - Fixed Version"""
        print("🧪 TEST MODULE 7 - FIXED VERSION")
        print("=" * 80)
        print(f"📋 Số lượng CCCD test: {len(self.test_cccds)}")
        print(f"📅 Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        start_time = asyncio.get_event_loop().time()
        
        # Test với Advanced API Client - Fixed
        async with AdvancedAPIClient(
            timeout=30,
            max_retries=2,  # Giảm retry để test nhanh hơn
            proxy_strategy="random",
            enable_dynamic_data=True
        ) as client:
            
            for i, cccd in enumerate(self.test_cccds, 1):
                print(f"\n📋 [{i}/{len(self.test_cccds)}] Test CCCD: {cccd}")
                print("-" * 60)
                
                try:
                    # Test với masothue.com
                    result = await client.request(
                        method="GET",
                        url="https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/",
                        json_body={"cccd": cccd, "type": "personal"}
                    )
                    
                    self.results.append({
                        "cccd": cccd,
                        "method": "fixed_advanced_api_client",
                        "result": {
                            "status": result.status.value,
                            "status_code": result.status_code,
                            "processing_time": result.processing_time,
                            "proxy_used": result.proxy_used.host if result.proxy_used else None,
                            "retry_count": result.retry_count,
                            "error_message": result.error_message
                        }
                    })
                    
                    # In kết quả
                    self.print_result_details(result, i)
                    
                    # Cập nhật summary
                    self.update_summary(result)
                    
                    # Delay giữa các request
                    if i < len(self.test_cccds):
                        print("⏳ Chờ 2s trước khi test CCCD tiếp theo...")
                        await asyncio.sleep(2.0)
                
                except Exception as e:
                    print(f"❌ Lỗi khi test CCCD {cccd}: {str(e)}")
                    self.results.append({
                        "cccd": cccd,
                        "method": "fixed_advanced_api_client",
                        "result": {
                            "status": "error",
                            "error_message": str(e)
                        }
                    })
                    self.summary["errors"] += 1
        
        # Tính thời gian xử lý tổng
        self.summary["processing_time"] = asyncio.get_event_loop().time() - start_time
        
        # In tổng kết
        self.print_summary()
        
        # Lưu kết quả
        self.save_results()
        
        return {
            "results": self.results,
            "summary": self.summary
        }
    
    async def test_fixed_wrapper(self) -> Dict[str, Any]:
        """Test Module 7 Wrapper - Fixed Version"""
        print("\n🧪 TEST MODULE 7 WRAPPER - FIXED VERSION")
        print("=" * 80)
        
        config = {
            'timeout': 30,
            'max_retries': 2,
            'proxy_strategy': 'random',
            'enable_dynamic_data': True
        }
        
        wrapper_results = []
        
        async with Module7Wrapper(config) as wrapper:
            
            for i, cccd in enumerate(self.test_cccds, 1):
                print(f"\n📋 [{i}/{len(self.test_cccds)}] Test CCCD với Wrapper: {cccd}")
                print("-" * 60)
                
                try:
                    result = await wrapper.check_cccd_with_proxy(cccd)
                    wrapper_results.append(result)
                    
                    # In kết quả
                    print(f"🔍 Kết quả CCCD #{i}:")
                    print(f"   CCCD: {result.get('cccd', 'N/A')}")
                    print(f"   Trạng thái: {result.get('status', 'N/A')}")
                    print(f"   Thông báo: {result.get('message', 'N/A')}")
                    print(f"   Proxy Used: {result.get('proxy_used', 'N/A')}")
                    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
                    print(f"   Retry Count: {result.get('retry_count', 0)}")
                    
                    if result.get('profiles'):
                        print(f"   📊 Số profiles: {len(result['profiles'])}")
                        for j, profile in enumerate(result['profiles'], 1):
                            print(f"   └─ Profile {j}: {profile.get('name', 'N/A')}")
                    
                    # Delay giữa các request
                    if i < len(self.test_cccds):
                        print("⏳ Chờ 2s trước khi test CCCD tiếp theo...")
                        await asyncio.sleep(2.0)
                
                except Exception as e:
                    print(f"❌ Lỗi khi test CCCD {cccd}: {str(e)}")
                    wrapper_results.append({
                        "cccd": cccd,
                        "status": "error",
                        "message": str(e)
                    })
        
        return wrapper_results
    
    async def test_proxy_quality(self):
        """Test chất lượng proxy"""
        print("\n🧪 TEST PROXY QUALITY")
        print("=" * 80)
        
        # Test với một số proxy khác
        test_proxies = [
            "http://8.210.83.33:80",
            "http://47.74.152.29:8888",
            "http://103.152.112.145:80",
            "http://185.162.251.76:80",
            "http://103.152.112.162:80"
        ]
        
        working_proxies = []
        
        for proxy_url in test_proxies:
            print(f"🔄 Test proxy: {proxy_url}")
            
            try:
                import os
                original_http_proxy = os.environ.get('HTTP_PROXY')
                original_https_proxy = os.environ.get('HTTPS_PROXY')
                
                try:
                    # Set proxy
                    os.environ['HTTP_PROXY'] = proxy_url
                    os.environ['HTTPS_PROXY'] = proxy_url
                    
                    # Test với httpbin.org
                    async with AdvancedAPIClient(timeout=10) as client:
                        result = await client.request(
                            method="GET",
                            url="https://httpbin.org/ip"
                        )
                        
                        if result.status.value == "success":
                            print(f"✅ Proxy hoạt động: {proxy_url}")
                            working_proxies.append(proxy_url)
                        else:
                            print(f"❌ Proxy không hoạt động: {proxy_url}")
                
                finally:
                    # Restore proxy settings
                    if original_http_proxy:
                        os.environ['HTTP_PROXY'] = original_http_proxy
                    elif 'HTTP_PROXY' in os.environ:
                        del os.environ['HTTP_PROXY']
                    
                    if original_https_proxy:
                        os.environ['HTTPS_PROXY'] = original_https_proxy
                    elif 'HTTPS_PROXY' in os.environ:
                        del os.environ['HTTPS_PROXY']
                
            except Exception as e:
                print(f"❌ Lỗi test proxy {proxy_url}: {str(e)}")
        
        print(f"\n📊 Kết quả test proxy:")
        print(f"   Tổng số proxy: {len(test_proxies)}")
        print(f"   Proxy hoạt động: {len(working_proxies)}")
        print(f"   Proxy không hoạt động: {len(test_proxies) - len(working_proxies)}")
        
        if working_proxies:
            print(f"   ✅ Proxy hoạt động: {working_proxies}")
        else:
            print(f"   ❌ Không có proxy nào hoạt động")
        
        return working_proxies
    
    def print_result_details(self, result, index: int):
        """In chi tiết kết quả"""
        print(f"🔍 Kết quả test #{index}:")
        print(f"   Status: {result.status.value}")
        print(f"   Status Code: {result.status_code}")
        print(f"   Processing Time: {result.processing_time:.2f}s")
        print(f"   Proxy Used: {result.proxy_used.host if result.proxy_used else 'None'}")
        print(f"   Retry Count: {result.retry_count}")
        
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        if result.response_data:
            print(f"   Response Data: {json.dumps(result.response_data, ensure_ascii=False, indent=6)[:200]}...")
    
    def update_summary(self, result):
        """Cập nhật summary"""
        if result.status.value == "success":
            self.summary["successful"] += 1
        elif result.status.value == "blocked":
            self.summary["blocked"] += 1
        else:
            self.summary["errors"] += 1
        
        self.summary["total_requests"] += 1
        self.summary["proxy_rotations"] += 1
    
    def print_summary(self):
        """In tổng kết"""
        print("\n" + "=" * 80)
        print("📊 TỔNG KẾT TEST MODULE 7 - FIXED VERSION")
        print("=" * 80)
        
        print(f"📋 Tổng số requests: {self.summary['total_requests']}")
        print(f"✅ Thành công: {self.summary['successful']}")
        print(f"🚫 Bị chặn: {self.summary['blocked']}")
        print(f"❌ Lỗi: {self.summary['errors']}")
        print(f"🔄 Proxy rotations: {self.summary['proxy_rotations']}")
        print(f"⏰ Thời gian xử lý tổng: {self.summary['processing_time']:.2f}s")
        
        # Tính tỷ lệ thành công
        success_rate = (self.summary['successful'] / max(1, self.summary['total_requests'])) * 100
        print(f"🎯 Tỷ lệ thành công: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ KẾT QUẢ: Xuất sắc - Module 7 Fixed hoạt động tốt")
        elif success_rate >= 60:
            print("⚠️ KẾT QUẢ: Tốt - Module 7 Fixed hoạt động ổn định")
        elif success_rate >= 40:
            print("⚠️ KẾT QUẢ: Trung bình - Cần cải thiện")
        else:
            print("❌ KẾT QUẢ: Kém - Cần sửa lỗi")
        
        print("=" * 80)
    
    def save_results(self):
        """Lưu kết quả"""
        try:
            results_data = {
                "test_info": {
                    "test_date": datetime.now().isoformat(),
                    "module": "module_7_advanced_api_client_fixed",
                    "total_cccds": len(self.test_cccds),
                    "test_cccds": self.test_cccds
                },
                "summary": self.summary,
                "results": self.results
            }
            
            with open('module_7_fixed_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Đã lưu kết quả vào: module_7_fixed_test_results.json")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu kết quả: {str(e)}")

async def main():
    """Hàm chính"""
    print("🧪 TEST MODULE 7 - FIXED VERSION")
    print("🎯 Test proxy rotation và dynamic payload - Fixed")
    print("=" * 80)
    
    tester = Module7FixedTester()
    
    # Test 1: Proxy Quality
    working_proxies = await tester.test_proxy_quality()
    
    # Test 2: Advanced API Client - Fixed
    await tester.test_fixed_advanced_api_client()
    
    # Test 3: Module 7 Wrapper - Fixed
    await tester.test_fixed_wrapper()
    
    # Kết luận
    success_rate = (tester.summary['successful'] / max(1, tester.summary['total_requests'])) * 100
    
    print(f"\n🎉 KẾT LUẬN:")
    if success_rate >= 80:
        print("✅ Module 7 Fixed hoạt động xuất sắc!")
        print("✅ Proxy rotation và dynamic payload hiệu quả")
    elif success_rate >= 60:
        print("⚠️ Module 7 Fixed hoạt động tốt")
        print("⚠️ Có thể cần cải thiện proxy pool")
    elif success_rate >= 40:
        print("⚠️ Module 7 Fixed hoạt động trung bình")
        print("⚠️ Cần cải thiện proxy quality")
    else:
        print("❌ Module 7 Fixed cần được cải thiện")
        print("❌ Có thể do proxy pool chất lượng thấp")
    
    print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")
    print(f"📋 Tổng số requests: {tester.summary['total_requests']}")
    print(f"🔄 Proxy rotations: {tester.summary['proxy_rotations']}")
    print(f"🔧 Working proxies: {len(working_proxies)}")

if __name__ == "__main__":
    asyncio.run(main())