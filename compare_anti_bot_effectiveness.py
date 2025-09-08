#!/usr/bin/env python3
"""
Script so sánh hiệu quả anti-bot trước và sau khi áp dụng Module 2 Enhanced V3
"""

import json
import os
from pathlib import Path

def analyze_lookup_results():
    """Phân tích kết quả lookup từ các file JSON"""
    
    print("📊 PHÂN TÍCH HIỆU QUẢ ANTI-BOT PROTECTION")
    print("=" * 60)
    
    # File paths
    files_to_analyze = [
        ("output/cccd_lookup_results.json", "Module 2 Enhanced V1 (Production)"),
        ("output/test_smart_anti_bot_results.json", "Module 2 Enhanced V3 (Test)")
    ]
    
    results = {}
    
    for file_path, description in files_to_analyze:
        if os.path.exists(file_path):
            print(f"\n📁 Analyzing: {description}")
            print("-" * 50)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total = len(data)
            found = sum(1 for item in data if item.get('status') == 'found')
            not_found = sum(1 for item in data if item.get('status') == 'not_found')
            error = sum(1 for item in data if item.get('status') == 'error')
            error_403 = sum(1 for item in data if '403' in str(item.get('error', '')))
            
            # Calculate response times
            response_times = [item.get('response_time') for item in data if item.get('response_time')]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            results[description] = {
                'total': total,
                'found': found,
                'not_found': not_found,
                'error': error,
                'error_403': error_403,
                'avg_response_time': avg_response_time,
                'success_rate': (found / total * 100) if total > 0 else 0,
                'error_rate': (error / total * 100) if total > 0 else 0,
                'error_403_rate': (error_403 / total * 100) if total > 0 else 0
            }
            
            print(f"  Total records: {total}")
            print(f"  ✅ Found: {found} ({found/total*100:.1f}%)")
            print(f"  ❌ Not found: {not_found} ({not_found/total*100:.1f}%)")
            print(f"  🚫 Errors: {error} ({error/total*100:.1f}%)")
            print(f"  🔒 403 Forbidden: {error_403} ({error_403/total*100:.1f}%)")
            print(f"  ⏱️ Avg response time: {avg_response_time:.2f}s")
        else:
            print(f"\n❌ File not found: {file_path}")
    
    # So sánh kết quả
    if len(results) >= 2:
        print(f"\n🔄 SO SÁNH HIỆU QUẢ:")
        print("=" * 60)
        
        v1_key = "Module 2 Enhanced V1 (Production)"
        v3_key = "Module 2 Enhanced V3 (Test)"
        
        if v1_key in results and v3_key in results:
            v1 = results[v1_key]
            v3 = results[v3_key]
            
            print(f"📈 Cải thiện 403 Error Rate:")
            print(f"  V1: {v1['error_403_rate']:.1f}%")
            print(f"  V3: {v3['error_403_rate']:.1f}%")
            improvement = v1['error_403_rate'] - v3['error_403_rate']
            if improvement > 0:
                print(f"  ✅ Cải thiện: -{improvement:.1f}%")
            else:
                print(f"  ⚠️ Không cải thiện: {improvement:.1f}%")
            
            print(f"\n📈 Cải thiện Response Time:")
            print(f"  V1: {v1['avg_response_time']:.2f}s")
            print(f"  V3: {v3['avg_response_time']:.2f}s")
            time_improvement = v1['avg_response_time'] - v3['avg_response_time']
            if time_improvement > 0:
                print(f"  ✅ Cải thiện: -{time_improvement:.2f}s")
            else:
                print(f"  ⚠️ Chậm hơn: +{abs(time_improvement):.2f}s")
            
            print(f"\n📈 Success Rate:")
            print(f"  V1: {v1['success_rate']:.1f}%")
            print(f"  V3: {v3['success_rate']:.1f}%")
            success_improvement = v3['success_rate'] - v1['success_rate']
            if success_improvement > 0:
                print(f"  ✅ Cải thiện: +{success_improvement:.1f}%")
            else:
                print(f"  ⚠️ Giảm: {success_improvement:.1f}%")
    
    # Đánh giá tổng thể
    print(f"\n🏆 ĐÁNH GIÁ TỔNG THỂ:")
    print("-" * 40)
    
    if v3_key in results:
        v3 = results[v3_key]
        
        if v3['error_403_rate'] == 0:
            print("✅ Hoàn hảo! Module 2 Enhanced V3 loại bỏ hoàn toàn 403 errors")
        elif v3['error_403_rate'] < 5:
            print("✅ Tốt! Module 2 Enhanced V3 giảm đáng kể 403 errors")
        elif v3['error_403_rate'] < 10:
            print("⚠️ Trung bình! Module 2 Enhanced V3 cải thiện một phần")
        else:
            print("❌ Cần cải thiện! Module 2 Enhanced V3 chưa hiệu quả")
        
        if v3['avg_response_time'] < 1:
            print("⚡ Tốc độ phản hồi nhanh")
        elif v3['avg_response_time'] < 2:
            print("⏱️ Tốc độ phản hồi trung bình")
        else:
            print("🐌 Tốc độ phản hồi chậm")
        
        if v3['success_rate'] > 80:
            print("🎯 Tỷ lệ thành công cao")
        elif v3['success_rate'] > 60:
            print("📊 Tỷ lệ thành công trung bình")
        else:
            print("📉 Tỷ lệ thành công thấp")
    
    # Khuyến nghị
    print(f"\n💡 KHUYẾN NGHỊ:")
    print("-" * 20)
    
    if v3_key in results and results[v3_key]['error_403_rate'] == 0:
        print("✅ Triển khai ngay Module 2 Enhanced V3 vào production")
        print("✅ Cập nhật main.py để sử dụng Module2CheckCCCDEnhancedV3")
        print("✅ Monitor hiệu suất trong production environment")
    else:
        print("⚠️ Cần test thêm Module 2 Enhanced V3 với dataset lớn hơn")
        print("⚠️ Cân nhắc điều chỉnh delay parameters")
        print("⚠️ Kiểm tra proxy configuration")

if __name__ == "__main__":
    analyze_lookup_results()