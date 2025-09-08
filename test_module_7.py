#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test Module 7 - Advanced API Client
Test proxy rotation và dynamic payload với dữ liệu thực tế
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

class Module7Tester:
    """Class test Module 7"""
    
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
    
    async def test_advanced_api_client(self) -> Dict[str, Any]:
        """Test Advanced API Client"""
        print("🧪 TEST MODULE 7 - ADVANCED API CLIENT")
        print("=" * 80)
        print(f"📋 Số lượng CCCD test: {len(self.test_cccds)}")
        print(f"📅 Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        start_time = asyncio.get_event_loop().time()
        
        # Test với Advanced API Client
        async with AdvancedAPIClient(
            timeout=30,
            max_retries=3,
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
                        "method": "advanced_api_client",
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
                        print("⏳ Chờ 3s trước khi test CCCD tiếp theo...")
                        await asyncio.sleep(3.0)
                
                except Exception as e:
                    print(f"❌ Lỗi khi test CCCD {cccd}: {str(e)}")
                    self.results.append({
                        "cccd": cccd,
                        "method": "advanced_api_client",
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
    
    async def test_module_7_wrapper(self) -> Dict[str, Any]:
        """Test Module 7 Wrapper"""
        print("\n🧪 TEST MODULE 7 WRAPPER")
        print("=" * 80)
        
        config = {
            'timeout': 30,
            'max_retries': 3,
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
                        print("⏳ Chờ 3s trước khi test CCCD tiếp theo...")
                        await asyncio.sleep(3.0)
                
                except Exception as e:
                    print(f"❌ Lỗi khi test CCCD {cccd}: {str(e)}")
                    wrapper_results.append({
                        "cccd": cccd,
                        "status": "error",
                        "message": str(e)
                    })
        
        return wrapper_results
    
    async def test_proxy_management(self):
        """Test proxy management"""
        print("\n🧪 TEST PROXY MANAGEMENT")
        print("=" * 80)
        
        # Test ProxyManager
        proxy_manager = ProxyManager("config/proxies.txt")
        
        print("🔄 Test fetch free proxies...")
        try:
            proxies = await proxy_manager.fetch_free_proxies(limit=10)
            print(f"✅ Tìm thấy {len(proxies)} proxy miễn phí")
            
            # Lưu proxies
            await proxy_manager.save_proxies(proxies)
            print("✅ Đã lưu proxies vào file")
            
        except Exception as e:
            print(f"❌ Lỗi khi fetch proxies: {str(e)}")
    
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
        print("📊 TỔNG KẾT TEST MODULE 7")
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
            print("✅ KẾT QUẢ: Xuất sắc - Module 7 hoạt động tốt")
        elif success_rate >= 60:
            print("⚠️ KẾT QUẢ: Tốt - Module 7 hoạt động ổn định")
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
                    "module": "module_7_advanced_api_client",
                    "total_cccds": len(self.test_cccds),
                    "test_cccds": self.test_cccds
                },
                "summary": self.summary,
                "results": self.results
            }
            
            with open('module_7_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Đã lưu kết quả vào: module_7_test_results.json")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu kết quả: {str(e)}")

async def main():
    """Hàm chính"""
    print("🧪 TEST MODULE 7 - ADVANCED API CLIENT")
    print("🎯 Test proxy rotation và dynamic payload")
    print("=" * 80)
    
    tester = Module7Tester()
    
    # Test 1: Advanced API Client
    await tester.test_advanced_api_client()
    
    # Test 2: Module 7 Wrapper
    await tester.test_module_7_wrapper()
    
    # Test 3: Proxy Management
    await tester.test_proxy_management()
    
    # Kết luận
    success_rate = (tester.summary['successful'] / max(1, tester.summary['total_requests'])) * 100
    
    print(f"\n🎉 KẾT LUẬN:")
    if success_rate >= 80:
        print("✅ Module 7 hoạt động xuất sắc!")
        print("✅ Proxy rotation và dynamic payload hiệu quả")
    elif success_rate >= 60:
        print("⚠️ Module 7 hoạt động tốt")
        print("⚠️ Có thể cần cải thiện proxy pool")
    elif success_rate >= 40:
        print("⚠️ Module 7 hoạt động trung bình")
        print("⚠️ Cần cải thiện proxy quality")
    else:
        print("❌ Module 7 cần được cải thiện")
        print("❌ Có thể do proxy pool chất lượng thấp")
    
    print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")
    print(f"📋 Tổng số requests: {tester.summary['total_requests']}")
    print(f"🔄 Proxy rotations: {tester.summary['proxy_rotations']}")

if __name__ == "__main__":
    asyncio.run(main())