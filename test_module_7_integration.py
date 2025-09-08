#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Module 7 - Integration với modules hiện có
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Thêm path để import module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.core.module_7_wrapper import Module7Wrapper, check_cccd_with_proxy

class Module7IntegrationTester:
    """Class test Module 7 - Integration"""
    
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
            "not_found": 0,
            "blocked": 0,
            "errors": 0,
            "processing_time": 0.0
        }
    
    async def test_integration_with_existing_modules(self):
        """Test integration với modules hiện có"""
        print("🧪 TEST MODULE 7 - INTEGRATION")
        print("🎯 Test integration với modules hiện có")
        print("=" * 80)
        print(f"📋 Số lượng CCCD test: {len(self.test_cccds)}")
        print(f"📅 Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        start_time = asyncio.get_event_loop().time()
        
        # Test với Module7Wrapper
        config = {
            'timeout': 30,
            'max_retries': 2,
            'proxy_strategy': 'random',
            'enable_dynamic_data': True
        }
        
        async with Module7Wrapper(config) as wrapper:
            
            for i, cccd in enumerate(self.test_cccds, 1):
                print(f"\n📋 [{i}/{len(self.test_cccds)}] Test CCCD: {cccd}")
                print("-" * 60)
                
                try:
                    # Test với wrapper
                    result = await wrapper.check_cccd_with_proxy(cccd)
                    
                    self.results.append({
                        "cccd": cccd,
                        "method": "module_7_wrapper",
                        "result": result
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
                        "method": "module_7_wrapper",
                        "result": {
                            "status": "error",
                            "error": str(e)
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
    
    async def test_standalone_functions(self):
        """Test standalone functions"""
        print("\n🧪 TEST STANDALONE FUNCTIONS")
        print("=" * 80)
        
        config = {
            'timeout': 30,
            'max_retries': 2,
            'proxy_strategy': 'random',
            'enable_dynamic_data': True
        }
        
        standalone_results = []
        
        for i, cccd in enumerate(self.test_cccds[:2], 1):  # Test 2 CCCD đầu tiên
            print(f"\n📋 [{i}/2] Test standalone function: {cccd}")
            print("-" * 40)
            
            try:
                # Test với standalone function
                result = await check_cccd_with_proxy(cccd, config)
                standalone_results.append(result)
                
                # In kết quả
                print(f"🔍 Kết quả standalone #{i}:")
                print(f"   CCCD: {result.get('cccd', 'N/A')}")
                print(f"   Trạng thái: {result.get('status', 'N/A')}")
                print(f"   Thông báo: {result.get('message', 'N/A')}")
                print(f"   Proxy Used: {result.get('proxy_used', 'N/A')}")
                print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
                
                # Delay
                if i < 2:
                    print("⏳ Chờ 2s...")
                    await asyncio.sleep(2.0)
            
            except Exception as e:
                print(f"❌ Lỗi: {str(e)}")
                standalone_results.append({
                    "cccd": cccd,
                    "status": "error",
                    "error": str(e)
                })
        
        return standalone_results
    
    async def test_comparison_with_old_modules(self):
        """Test so sánh với modules cũ"""
        print("\n🧪 TEST COMPARISON WITH OLD MODULES")
        print("=" * 80)
        
        # Test với CCCD đầu tiên
        test_cccd = self.test_cccds[0]
        print(f"📋 Test CCCD: {test_cccd}")
        print("-" * 40)
        
        # Test Module 7 (mới)
        print("🔄 Test Module 7 (mới)...")
        try:
            config = {
                'timeout': 30,
                'max_retries': 2,
                'proxy_strategy': 'random',
                'enable_dynamic_data': True
            }
            
            async with Module7Wrapper(config) as wrapper:
                module7_result = await wrapper.check_cccd_with_proxy(test_cccd)
            
            print(f"✅ Module 7 Result:")
            print(f"   Status: {module7_result.get('status', 'N/A')}")
            print(f"   Message: {module7_result.get('message', 'N/A')}")
            print(f"   Proxy Used: {module7_result.get('proxy_used', 'N/A')}")
            print(f"   Processing Time: {module7_result.get('processing_time', 0):.2f}s")
            
        except Exception as e:
            print(f"❌ Module 7 Error: {str(e)}")
            module7_result = {"status": "error", "error": str(e)}
        
        # Test Module 2 (cũ) - nếu có
        print("\n🔄 Test Module 2 (cũ)...")
        try:
            # Import module cũ nếu có
            from modules.core.module_2_check_cccd_standardized import Module2CheckCCCDStandardized
            
            old_config = {
                'timeout': 30,
                'max_retries': 3,
                'output_file': 'comparison_test_output.txt'
            }
            
            old_module = Module2CheckCCCDStandardized(old_config)
            old_result = old_module.check_cccd(test_cccd)
            
            print(f"✅ Module 2 Result:")
            print(f"   Status: {old_result.status}")
            print(f"   Message: {old_result.message}")
            print(f"   Processing Time: {old_result.processing_time:.2f}s")
            print(f"   Retry Count: {old_result.retry_count}")
            
        except Exception as e:
            print(f"❌ Module 2 Error: {str(e)}")
            old_result = {"status": "error", "error": str(e)}
        
        # So sánh kết quả
        print(f"\n📊 SO SÁNH KẾT QUẢ:")
        print(f"   Module 7 (mới): {module7_result.get('status', 'N/A')}")
        print(f"   Module 2 (cũ): {old_result.status if hasattr(old_result, 'status') else old_result.get('status', 'N/A')}")
        
        if module7_result.get('status') == old_result.status if hasattr(old_result, 'status') else old_result.get('status'):
            print("✅ Kết quả giống nhau")
        else:
            print("⚠️ Kết quả khác nhau")
        
        return {
            "module7_result": module7_result,
            "old_result": old_result
        }
    
    def print_result_details(self, result, index: int):
        """In chi tiết kết quả"""
        print(f"🔍 Kết quả test #{index}:")
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
        
        if result.get('error_details'):
            print(f"   Error Details: {result['error_details']}")
    
    def update_summary(self, result):
        """Cập nhật summary"""
        status = result.get('status', 'error')
        
        if status == 'found':
            self.summary["successful"] += 1
        elif status == 'not_found':
            self.summary["not_found"] += 1
        elif status == 'blocked':
            self.summary["blocked"] += 1
        else:
            self.summary["errors"] += 1
        
        self.summary["total_requests"] += 1
    
    def print_summary(self):
        """In tổng kết"""
        print("\n" + "=" * 80)
        print("📊 TỔNG KẾT TEST MODULE 7 - INTEGRATION")
        print("=" * 80)
        
        print(f"📋 Tổng số requests: {self.summary['total_requests']}")
        print(f"✅ Thành công: {self.summary['successful']}")
        print(f"ℹ️ Không tìm thấy: {self.summary['not_found']}")
        print(f"🚫 Bị chặn: {self.summary['blocked']}")
        print(f"❌ Lỗi: {self.summary['errors']}")
        print(f"⏰ Thời gian xử lý tổng: {self.summary['processing_time']:.2f}s")
        
        # Tính tỷ lệ thành công
        success_rate = (self.summary['successful'] / max(1, self.summary['total_requests'])) * 100
        print(f"🎯 Tỷ lệ thành công: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ KẾT QUẢ: Xuất sắc - Module 7 Integration hoạt động tốt")
        elif success_rate >= 60:
            print("⚠️ KẾT QUẢ: Tốt - Module 7 Integration hoạt động ổn định")
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
                    "module": "module_7_integration",
                    "total_cccds": len(self.test_cccds),
                    "test_cccds": self.test_cccds
                },
                "summary": self.summary,
                "results": self.results
            }
            
            with open('module_7_integration_results.json', 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Đã lưu kết quả vào: module_7_integration_results.json")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu kết quả: {str(e)}")

async def main():
    """Hàm chính"""
    print("🧪 TEST MODULE 7 - INTEGRATION")
    print("🎯 Test integration với modules hiện có")
    print("=" * 80)
    
    tester = Module7IntegrationTester()
    
    # Test 1: Integration với existing modules
    await tester.test_integration_with_existing_modules()
    
    # Test 2: Standalone functions
    await tester.test_standalone_functions()
    
    # Test 3: Comparison với old modules
    await tester.test_comparison_with_old_modules()
    
    # Kết luận
    success_rate = (tester.summary['successful'] / max(1, tester.summary['total_requests'])) * 100
    
    print(f"\n🎉 KẾT LUẬN INTEGRATION:")
    if success_rate >= 80:
        print("✅ Module 7 Integration hoạt động xuất sắc!")
        print("✅ Tích hợp hoàn hảo với modules hiện có")
    elif success_rate >= 60:
        print("⚠️ Module 7 Integration hoạt động tốt")
        print("⚠️ Tích hợp ổn định với modules hiện có")
    elif success_rate >= 40:
        print("⚠️ Module 7 Integration hoạt động trung bình")
        print("⚠️ Cần cải thiện tích hợp")
    else:
        print("❌ Module 7 Integration cần được cải thiện")
    
    print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")
    print(f"📋 Tổng số requests: {tester.summary['total_requests']}")
    print(f"✅ Thành công: {tester.summary['successful']}")
    print(f"ℹ️ Không tìm thấy: {tester.summary['not_found']}")

if __name__ == "__main__":
    asyncio.run(main())