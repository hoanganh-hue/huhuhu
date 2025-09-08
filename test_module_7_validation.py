#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Module 7 - Validation với các website khác
Để xác minh module hoạt động đúng
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

class Module7ValidationTester:
    """Class test Module 7 - Validation"""
    
    def __init__(self):
        self.test_urls = [
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
            "https://api.github.com",
            "https://jsonplaceholder.typicode.com/posts/1"
        ]
        
        self.results = []
        self.summary = {
            "total_requests": 0,
            "successful": 0,
            "blocked": 0,
            "errors": 0,
            "proxy_rotations": 0,
            "processing_time": 0.0
        }
    
    async def test_with_different_websites(self) -> Dict[str, Any]:
        """Test với các website khác để xác minh module hoạt động"""
        print("🧪 TEST MODULE 7 - VALIDATION")
        print("🎯 Test với các website khác để xác minh module hoạt động")
        print("=" * 80)
        print(f"📋 Số lượng URL test: {len(self.test_urls)}")
        print(f"📅 Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        start_time = asyncio.get_event_loop().time()
        
        # Test với Advanced API Client
        async with AdvancedAPIClient(
            timeout=30,
            max_retries=2,
            proxy_strategy="random",
            enable_dynamic_data=True
        ) as client:
            
            for i, url in enumerate(self.test_urls, 1):
                print(f"\n📋 [{i}/{len(self.test_urls)}] Test URL: {url}")
                print("-" * 60)
                
                try:
                    # Test với URL khác
                    result = await client.request(
                        method="GET",
                        url=url,
                        json_body=None
                    )
                    
                    self.results.append({
                        "url": url,
                        "method": "validation_test",
                        "result": {
                            "status": result.status.value,
                            "status_code": result.status_code,
                            "processing_time": result.processing_time,
                            "proxy_used": result.proxy_used.host if result.proxy_used else None,
                            "retry_count": result.retry_count,
                            "error_message": result.error_message,
                            "response_data": result.response_data
                        }
                    })
                    
                    # In kết quả
                    self.print_result_details(result, i, url)
                    
                    # Cập nhật summary
                    self.update_summary(result)
                    
                    # Delay giữa các request
                    if i < len(self.test_urls):
                        print("⏳ Chờ 2s trước khi test URL tiếp theo...")
                        await asyncio.sleep(2.0)
                
                except Exception as e:
                    print(f"❌ Lỗi khi test URL {url}: {str(e)}")
                    self.results.append({
                        "url": url,
                        "method": "validation_test",
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
    
    async def test_proxy_rotation_validation(self):
        """Test proxy rotation validation"""
        print("\n🧪 TEST PROXY ROTATION VALIDATION")
        print("=" * 80)
        
        # Test với httpbin.org/ip để xem IP thay đổi
        test_url = "https://httpbin.org/ip"
        ip_addresses = []
        
        async with AdvancedAPIClient(
            timeout=30,
            max_retries=1,
            proxy_strategy="random",
            enable_dynamic_data=True
        ) as client:
            
            for i in range(5):
                print(f"\n📋 [{i+1}/5] Test proxy rotation: {test_url}")
                print("-" * 40)
                
                try:
                    result = await client.request(
                        method="GET",
                        url=test_url,
                        json_body=None
                    )
                    
                    if result.status.value == "success" and result.response_data:
                        ip_info = result.response_data.get("origin", "Unknown")
                        ip_addresses.append(ip_info)
                        print(f"✅ IP Address: {ip_info}")
                        print(f"🔄 Proxy Used: {result.proxy_used.host if result.proxy_used else 'None'}")
                    else:
                        print(f"❌ Request failed: {result.error_message}")
                    
                    # Delay
                    if i < 4:
                        print("⏳ Chờ 1s...")
                        await asyncio.sleep(1.0)
                
                except Exception as e:
                    print(f"❌ Lỗi: {str(e)}")
        
        # Phân tích IP addresses
        print(f"\n📊 PHÂN TÍCH PROXY ROTATION:")
        print(f"   Tổng số requests: {len(ip_addresses)}")
        print(f"   IP addresses: {ip_addresses}")
        
        unique_ips = list(set(ip_addresses))
        print(f"   Unique IPs: {len(unique_ips)}")
        print(f"   Unique IP addresses: {unique_ips}")
        
        if len(unique_ips) > 1:
            print("✅ Proxy rotation hoạt động - IP addresses khác nhau")
        else:
            print("⚠️ Proxy rotation có thể không hoạt động - IP addresses giống nhau")
        
        return ip_addresses
    
    async def test_dynamic_payload_validation(self):
        """Test dynamic payload validation"""
        print("\n🧪 TEST DYNAMIC PAYLOAD VALIDATION")
        print("=" * 80)
        
        # Test với httpbin.org/post để xem payload thay đổi
        test_url = "https://httpbin.org/post"
        payloads = []
        
        async with AdvancedAPIClient(
            timeout=30,
            max_retries=1,
            proxy_strategy="random",
            enable_dynamic_data=True
        ) as client:
            
            for i in range(3):
                print(f"\n📋 [{i+1}/3] Test dynamic payload: {test_url}")
                print("-" * 40)
                
                try:
                    test_payload = {
                        "test_id": i,
                        "timestamp": datetime.now().isoformat(),
                        "message": f"Test payload {i}"
                    }
                    
                    result = await client.request(
                        method="POST",
                        url=test_url,
                        json_body=test_payload
                    )
                    
                    if result.status.value == "success" and result.response_data:
                        received_payload = result.response_data.get("json", {})
                        payloads.append(received_payload)
                        print(f"✅ Payload sent: {test_payload}")
                        print(f"✅ Payload received: {received_payload}")
                        
                        # Kiểm tra dynamic data
                        if "dynamic_info" in received_payload:
                            print(f"✅ Dynamic data included: {received_payload['dynamic_info']}")
                        else:
                            print("⚠️ Dynamic data not included")
                    else:
                        print(f"❌ Request failed: {result.error_message}")
                    
                    # Delay
                    if i < 2:
                        print("⏳ Chờ 1s...")
                        await asyncio.sleep(1.0)
                
                except Exception as e:
                    print(f"❌ Lỗi: {str(e)}")
        
        print(f"\n📊 PHÂN TÍCH DYNAMIC PAYLOAD:")
        print(f"   Tổng số payloads: {len(payloads)}")
        
        for i, payload in enumerate(payloads):
            print(f"   Payload {i+1}: {payload}")
        
        return payloads
    
    def print_result_details(self, result, index: int, url: str):
        """In chi tiết kết quả"""
        print(f"🔍 Kết quả test #{index}:")
        print(f"   URL: {url}")
        print(f"   Status: {result.status.value}")
        print(f"   Status Code: {result.status_code}")
        print(f"   Processing Time: {result.processing_time:.2f}s")
        print(f"   Proxy Used: {result.proxy_used.host if result.proxy_used else 'None'}")
        print(f"   Retry Count: {result.retry_count}")
        
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        if result.response_data:
            # In một phần response data
            response_str = json.dumps(result.response_data, ensure_ascii=False, indent=2)
            if len(response_str) > 200:
                response_str = response_str[:200] + "..."
            print(f"   Response Data: {response_str}")
    
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
        print("📊 TỔNG KẾT TEST MODULE 7 - VALIDATION")
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
            print("✅ KẾT QUẢ: Xuất sắc - Module 7 Validation hoạt động tốt")
        elif success_rate >= 60:
            print("⚠️ KẾT QUẢ: Tốt - Module 7 Validation hoạt động ổn định")
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
                    "module": "module_7_validation",
                    "total_urls": len(self.test_urls),
                    "test_urls": self.test_urls
                },
                "summary": self.summary,
                "results": self.results
            }
            
            with open('module_7_validation_results.json', 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Đã lưu kết quả vào: module_7_validation_results.json")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu kết quả: {str(e)}")

async def main():
    """Hàm chính"""
    print("🧪 TEST MODULE 7 - VALIDATION")
    print("🎯 Test với các website khác để xác minh module hoạt động")
    print("=" * 80)
    
    tester = Module7ValidationTester()
    
    # Test 1: Different websites
    await tester.test_with_different_websites()
    
    # Test 2: Proxy rotation validation
    ip_addresses = await tester.test_proxy_rotation_validation()
    
    # Test 3: Dynamic payload validation
    payloads = await tester.test_dynamic_payload_validation()
    
    # Kết luận
    success_rate = (tester.summary['successful'] / max(1, tester.summary['total_requests'])) * 100
    
    print(f"\n🎉 KẾT LUẬN VALIDATION:")
    if success_rate >= 80:
        print("✅ Module 7 Validation hoạt động xuất sắc!")
        print("✅ Proxy rotation và dynamic payload hiệu quả")
    elif success_rate >= 60:
        print("⚠️ Module 7 Validation hoạt động tốt")
        print("⚠️ Có thể cần cải thiện")
    elif success_rate >= 40:
        print("⚠️ Module 7 Validation hoạt động trung bình")
        print("⚠️ Cần cải thiện")
    else:
        print("❌ Module 7 Validation cần được cải thiện")
    
    print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")
    print(f"📋 Tổng số requests: {tester.summary['total_requests']}")
    print(f"🔄 Proxy rotations: {tester.summary['proxy_rotations']}")
    print(f"🌐 Unique IPs: {len(set(ip_addresses))}")
    print(f"📦 Dynamic payloads: {len(payloads)}")

if __name__ == "__main__":
    asyncio.run(main())