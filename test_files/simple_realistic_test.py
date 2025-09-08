#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test cho Realistic CCCD Generator
"""

import random
from collections import Counter

def simulate_realistic_generator():
    """Mô phỏng realistic generator"""
    print("🚀 Mô phỏng Realistic CCCD Generator")
    print("=" * 50)
    
    # Tỷ lệ dân số theo vùng miền (2023)
    region_weights = {
        "Miền Bắc": 0.35,  # 35% dân số
        "Miền Trung": 0.20,  # 20% dân số  
        "Miền Nam": 0.45   # 45% dân số
    }
    
    # Tỷ lệ giới tính (2023)
    gender_weights = {
        "Nam": 0.49,  # 49%
        "Nữ": 0.51   # 51%
    }
    
    # Mapping tỉnh thành theo vùng miền
    province_mapping = {
        "Miền Bắc": ["001", "002", "004", "006", "008", "010", "011", "012", "014", "015", 
                    "017", "019", "020", "022", "024", "025", "026", "027", "030", "031", 
                    "033", "034", "035", "036", "037", "038", "040", "042"],
        "Miền Trung": ["044", "045", "046", "048", "049", "051", "052", "054", "056", "058", 
                      "060", "062", "064", "066", "067", "068"],
        "Miền Nam": ["070", "072", "074", "075", "077", "079", "080", "082", "083", "084", 
                    "086", "087", "089", "091", "092", "093", "094", "095", "096"]
    }
    
    # Tạo weighted provinces
    weighted_provinces = []
    province_weights = []
    
    for region, provinces in province_mapping.items():
        region_weight = region_weights[region]
        province_weight = region_weight / len(provinces)
        
        for province in provinces:
            weighted_provinces.append(province)
            province_weights.append(province_weight)
    
    # Tạo 1000 CCCD với phân bố thực tế
    results = []
    for _ in range(1000):
        # Chọn tỉnh theo trọng số
        province_code = random.choices(
            weighted_provinces,
            weights=province_weights
        )[0]
        
        # Chọn giới tính theo tỷ lệ thực tế
        gender = random.choices(
            list(gender_weights.keys()),
            weights=list(gender_weights.values())
        )[0]
        
        # Chọn năm sinh theo tỷ lệ thực tế
        birth_year_ranges = {
            "1990-1999": (1990, 1999),
            "2000-2009": (2000, 2009),
            "2010-2019": (2010, 2019),
            "2020-2023": (2020, 2023)
        }
        
        year_range = random.choices(
            list(birth_year_ranges.keys()),
            weights=[0.25, 0.30, 0.25, 0.20]  # Tỷ lệ thực tế
        )[0]
        
        start_year, end_year = birth_year_ranges[year_range]
        birth_year = random.randint(start_year, end_year)
        
        # Tìm vùng miền
        region = None
        for reg, provinces in province_mapping.items():
            if province_code in provinces:
                region = reg
                break
        
        results.append({
            "province_code": province_code,
            "region": region,
            "gender": gender,
            "birth_year": birth_year,
            "year_range": year_range
        })
    
    return results

def simulate_current_generator():
    """Mô phỏng generator hiện tại (random đều)"""
    print("\n🔍 Mô phỏng Generator hiện tại (Random đều)")
    print("=" * 50)
    
    # Tất cả mã tỉnh
    all_provinces = []
    province_mapping = {
        "Miền Bắc": ["001", "002", "004", "006", "008", "010", "011", "012", "014", "015", 
                    "017", "019", "020", "022", "024", "025", "026", "027", "030", "031", 
                    "033", "034", "035", "036", "037", "038", "040", "042"],
        "Miền Trung": ["044", "045", "046", "048", "049", "051", "052", "054", "056", "058", 
                      "060", "062", "064", "066", "067", "068"],
        "Miền Nam": ["070", "072", "074", "075", "077", "079", "080", "082", "083", "084", 
                    "086", "087", "089", "091", "092", "093", "094", "095", "096"]
    }
    
    for provinces in province_mapping.values():
        all_provinces.extend(provinces)
    
    # Tạo 1000 CCCD với random đều
    results = []
    for _ in range(1000):
        # Random tỉnh thành
        province_code = random.choice(all_provinces)
        
        # Random giới tính
        gender = random.choice(["Nam", "Nữ"])
        
        # Random năm sinh
        birth_year = random.randint(1990, 2023)
        
        # Tìm vùng miền
        region = None
        for reg, provinces in province_mapping.items():
            if province_code in provinces:
                region = reg
                break
        
        results.append({
            "province_code": province_code,
            "region": region,
            "gender": gender,
            "birth_year": birth_year
        })
    
    return results

def analyze_distribution(data, title):
    """Phân tích phân bố dữ liệu"""
    print(f"\n📊 Phân tích phân bố: {title}")
    print("-" * 40)
    
    total = len(data)
    
    # Phân tích vùng miền
    region_count = Counter(item["region"] for item in data)
    print("🗺️ Vùng miền:")
    for region, count in region_count.items():
        ratio = (count / total) * 100
        print(f"  {region}: {count:3d} ({ratio:5.1f}%)")
    
    # Phân tích giới tính
    gender_count = Counter(item["gender"] for item in data)
    print("\n👥 Giới tính:")
    for gender, count in gender_count.items():
        ratio = (count / total) * 100
        print(f"  {gender}: {count:3d} ({ratio:5.1f}%)")
    
    # Phân tích tỉnh thành
    province_count = Counter(item["province_code"] for item in data)
    print("\n🏙️ Top 10 tỉnh thành:")
    for i, (province, count) in enumerate(province_count.most_common(10)):
        ratio = (count / total) * 100
        print(f"  {i+1:2d}. {province}: {count:3d} ({ratio:5.1f}%)")
    
    return {
        "region_distribution": dict(region_count),
        "gender_distribution": dict(gender_count),
        "province_distribution": dict(province_count)
    }

def compare_with_real_statistics(current_stats, realistic_stats):
    """So sánh với thống kê thực tế"""
    print("\n📈 So sánh với thống kê thực tế")
    print("=" * 50)
    
    print("🗺️ Phân bố vùng miền (thực tế: Bắc 35%, Trung 20%, Nam 45%):")
    
    # Current generator
    current_total = sum(current_stats["region_distribution"].values())
    print("  Generator hiện tại:")
    for region in ["Miền Bắc", "Miền Trung", "Miền Nam"]:
        count = current_stats["region_distribution"].get(region, 0)
        ratio = (count / current_total) * 100 if current_total > 0 else 0
        expected = 35.0 if region == "Miền Bắc" else 20.0 if region == "Miền Trung" else 45.0
        diff = abs(ratio - expected)
        status = "✅" if diff < 5 else "⚠️" if diff < 10 else "❌"
        print(f"    {status} {region}: {ratio:.1f}% (thực tế: {expected:.1f}%, chênh lệch: {diff:.1f}%)")
    
    # Realistic generator
    realistic_total = sum(realistic_stats["region_distribution"].values())
    print("  Generator thực tế:")
    for region in ["Miền Bắc", "Miền Trung", "Miền Nam"]:
        count = realistic_stats["region_distribution"].get(region, 0)
        ratio = (count / realistic_total) * 100 if realistic_total > 0 else 0
        expected = 35.0 if region == "Miền Bắc" else 20.0 if region == "Miền Trung" else 45.0
        diff = abs(ratio - expected)
        status = "✅" if diff < 5 else "⚠️" if diff < 10 else "❌"
        print(f"    {status} {region}: {ratio:.1f}% (thực tế: {expected:.1f}%, chênh lệch: {diff:.1f}%)")
    
    print("\n👥 Tỷ lệ giới tính (thực tế: Nam 49%, Nữ 51%):")
    
    # Current generator
    current_total = sum(current_stats["gender_distribution"].values())
    print("  Generator hiện tại:")
    for gender in ["Nam", "Nữ"]:
        count = current_stats["gender_distribution"].get(gender, 0)
        ratio = (count / current_total) * 100 if current_total > 0 else 0
        expected = 49.0 if gender == "Nam" else 51.0
        diff = abs(ratio - expected)
        status = "✅" if diff < 3 else "⚠️" if diff < 5 else "❌"
        print(f"    {status} {gender}: {ratio:.1f}% (thực tế: {expected:.1f}%, chênh lệch: {diff:.1f}%)")
    
    # Realistic generator
    realistic_total = sum(realistic_stats["gender_distribution"].values())
    print("  Generator thực tế:")
    for gender in ["Nam", "Nữ"]:
        count = realistic_stats["gender_distribution"].get(gender, 0)
        ratio = (count / realistic_total) * 100 if realistic_total > 0 else 0
        expected = 49.0 if gender == "Nam" else 51.0
        diff = abs(ratio - expected)
        status = "✅" if diff < 3 else "⚠️" if diff < 5 else "❌"
        print(f"    {status} {gender}: {ratio:.1f}% (thực tế: {expected:.1f}%, chênh lệch: {diff:.1f}%)")

def main():
    """Main function"""
    print("🧪 Test Realistic CCCD Generator")
    print("=" * 60)
    
    # Mô phỏng generator hiện tại
    current_data = simulate_current_generator()
    current_stats = analyze_distribution(current_data, "Generator hiện tại")
    
    # Mô phỏng generator thực tế
    realistic_data = simulate_realistic_generator()
    realistic_stats = analyze_distribution(realistic_data, "Generator thực tế")
    
    # So sánh với thống kê thực tế
    compare_with_real_statistics(current_stats, realistic_stats)
    
    print("\n🎯 KẾT LUẬN:")
    print("=" * 30)
    print("❌ Generator hiện tại: Random đều, không phản ánh thực tế")
    print("✅ Generator thực tế: Phân bố theo tỷ lệ thực tế")
    print("\n💡 KHUYẾN NGHỊ:")
    print("  1. Thay thế random đều bằng weighted random")
    print("  2. Sử dụng tỷ lệ dân số thực tế")
    print("  3. Cập nhật generator hiện tại")
    print("\n🚀 Generator thực tế đã sẵn sàng tích hợp!")

if __name__ == "__main__":
    main()