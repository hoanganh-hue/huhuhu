#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script xử lý batch dữ liệu CCCD - Bước 2 đến bước cuối
Chuyển đổi JSON sang CSV, tạo báo cáo thống kê và phân tích dữ liệu
"""

import sys
import os
import json
import csv
from datetime import datetime
from collections import Counter
from typing import Dict, List, Any
from src.utils.output_manager import get_output_manager, save_to_output, save_report, save_data


def load_cccd_data(json_file: str) -> Dict[str, Any]:
    """Đọc dữ liệu CCCD từ file JSON"""
    print(f"📖 Đang đọc file: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Đã đọc {len(data['data'])} bản ghi CCCD")
    return data

def convert_to_csv(data: Dict[str, Any], csv_file: str) -> None:
    """Chuyển đổi dữ liệu sang định dạng CSV"""
    print(f"📊 Đang chuyển đổi sang CSV: {csv_file}")

    records = data['data']

    if not records:
        print("❌ Không có dữ liệu để chuyển đổi")
        return

    # Lấy các trường từ record đầu tiên
    fieldnames = list(records[0].keys())

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"✅ Đã chuyển đổi thành công sang CSV ({len(records)} bản ghi)")

def analyze_birth_year_distribution(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Phân tích phân bố theo năm sinh"""
    print("📈 Đang phân tích phân bố năm sinh...")

    birth_years = [r.get('birth_year') for r in records if r.get('birth_year')]
    year_counts = Counter(birth_years)

    total = len(birth_years)
    distribution = {}

    for year in sorted(year_counts.keys()):
        count = year_counts[year]
        percentage = (count / total * 100) if total > 0 else 0
        distribution[str(year)] = {
            'count': count,
            'percentage': round(percentage, 2)
        }

    return distribution

def analyze_age_distribution(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Phân tích phân bố theo độ tuổi hiện tại"""
    print("📈 Đang phân tích phân bố độ tuổi...")

    current_year = datetime.now().year
    ages = []

    for record in records:
        birth_year = record.get('birth_year')
        if birth_year:
            age = current_year - birth_year
            ages.append(age)

    age_counts = Counter(ages)
    total = len(ages)
    distribution = {}

    for age in sorted(age_counts.keys()):
        count = age_counts[age]
        percentage = (count / total * 100) if total > 0 else 0
        distribution[str(age)] = {
            'count': count,
            'percentage': round(percentage, 2)
        }

    return distribution

def analyze_month_distribution(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Phân tích phân bố theo tháng sinh"""
    print("📈 Đang phân tích phân bố tháng sinh...")

    months = [r.get('birth_month') for r in records if r.get('birth_month')]
    month_counts = Counter(months)

    total = len(months)
    distribution = {}

    for month in range(1, 13):
        count = month_counts.get(month, 0)
        percentage = (count / total * 100) if total > 0 else 0
        distribution[str(month)] = {
            'count': count,
            'percentage': round(percentage, 2)
        }

    return distribution

def generate_comprehensive_report(data: Dict[str, Any], output_dir: str = "reports") -> None:
    """Tạo báo cáo tổng hợp chi tiết"""
    print("📋 Đang tạo báo cáo tổng hợp...")

    # Tạo thư mục reports nếu chưa có
    os.makedirs(output_dir, exist_ok=True)

    records = data['data']
    metadata = data['metadata']

    # Phân tích dữ liệu
    birth_year_dist = analyze_birth_year_distribution(records)
    age_dist = analyze_age_distribution(records)
    month_dist = analyze_month_distribution(records)

    # Tạo báo cáo
    report_content = f"""
# 📊 BÁO CÁO PHÂN TÍCH DỮ LIỆU CCCD
## Tỉnh Quảng Ninh - Giới tính Nữ (1965-1975)

**Thời gian tạo báo cáo:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📋 THÔNG TIN CHUNG

- **Tỉnh/Thành phố:** {metadata['province']}
- **Giới tính:** {metadata['gender']}
- **Khoảng năm sinh:** {metadata['birth_year_range'][0]} - {metadata['birth_year_range'][1]}
- **Số lượng yêu cầu:** {metadata['quantity_requested']:,}
- **Số lượng tạo được:** {metadata['quantity_generated']:,}
- **Tỷ lệ hợp lệ:** {metadata['validity_rate']:.1f}%
- **Thời gian tạo:** {metadata['generation_time_seconds']:.3f} giây

---

## 📈 PHÂN BỐ THEO NĂM SINH

| Năm sinh | Số lượng | Tỷ lệ (%) |
|----------|----------|-----------|
"""

    for year, info in birth_year_dist.items():
        report_content += f"| {year} | {info['count']:,} | {info['percentage']:.1f}% |\n"

    report_content += "\n---\n\n## 📈 PHÂN BỐ THEO ĐỘ TUỔI HIỆN TẠI\n\n"
    report_content += "| Độ tuổi | Số lượng | Tỷ lệ (%) |\n"
    report_content += "|---------|----------|-----------|\n"

    for age, info in age_dist.items():
        report_content += f"| {age} | {info['count']:,} | {info['percentage']:.1f}% |\n"

    report_content += "\n---\n\n## 📈 PHÂN BỐ THEO THÁNG SINH\n\n"
    report_content += "| Tháng | Số lượng | Tỷ lệ (%) |\n"
    report_content += "|-------|----------|-----------|\n"

    for month, info in month_dist.items():
        report_content += f"| {month} | {info['count']:,} | {info['percentage']:.1f}% |\n"

    report_content += "\n---\n\n## 🎯 THỐNG KÊ VALIDATION\n\n"
    report_content += f"- **Tổng số CCCD:** {len(records):,}\n"
    report_content += f"- **CCCD hợp lệ:** {metadata['valid_count']:,}\n"
    report_content += f"- **CCCD không hợp lệ:** {metadata['invalid_count']:,}\n"
    report_content += f"- **Tỷ lệ chính xác:** {metadata['validity_rate']:.2f}%\n"

    # Lưu báo cáo
    report_file = os.path.join(output_dir, "bao_cao_cccd_quang_ninh_1965_1975.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"✅ Đã tạo báo cáo: {report_file}")

def create_summary_csv(data: Dict[str, Any], output_dir: str = "reports") -> None:
    """Tạo file CSV tóm tắt thống kê"""
    print("📊 Đang tạo file CSV tóm tắt...")

    os.makedirs(output_dir, exist_ok=True)

    records = data['data']
    metadata = data['metadata']

    # Phân tích dữ liệu
    birth_year_dist = analyze_birth_year_distribution(records)
    age_dist = analyze_age_distribution(records)

    # Tạo file CSV tóm tắt
    summary_file = os.path.join(output_dir, "thong_ke_cccd_quang_ninh_1965_1975.csv")

    with open(summary_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow(['Chỉ số', 'Giá trị', 'Đơn vị'])

        # Thông tin chung
        writer.writerow(['Tỉnh/Thành phố', metadata['province'], ''])
        writer.writerow(['Giới tính', metadata['gender'], ''])
        writer.writerow(['Năm sinh từ', metadata['birth_year_range'][0], ''])
        writer.writerow(['Năm sinh đến', metadata['birth_year_range'][1], ''])
        writer.writerow(['Số lượng yêu cầu', metadata['quantity_requested'], 'CCCD'])
        writer.writerow(['Số lượng tạo được', metadata['quantity_generated'], 'CCCD'])
        writer.writerow(['Tỷ lệ hợp lệ', f"{metadata['validity_rate']:.2f}", '%'])
        writer.writerow(['Thời gian tạo', f"{metadata['generation_time_seconds']:.3f}", 'giây'])

        # Phân bố năm sinh
        writer.writerow([])
        writer.writerow(['=== PHÂN BỐ THEO NĂM SINH ===', '', ''])
        for year, info in birth_year_dist.items():
            writer.writerow([f'Năm {year}', info['count'], f"{info['percentage']:.1f}%"])

        # Phân bố độ tuổi
        writer.writerow([])
        writer.writerow(['=== PHÂN BỐ THEO ĐỘ TUỔI ===', '', ''])
        for age, info in age_dist.items():
            writer.writerow([f'Tuổi {age}', info['count'], f"{info['percentage']:.1f}%"])

    print(f"✅ Đã tạo file CSV tóm tắt: {summary_file}")

def main():
    """Hàm chính để xử lý batch CCCD"""
    print("🚀 Bắt đầu xử lý batch dữ liệu CCCD - Bước 2 đến bước cuối")
    print("=" * 80)

    # File input
    json_file = "quang_ninh_female_1965_1975.json"

    if not os.path.exists(json_file):
        print(f"❌ Không tìm thấy file: {json_file}")
        return

    try:
        # Bước 1: Đọc dữ liệu
        data = load_cccd_data(json_file)

        # Bước 2: Chuyển đổi sang CSV
        csv_file = "quang_ninh_female_1965_1975.csv"
        convert_to_csv(data, csv_file)

        # Bước 3: Tạo báo cáo tổng hợp
        generate_comprehensive_report(data)

        # Bước 4: Tạo file CSV tóm tắt
        create_summary_csv(data)

        print("\n" + "=" * 80)
        print("🎉 HOÀN THÀNH XỬ LÝ BATCH DỮ LIỆU CCCD!")
        print("=" * 80)

        print("\n📁 Các file đã tạo:")
        print("├── quang_ninh_female_1965_1975.csv (dữ liệu CSV)")
        print("├── reports/")
        print("│   ├── bao_cao_cccd_quang_ninh_1965_1975.md (báo cáo chi tiết)")
        print("│   └── thong_ke_cccd_quang_ninh_1965_1975.csv (thống kê tóm tắt)")

        print("\n📊 Tóm tắt:")
        print(f"   - Tổng số CCCD: {len(data['data']):,}")
        print(f"   - Tỷ lệ hợp lệ: {data['metadata']['validity_rate']:.1f}%")
        print(f"   - Thời gian xử lý: {data['metadata']['generation_time_seconds']:.3f} giây")

    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()