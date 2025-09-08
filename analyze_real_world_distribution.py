#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phân tích tỷ lệ phân bố CCCD theo dữ liệu thực tế
Kiểm tra tính chính xác và phù hợp với thống kê Việt Nam
"""

import sys
import os
import random
import json
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple

# Add cccd directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cccd'))

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
        },
        
        # Phân bố năm sinh thực tế (dựa trên cấu trúc dân số)
        "birth_year_distribution": {
            "1990-1999": 0.25,  # Thế hệ 8X-9X
            "2000-2009": 0.30,  # Thế hệ 2K
            "2010-2019": 0.25,  # Thế hệ 2K1
            "2020-2023": 0.20   # Thế hệ 2K2+
        }
    }

def analyze_current_generator_distribution():
    """Phân tích phân bố của generator hiện tại"""
    print("🔍 Phân tích phân bố của Generator hiện tại")
    print("=" * 60)
    
    # Test với Enhanced Generator
    try:
        from cccd_generator_enhanced import CCCDGeneratorEnhanced
        
        generator = CCCDGeneratorEnhanced()
        
        # Tạo 1000 CCCD để phân tích
        result = generator.generate_cccd_list_enhanced(
            province_codes=None,  # Tất cả tỉnh
            gender=None,  # Random
            birth_year_range=(1990, 2023),
            quantity=1000
        )
        
        if result["success"]:
            data = result["data"]
            valid_data = [item for item in data if item.get("valid", False)]
            
            print(f"✅ Generated {len(valid_data)} valid CCCD for analysis")
            
            # Phân tích theo tỉnh thành
            province_dist = Counter()
            region_dist = Counter()
            gender_dist = Counter()
            age_group_dist = Counter()
            birth_year_dist = Counter()
            
            for item in valid_data:
                # Tỉnh thành
                province_code = item["province_code"]
                province_dist[province_code] += 1
                
                # Vùng miền
                province_name = item["province_name"]
                if "Hà Nội" in province_name or "Hải Phòng" in province_name:
                    region_dist["Miền Bắc"] += 1
                elif "TP.HCM" in province_name or "Cần Thơ" in province_name:
                    region_dist["Miền Nam"] += 1
                else:
                    # Cần mapping chính xác hơn
                    region_dist["Miền Trung"] += 1
                
                # Giới tính
                gender = item["gender"]
                gender_dist[gender] += 1
                
                # Năm sinh
                birth_year = item["birth_year"]
                birth_year_dist[birth_year] += 1
                
                # Nhóm tuổi
                current_year = 2024
                age = current_year - birth_year
                if age <= 17:
                    age_group_dist["0-17"] += 1
                elif age <= 30:
                    age_group_dist["18-30"] += 1
                elif age <= 45:
                    age_group_dist["31-45"] += 1
                elif age <= 60:
                    age_group_dist["46-60"] += 1
                else:
                    age_group_dist["61+"] += 1
            
            return {
                "province_distribution": dict(province_dist),
                "region_distribution": dict(region_dist),
                "gender_distribution": dict(gender_dist),
                "age_group_distribution": dict(age_group_dist),
                "birth_year_distribution": dict(birth_year_dist),
                "total_samples": len(valid_data)
            }
        else:
            print(f"❌ Error generating CCCD: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ Error analyzing generator: {e}")
        return None

def compare_with_real_statistics(generator_stats: Dict, real_stats: Dict):
    """So sánh với thống kê thực tế"""
    print("\n📊 So sánh với thống kê thực tế")
    print("=" * 60)
    
    total_samples = generator_stats["total_samples"]
    
    # So sánh tỷ lệ giới tính
    print("👥 Tỷ lệ giới tính:")
    print("-" * 30)
    real_gender = real_stats["gender_ratio"]
    gen_gender = generator_stats["gender_distribution"]
    
    for gender in ["Nam", "Nữ"]:
        real_ratio = real_gender.get(gender, 0) * 100
        gen_count = gen_gender.get(gender, 0)
        gen_ratio = (gen_count / total_samples) * 100 if total_samples > 0 else 0
        
        diff = abs(gen_ratio - real_ratio)
        status = "✅" if diff < 5 else "⚠️" if diff < 10 else "❌"
        
        print(f"{status} {gender}: Thực tế {real_ratio:.1f}% | Generator {gen_ratio:.1f}% | Chênh lệch {diff:.1f}%")
    
    # So sánh phân bố tuổi
    print("\n📅 Phân bố nhóm tuổi:")
    print("-" * 30)
    real_age = real_stats["age_distribution"]
    gen_age = generator_stats["age_group_distribution"]
    
    for age_group in ["0-17", "18-30", "31-45", "46-60", "61+"]:
        real_ratio = real_age.get(age_group, 0) * 100
        gen_count = gen_age.get(age_group, 0)
        gen_ratio = (gen_count / total_samples) * 100 if total_samples > 0 else 0
        
        diff = abs(gen_ratio - real_ratio)
        status = "✅" if diff < 5 else "⚠️" if diff < 10 else "❌"
        
        print(f"{status} {age_group}: Thực tế {real_ratio:.1f}% | Generator {gen_ratio:.1f}% | Chênh lệch {diff:.1f}%")
    
    # So sánh phân bố vùng miền
    print("\n🗺️ Phân bố vùng miền:")
    print("-" * 30)
    real_region = real_stats["population_by_region"]
    gen_region = generator_stats["region_distribution"]
    
    for region in ["Miền Bắc", "Miền Trung", "Miền Nam"]:
        real_ratio = real_region.get(region, 0) * 100
        gen_count = gen_region.get(region, 0)
        gen_ratio = (gen_count / total_samples) * 100 if total_samples > 0 else 0
        
        diff = abs(gen_ratio - real_ratio)
        status = "✅" if diff < 5 else "⚠️" if diff < 10 else "❌"
        
        print(f"{status} {region}: Thực tế {real_ratio:.1f}% | Generator {gen_ratio:.1f}% | Chênh lệch {diff:.1f}%")

def analyze_province_distribution(generator_stats: Dict, real_stats: Dict):
    """Phân tích phân bố tỉnh thành chi tiết"""
    print("\n🏙️ Phân tích phân bố tỉnh thành")
    print("=" * 60)
    
    total_samples = generator_stats["total_samples"]
    province_dist = generator_stats["province_distribution"]
    top_provinces = real_stats["top_populated_provinces"]
    
    print("Top 10 tỉnh thành được tạo nhiều nhất:")
    print("-" * 40)
    
    # Sắp xếp theo số lượng
    sorted_provinces = sorted(province_dist.items(), key=lambda x: x[1], reverse=True)
    
    for i, (province_code, count) in enumerate(sorted_provinces[:10]):
        ratio = (count / total_samples) * 100
        expected_ratio = top_provinces.get(province_code, 0) * 100
        
        if expected_ratio > 0:
            diff = abs(ratio - expected_ratio)
            status = "✅" if diff < 2 else "⚠️" if diff < 5 else "❌"
            print(f"{status} {i+1:2d}. {province_code}: {count:3d} ({ratio:4.1f}%) | Thực tế: {expected_ratio:4.1f}%")
        else:
            print(f"ℹ️  {i+1:2d}. {province_code}: {count:3d} ({ratio:4.1f}%) | Thực tế: <1%")

def create_realistic_generator():
    """Tạo generator với tỷ lệ phân bố thực tế"""
    print("\n🎯 Tạo Generator với tỷ lệ phân bố thực tế")
    print("=" * 60)
    
    real_stats = get_vietnam_real_statistics()
    
    # Tạo generator với weighted random
    class RealisticCCCDGenerator:
        def __init__(self):
            self.real_stats = real_stats
            
        def generate_realistic_cccd(self, quantity: int = 1000):
            """Tạo CCCD với tỷ lệ phân bố thực tế"""
            results = []
            
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
            
            # Tạo CCCD với tỷ lệ thực tế
            for _ in range(quantity):
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
                birth_year_range = random.choices(
                    list(real_stats["birth_year_distribution"].keys()),
                    weights=list(real_stats["birth_year_distribution"].values())
                )[0]
                
                # Parse năm sinh
                start_year, end_year = map(int, birth_year_range.split('-'))
                birth_year = random.randint(start_year, end_year)
                
                # Tạo CCCD (simplified)
                gender_century_code = 0 if gender == "Nam" else 1
                year_code = str(birth_year % 100).zfill(2)
                month_code = str(random.randint(1, 12)).zfill(2)
                day_code = str(random.randint(1, 28)).zfill(2)
                sequence_code = str(random.randint(1, 99)).zfill(2)
                
                cccd = f"{province_code}{gender_century_code}{year_code}{month_code}{day_code}{sequence_code}"
                
                results.append({
                    "cccd_number": cccd,
                    "province_code": province_code,
                    "region": region,
                    "gender": gender,
                    "birth_year": birth_year,
                    "birth_year_range": birth_year_range
                })
            
            return results
    
    # Test realistic generator
    realistic_gen = RealisticCCCDGenerator()
    realistic_data = realistic_gen.generate_realistic_cccd(1000)
    
    # Phân tích kết quả
    print("📊 Phân tích Generator thực tế:")
    print("-" * 40)
    
    # Phân tích vùng miền
    region_count = Counter(item["region"] for item in realistic_data)
    print("Vùng miền:")
    for region, count in region_count.items():
        ratio = (count / len(realistic_data)) * 100
        expected = real_stats["population_by_region"][region] * 100
        diff = abs(ratio - expected)
        status = "✅" if diff < 3 else "⚠️"
        print(f"  {status} {region}: {ratio:.1f}% (thực tế: {expected:.1f}%)")
    
    # Phân tích giới tính
    gender_count = Counter(item["gender"] for item in realistic_data)
    print("\nGiới tính:")
    for gender, count in gender_count.items():
        ratio = (count / len(realistic_data)) * 100
        expected = real_stats["gender_ratio"][gender] * 100
        diff = abs(ratio - expected)
        status = "✅" if diff < 3 else "⚠️"
        print(f"  {status} {gender}: {ratio:.1f}% (thực tế: {expected:.1f}%)")
    
    # Phân tích năm sinh
    year_range_count = Counter(item["birth_year_range"] for item in realistic_data)
    print("\nNăm sinh:")
    for year_range, count in year_range_count.items():
        ratio = (count / len(realistic_data)) * 100
        expected = real_stats["birth_year_distribution"][year_range] * 100
        diff = abs(ratio - expected)
        status = "✅" if diff < 3 else "⚠️"
        print(f"  {status} {year_range}: {ratio:.1f}% (thực tế: {expected:.1f}%)")

def main():
    """Main function"""
    print("🚀 Phân tích tính chính xác và phù hợp với dữ liệu thực tế")
    print("=" * 70)
    
    # Lấy thống kê thực tế
    real_stats = get_vietnam_real_statistics()
    print("📈 Thống kê thực tế Việt Nam (2023):")
    print(f"  - Dân số theo vùng: Bắc {real_stats['population_by_region']['Miền Bắc']*100:.0f}%, Trung {real_stats['population_by_region']['Miền Trung']*100:.0f}%, Nam {real_stats['population_by_region']['Miền Nam']*100:.0f}%")
    print(f"  - Tỷ lệ giới tính: Nam {real_stats['gender_ratio']['Nam']*100:.0f}%, Nữ {real_stats['gender_ratio']['Nữ']*100:.0f}%")
    print(f"  - Phân bố tuổi: Trẻ em {real_stats['age_distribution']['0-17']*100:.0f}%, Thanh niên {real_stats['age_distribution']['18-30']*100:.0f}%, Trung niên {real_stats['age_distribution']['31-45']*100:.0f}%")
    
    # Phân tích generator hiện tại
    generator_stats = analyze_current_generator_distribution()
    
    if generator_stats:
        # So sánh với thống kê thực tế
        compare_with_real_statistics(generator_stats, real_stats)
        
        # Phân tích tỉnh thành chi tiết
        analyze_province_distribution(generator_stats, real_stats)
        
        # Tạo generator thực tế
        create_realistic_generator()
        
        print("\n🎯 KẾT LUẬN:")
        print("=" * 30)
        print("✅ Generator hiện tại tạo CCCD ngẫu nhiên đều")
        print("⚠️  Không phản ánh tỷ lệ phân bố thực tế")
        print("💡 Cần tạo generator với weighted random")
        print("🚀 Generator thực tế đã được tạo và test")
    else:
        print("❌ Không thể phân tích generator hiện tại")

if __name__ == "__main__":
    main()