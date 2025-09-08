#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để chuyển đổi dữ liệu CCCD từ JSON sang Excel
Tự động hóa quá trình xuất kết quả ra file Excel
"""

import json
import pandas as pd
import os
from datetime import datetime
import sys

def convert_json_to_excel(json_file: str, excel_file: str = None):
    """Chuyển đổi file JSON chứa dữ liệu CCCD sang Excel"""

    print("🚀 Bắt đầu chuyển đổi dữ liệu từ JSON sang Excel")
    print("=" * 60)

    # Kiểm tra file JSON tồn tại
    if not os.path.exists(json_file):
        print(f"❌ File JSON không tồn tại: {json_file}")
        return False

    try:
        # Đọc file JSON
        print(f"📖 Đang đọc file JSON: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Kiểm tra cấu trúc dữ liệu
        if not isinstance(data, dict) or 'data' not in data:
            print("❌ Cấu trúc file JSON không hợp lệ")
            return False

        # Lấy metadata
        metadata = data.get('metadata', {})
        cccd_data = data['data']

        print(f"📊 Số lượng CCCD: {len(cccd_data)}")
        print(f"📋 Mô tả: {metadata.get('description', 'N/A')}")

        # Chuyển đổi sang DataFrame
        print("🔄 Đang chuyển đổi dữ liệu...")

        # Chuẩn bị dữ liệu cho DataFrame
        df_data = []
        for item in cccd_data:
            row = {
                'STT': len(df_data) + 1,
                'CCCD': item.get('cccd_number', ''),
                'Giới tính': item.get('gender', ''),
                'Ngày sinh': item.get('birth_date', ''),
                'Năm sinh': item.get('birth_year', ''),
                'Tỉnh/Thành': item.get('province_name', ''),
                'Mã tỉnh': item.get('province_code', ''),
                'Tuổi': datetime.now().year - item.get('birth_year', 2000) if item.get('birth_year') else '',
                'Checksum hợp lệ': item.get('valid', True)
            }
            df_data.append(row)

        # Tạo DataFrame
        df = pd.DataFrame(df_data)

        # Tên file Excel mặc định
        if excel_file is None:
            base_name = os.path.splitext(json_file)[0]
            excel_file = f"{base_name}.xlsx"

        # Xuất ra Excel
        print(f"💾 Đang xuất file Excel: {excel_file}")

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Sheet chính chứa dữ liệu
            df.to_excel(writer, sheet_name='CCCD_Data', index=False)

            # Sheet thống kê
            stats_data = create_statistics_sheet(df, metadata)
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Thong_Ke', index=False)

            # Sheet metadata
            metadata_df = pd.DataFrame([metadata])
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

        print("✅ Hoàn thành chuyển đổi!")
        print(f"📁 File Excel: {excel_file}")
        print(f"📊 Kích thước: {os.path.getsize(excel_file)} bytes")
        print(f"📋 Số dòng dữ liệu: {len(df)}")

        return True

    except Exception as e:
        print(f"❌ Lỗi khi chuyển đổi: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_statistics_sheet(df: pd.DataFrame, metadata: dict) -> list:
    """Tạo sheet thống kê"""

    stats = []

    # Thống kê tổng quan
    stats.append({'Chỉ số': 'Tổng số CCCD', 'Giá trị': len(df)})
    stats.append({'Chỉ số': 'Tỉnh/Thành', 'Giá trị': metadata.get('province', 'N/A')})
    stats.append({'Chỉ số': 'Giới tính', 'Giá trị': metadata.get('gender', 'N/A')})
    stats.append({'Chỉ số': 'Khoảng năm sinh', 'Giá trị': f"{metadata.get('birth_year_range', [0, 0])[0]}-{metadata.get('birth_year_range', [0, 0])[1]}"})

    # Thống kê theo năm sinh
    if 'Năm sinh' in df.columns:
        year_stats = df['Năm sinh'].value_counts().sort_index()
        for year, count in year_stats.items():
            percentage = (count / len(df)) * 100
            stats.append({'Chỉ số': f'Năm {year}', 'Giá trị': f"{count} ({percentage:.1f}%)"})

    # Thống kê theo giới tính
    if 'Giới tính' in df.columns:
        gender_stats = df['Giới tính'].value_counts()
        for gender, count in gender_stats.items():
            percentage = (count / len(df)) * 100
            stats.append({'Chỉ số': f'Giới tính {gender}', 'Giá trị': f"{count} ({percentage:.1f}%)"})

    # Thống kê checksum
    if 'Checksum hợp lệ' in df.columns:
        valid_count = df['Checksum hợp lệ'].sum()
        invalid_count = len(df) - valid_count
        valid_percentage = (valid_count / len(df)) * 100
        stats.append({'Chỉ số': 'Checksum hợp lệ', 'Giá trị': f"{valid_count} ({valid_percentage:.1f}%)"})
        stats.append({'Chỉ số': 'Checksum không hợp lệ', 'Giá trị': f"{invalid_count} ({(100-valid_percentage):.1f}%)"})

    return stats

def main():
    """Hàm chính"""
    # File JSON đầu vào
    json_file = "quang_ninh_female_1965_1975.json"

    # File Excel đầu ra
    excel_file = "quang_ninh_female_1965_1975.xlsx"

    # Chuyển đổi
    success = convert_json_to_excel(json_file, excel_file)

    if success:
        print("\n🎉 Chuyển đổi hoàn thành thành công!")
        print(f"📂 File Excel được tạo: {excel_file}")

        # Hiển thị thông tin file
        if os.path.exists(excel_file):
            file_size = os.path.getsize(excel_file)
            print(f"📊 Kích thước file: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    else:
        print("\n❌ Chuyển đổi thất bại!")
        sys.exit(1)

if __name__ == "__main__":
    main()