#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tạo 5000 CCCD cho tỉnh Quảng Ninh, giới tính nữ, năm sinh từ 1965 đến 1975
Sử dụng module cccd_generator_service.py
"""

import sys
import os
import json
import time
from datetime import datetime

# Thêm thư mục cccd vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cccd'))

from cccd.cccd_generator_service import CCCDGeneratorService
from cccd.checksum import is_checksum_valid

def main():
    """Hàm chính để tạo CCCD"""
    print("🚀 Bắt đầu tạo 5000 CCCD cho tỉnh Quảng Ninh, giới tính nữ (1965-1975)")
    print("=" * 70)

    # Khởi tạo generator
    generator = CCCDGeneratorService()

    # Tham số tạo CCCD
    params = {
        "provinceCodes": ["022"],  # Mã tỉnh Quảng Ninh
        "gender": "Nữ",            # Giới tính nữ
        "birthYearRange": [1965, 1975],  # Năm sinh từ 1965 đến 1975
        "quantity": 5000           # Số lượng 5000
    }

    print(f"📋 Tham số tạo CCCD:")
    print(f"   - Tỉnh: Quảng Ninh (022)")
    print(f"   - Giới tính: Nữ")
    print(f"   - Năm sinh: {params['birthYearRange'][0]} - {params['birthYearRange'][1]}")
    print(f"   - Số lượng: {params['quantity']}")
    print()

    # Bắt đầu tạo
    start_time = time.time()
    print("⏳ Đang tạo CCCD...")

    try:
        # Gọi hàm tạo CCCD
        results = generator.generateCccdList(**params)

        end_time = time.time()
        generation_time = end_time - start_time

        # Kiểm tra kết quả
        if isinstance(results, dict) and "error" in results:
            print(f"❌ Lỗi: {results['error']}")
            return

        print("✅ Hoàn thành tạo CCCD!")
        print(f"📊 Thời gian tạo: {generation_time:.2f} giây")
        print(f"📊 Số lượng CCCD tạo được: {len(results)}")
        print()

        # Kiểm tra tính hợp lệ
        valid_count = 0
        invalid_count = 0
        checksum_errors = 0

        print("🔍 Đang kiểm tra tính hợp lệ...")

        for result in results:
            cccd = result.get("cccd_number", "")
            if is_checksum_valid(cccd):
                valid_count += 1
            else:
                invalid_count += 1
                checksum_errors += 1

        print(f"✅ CCCD hợp lệ: {valid_count}")
        print(f"❌ CCCD không hợp lệ: {invalid_count}")
        print(f"📊 Tỷ lệ hợp lệ: {(valid_count / len(results) * 100):.2f}%")
        print()

        # Hiển thị một số mẫu
        print("📋 Mẫu CCCD được tạo:")
        print("-" * 50)
        for i, result in enumerate(results[:10]):
            print(f"{i+1:2d}. {result['cccd_number']} - {result['gender']} - {result['birth_date']} - {result['province_name']}")
        print("-" * 50)
        print()

        # Lưu kết quả vào file
        output_file = "quang_ninh_female_1965_1975.json"
        output_data = {
            "metadata": {
                "description": "5000 CCCD tỉnh Quảng Ninh, giới tính nữ, năm sinh 1965-1975",
                "province": "Quảng Ninh (022)",
                "gender": "Nữ",
                "birth_year_range": [1965, 1975],
                "quantity_requested": 5000,
                "quantity_generated": len(results),
                "generation_time_seconds": generation_time,
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "validity_rate": valid_count / len(results) * 100,
                "generated_at": datetime.now().isoformat(),
                "generator_module": "cccd_generator_service.py"
            },
            "data": results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"💾 Đã lưu kết quả vào file: {output_file}")
        print(f"📁 Kích thước file: {os.path.getsize(output_file)} bytes")
        print()

        # Thống kê thêm
        print("📊 Thống kê chi tiết:")
        print("-" * 30)

        # Thống kê năm sinh
        birth_years = [r.get("birth_year") for r in results if r.get("birth_year")]
        year_counts = {}
        for year in birth_years:
            year_counts[year] = year_counts.get(year, 0) + 1

        print("Năm sinh phân bố:")
        for year in sorted(year_counts.keys()):
            count = year_counts[year]
            percentage = (count / len(results)) * 100
            print(f"{year:4d}: {count:4d} ({percentage:5.1f}%)")

        print()
        print("🎉 Hoàn thành thành công!")

    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()