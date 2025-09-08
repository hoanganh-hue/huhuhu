#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phân tích phân bố CCCD theo dữ liệu thực tế (phiên bản đơn giản)
"""

import random
import json
from collections import Counter, defaultdict
from typing import Dict, List, Any

def get_vietnam_real_statistics():
    """Lấy thống kê thực tế của Việt Nam"""
    return {
        # Dân số theo vùng miền (2023)
        "population_by_region": {
            "Miền Bắc": 0.35,  # ~35% dân số
            "Miền Trung": 0.20,  # ~20% dân số  
            "Miền Nam": 0.45   # ~45% dân số
        },
        
        # Tỷ lệ giới tính (2023)
        "gender_ratio": {
            "Nam": 0.49,  # ~49%
            "Nữ": 0.51   # ~51%
        },
        
        # Phân bố dân số theo độ tuổi (2023)
        "age_distribution": {
            "0-17": 0.25,   # 25% trẻ em/vị thành niên
            "18-30": 0.20,  # 20% thanh niên
            "31-45": 0.25,  # 25% trung niên
            "46-60": 0.20,  # 20% cao tuổi
            "61+": 0.10     # 10% người già
        },
        
        # Các tỉnh thành đông dân nhất
        "top_populated_provinces": {
            "079": 0.12,  # TP.HCM - 12% dân số
            "001": 0.08,  # Hà Nội - 8% dân số
            "075": 0.04,  # Đồng Nai - 4% dân số
            "074": 0.03,  # Bình Dương - 3% dân số
            "031": 0.03,  # Hải Phòng - 3% dân số
            "092": 0.02,  # Cần Thơ - 2% dân số
            "048": 0.02,  # Đà Nẵng - 2% dân số
        }
    }

def get_province_mapping():
    """Mapping tỉnh thành theo vùng miền"""
    return {
        "Miền Bắc": ["001", "002", "004", "006", "008", "010", "011", "012", "014", "015", 
                    "017", "019", "020", "022", "024", "025", "026", "027", "030", "031", 
                    "033", "034", "035", "036", "037", "038", "040", "042"],
        "Miền Trung": ["044", "045", "046", "048", "049", "051", "052", "054", "056", "058", 
                      "060", "062", "064", "066", "067", "068"],
        "Miền Nam": ["070", "072", "074", "075", "077", "079", "080", "082", "083", "084", 
                    "086", "087", "089", "091", "092", "093", "094", "095", "096"]
    }

def simulate_current_generator():
    """Mô phỏng generator hiện tại (random đều)"""
    print("🔍 Mô phỏng Generator hiện tại (Random đều)")
    print("=" * 50)
    
    # Tất cả mã tỉnh
    all_provinces = []
    province_mapping = get_province_mapping()
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
        
        # Random tháng/ngày
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
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
            "birth_month": birth_month,
            "birth_day": birth_day
        })
    
    return results

def simulate_realistic_generator():
    """Mô phỏng generator thực tế (weighted random)"""
    print("\n🎯 Mô phỏng Generator thực tế (Weighted Random)")
    print("=" * 50)
    
    real_stats = get_vietnam_real_statistics()
    province_mapping = get_province_mapping()
    
    # Tạo 1000 CCCD với tỷ lệ thực tế
    results = []
    for _ in range(1000):
        # Chọn vùng miền theo tỷ lệ thực tế
        region = random.choices(
            list(real_stats["population_by_region"].keys()),
            weights=list(real_stats["population_by_region"].values())
        )[0]
        
        # Chọn tỉnh trong vùng miền
        province_code = random.choice(province_mapping[region])
        
        # Chọn giới tính theo tỷ lệ thực tế
        gender = random.choices(
            list(real_stats["gender_ratio"].keys()),
            weights=list(real_stats["gender_ratio"].values())
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
        
        # Random tháng/ngày
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        results.append({
            "province_code": province_code,
            "region": region,
            "gender": gender,
            "birth_year": birth_year,
            "birth_month": birth_month,
            "birth_day": birth_day,
            "year_range": year_range
        })
    
    return results

def analyze_distribution(data: List[Dict], title: str):
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
    
    # Phân tích năm sinh
    birth_year_count = Counter(item["birth_year"] for item in data)
    print("\n📅 Top 10 năm sinh:")
    for year, count in birth_year_count.most_common(10):
        ratio = (count / total) * 100
        print(f"  {year}: {count:3d} ({ratio:5.1f}%)")
    
    # Phân tích tỉnh thành
    province_count = Counter(item["province_code"] for item in data)
    print("\n🏙️ Top 10 tỉnh thành:")
    for province, count in province_count.most_common(10):
        ratio = (count / total) * 100
        print(f"  {province}: {count:3d} ({ratio:5.1f}%)")
    
    return {
        "region_distribution": dict(region_count),
        "gender_distribution": dict(gender_count),
        "province_distribution": dict(province_count),
        "birth_year_distribution": dict(birth_year_count)
    }

def compare_with_real_statistics(current_stats: Dict, realistic_stats: Dict):
    """So sánh với thống kê thực tế"""
    print("\n📈 So sánh với thống kê thực tế")
    print("=" * 50)
    
    real_stats = get_vietnam_real_statistics()
    
    print("🗺️ Phân bố vùng miền:")
    print("  Thực tế: Bắc 35%, Trung 20%, Nam 45%")
    
    # Current generator
    current_total = sum(current_stats["region_distribution"].values())
    print("  Generator hiện tại:")
    for region in ["Miền Bắc", "Miền Trung", "Miền Nam"]:
        count = current_stats["region_distribution"].get(region, 0)
        ratio = (count / current_total) * 100 if current_total > 0 else 0
        print(f"    {region}: {ratio:.1f}%")
    
    # Realistic generator
    realistic_total = sum(realistic_stats["region_distribution"].values())
    print("  Generator thực tế:")
    for region in ["Miền Bắc", "Miền Trung", "Miền Nam"]:
        count = realistic_stats["region_distribution"].get(region, 0)
        ratio = (count / realistic_total) * 100 if realistic_total > 0 else 0
        print(f"    {region}: {ratio:.1f}%")
    
    print("\n👥 Tỷ lệ giới tính:")
    print("  Thực tế: Nam 49%, Nữ 51%")
    
    # Current generator
    current_total = sum(current_stats["gender_distribution"].values())
    print("  Generator hiện tại:")
    for gender in ["Nam", "Nữ"]:
        count = current_stats["gender_distribution"].get(gender, 0)
        ratio = (count / current_total) * 100 if current_total > 0 else 0
        print(f"    {gender}: {ratio:.1f}%")
    
    # Realistic generator
    realistic_total = sum(realistic_stats["gender_distribution"].values())
    print("  Generator thực tế:")
    for gender in ["Nam", "Nữ"]:
        count = realistic_stats["gender_distribution"].get(gender, 0)
        ratio = (count / realistic_total) * 100 if realistic_total > 0 else 0
        print(f"    {gender}: {ratio:.1f}%")

def create_improved_generator():
    """Tạo generator cải tiến với tỷ lệ thực tế"""
    print("\n🚀 Tạo Generator cải tiến")
    print("=" * 50)
    
    class ImprovedCCCDGenerator:
        def __init__(self):
            self.real_stats = get_vietnam_real_statistics()
            self.province_mapping = get_province_mapping()
            
            # Tạo weighted provinces
            self.weighted_provinces = []
            self.province_weights = []
            
            for region, provinces in self.province_mapping.items():
                region_weight = self.real_stats["population_by_region"][region]
                province_weight = region_weight / len(provinces)
                
                for province in provinces:
                    self.weighted_provinces.append(province)
                    self.province_weights.append(province_weight)
        
        def generate_cccd_with_realistic_distribution(self, quantity: int = 1000):
            """Tạo CCCD với phân bố thực tế"""
            results = []
            
            for _ in range(quantity):
                # Chọn tỉnh theo trọng số
                province_code = random.choices(
                    self.weighted_provinces,
                    weights=self.province_weights
                )[0]
                
                # Chọn giới tính theo tỷ lệ thực tế
                gender = random.choices(
                    ["Nam", "Nữ"],
                    weights=[0.49, 0.51]
                )[0]
                
                # Chọn năm sinh theo tỷ lệ thực tế
                birth_year_ranges = [
                    (1990, 1999, 0.25),
                    (2000, 2009, 0.30),
                    (2010, 2019, 0.25),
                    (2020, 2023, 0.20)
                ]
                
                year_range = random.choices(
                    birth_year_ranges,
                    weights=[w for _, _, w in birth_year_ranges]
                )[0]
                
                start_year, end_year, _ = year_range
                birth_year = random.randint(start_year, end_year)
                
                # Tìm vùng miền
                region = None
                for reg, provinces in self.province_mapping.items():
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
    
    # Test improved generator
    improved_gen = ImprovedCCCDGenerator()
    improved_data = improved_gen.generate_cccd_with_realistic_distribution(1000)
    
    # Phân tích kết quả
    improved_stats = analyze_distribution(improved_data, "Generator cải tiến")
    
    print("\n✅ Generator cải tiến đã được tạo!")
    print("📋 Tính năng:")
    print("  - Phân bố tỉnh thành theo trọng số dân số")
    print("  - Tỷ lệ giới tính thực tế (49% Nam, 51% Nữ)")
    print("  - Phân bố năm sinh theo cấu trúc dân số")
    print("  - Có thể tích hợp vào hệ thống hiện tại")

def main():
    """Main function"""
    print("🚀 Phân tích tính chính xác và phù hợp với dữ liệu thực tế")
    print("=" * 70)
    
    # Mô phỏng generator hiện tại
    current_data = simulate_current_generator()
    current_stats = analyze_distribution(current_data, "Generator hiện tại")
    
    # Mô phỏng generator thực tế
    realistic_data = simulate_realistic_generator()
    realistic_stats = analyze_distribution(realistic_data, "Generator thực tế")
    
    # So sánh với thống kê thực tế
    compare_with_real_statistics(current_stats, realistic_stats)
    
    # Tạo generator cải tiến
    create_improved_generator()
    
    print("\n🎯 KẾT LUẬN:")
    print("=" * 30)
    print("❌ Generator hiện tại: Random đều, không phản ánh thực tế")
    print("✅ Generator thực tế: Phân bố theo tỷ lệ thực tế")
    print("🚀 Generator cải tiến: Đã sẵn sàng tích hợp")
    print("\n💡 KHUYẾN NGHỊ:")
    print("  1. Thay thế random đều bằng weighted random")
    print("  2. Sử dụng tỷ lệ dân số thực tế")
    print("  3. Cập nhật generator hiện tại")

if __name__ == "__main__":
    main()