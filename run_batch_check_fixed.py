#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chạy lại batch check CCCD với scraper đã sửa
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
import time
from src.utils.output_manager import get_output_manager, save_to_output, save_report, save_data


# Thêm path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'check-cccd', 'src'))

def load_cccd_from_excel(excel_file: str) -> list:
    """Load danh sách CCCD từ file Excel"""
    try:
        df = pd.read_excel(excel_file, sheet_name='CCCD_Data')
        cccd_list = df['CCCD'].dropna().astype(str).tolist()
        print(f"✅ Đã load {len(cccd_list)} CCCD từ file Excel")
        return cccd_list
    except Exception as e:
        print(f"❌ Lỗi khi đọc file Excel: {e}")
        return []

def batch_check_cccd(cccd_list: list, batch_size: int = 5, delay: float = 3.0):
    """Chạy batch check CCCD với scraper đã sửa"""
    from check_cccd.scraper import scrape_cccd_sync

    results = []
    total_batches = (len(cccd_list) + batch_size - 1) // batch_size

    print(f"🚀 Bắt đầu batch check {len(cccd_list)} CCCD")
    print(f"📊 Batch size: {batch_size}, Delay: {delay}s")
    print(f"📦 Tổng số batches: {total_batches}")
    print("=" * 60)

    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(cccd_list))
        batch_cccds = cccd_list[start_idx:end_idx]

        print(f"\n🔄 Batch {batch_idx + 1}/{total_batches}: CCCD {start_idx + 1}-{end_idx}")

        for i, cccd in enumerate(batch_cccds):
            try:
                print(f"  📋 Checking CCCD {start_idx + i + 1}/{len(cccd_list)}: {cccd}")

                # Call scraper
                result = scrape_cccd_sync(cccd)

                # Extract key information
                status = result.get('status', 'unknown')
                matches_count = len(result.get('matches', []))

                if matches_count > 0:
                    match = result['matches'][0]
                    tax_code = match.get('tax_code', '')
                    name = match.get('name', '')
                    address = match.get('address', '')
                    role = match.get('role', '')
                else:
                    tax_code = name = address = role = ''

                # Store result
                result_data = {
                    'STT': start_idx + i + 1,
                    'CCCD': cccd,
                    'Trạng thái check': status,
                    'Thời gian response': f"{result.get('duration_ms', 0):.0f}ms",
                    'API Status': 'completed' if status != 'error' else 'error',
                    'Kết quả tìm kiếm': f"Tìm thấy {matches_count} kết quả" if matches_count > 0 else "Không tìm thấy",
                    'Số matches': matches_count,
                    'Tên': name,
                    'Mã số thuế': tax_code,
                    'Địa chỉ': address,
                    'Chức vụ': role,
                    'URL': result['matches'][0].get('url', '') if result.get('matches') else '',
                    'Lỗi': result.get('error_message', '')
                }

                results.append(result_data)

                print(f"    ✅ Status: {status}, Matches: {matches_count}")
                if tax_code:
                    print(f"    🔢 Tax Code: {tax_code}")

            except Exception as e:
                print(f"    ❌ Error checking CCCD {cccd}: {e}")
                results.append({
                    'STT': start_idx + i + 1,
                    'CCCD': cccd,
                    'Trạng thái check': 'error',
                    'Thời gian response': '0ms',
                    'API Status': 'error',
                    'Kết quả tìm kiếm': 'Lỗi',
                    'Số matches': 0,
                    'Tên': '',
                    'Mã số thuế': '',
                    'Địa chỉ': '',
                    'Chức vụ': '',
                    'URL': '',
                    'Lỗi': str(e)
                })

        # Delay between batches
        if batch_idx < total_batches - 1:
            print(f"⏳ Đợi {delay}s trước batch tiếp theo...")
            time.sleep(delay)

    return results

def create_comprehensive_report(results: list):
    """Tạo báo cáo Excel chi tiết"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"batch_check_results_fixed_{timestamp}.xlsx"

    print(f"\n💾 Tạo báo cáo Excel: {excel_file}")

    # Create DataFrame
    df = pd.DataFrame(results)

    # Create Excel writer with multiple sheets
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:

        # Sheet 1: Ket_Qua_Check
        df.to_excel(writer, sheet_name='Ket_Qua_Check', index=False)

        # Sheet 2: Thong_Ke
        stats_data = create_statistics_sheet(df)
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Thong_Ke', index=False)

        # Sheet 3: Tom_Tat
        summary_data = create_summary_sheet(df, timestamp)
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Tom_Tat', index=False)

    print(f"✅ Đã tạo file Excel: {excel_file}")
    print(f"📊 Kích thước: {os.path.getsize(excel_file)} bytes")

    return excel_file

def create_statistics_sheet(df: pd.DataFrame) -> list:
    """Tạo sheet thống kê"""
    stats = []

    # Basic stats
    total_cccd = len(df)
    found_count = len(df[df['Trạng thái check'] == 'found'])
    not_found_count = len(df[df['Trạng thái check'] == 'not_found'])
    error_count = len(df[df['Trạng thái check'] == 'error'])

    stats.append({'Chỉ số': 'Tổng số CCCD', 'Giá trị': total_cccd})
    stats.append({'Chỉ số': 'Tìm thấy công ty', 'Giá trị': found_count})
    stats.append({'Chỉ số': 'Không tìm thấy', 'Giá trị': not_found_count})
    stats.append({'Chỉ số': 'Lỗi', 'Giá trị': error_count})
    stats.append({'Chỉ số': 'Tỷ lệ thành công', 'Giá trị': f"{(found_count/total_cccd*100):.1f}%" if total_cccd > 0 else "0%"})

    # Tax code analysis
    unique_tax_codes = df['Mã số thuế'].dropna().nunique()
    duplicate_tax_codes = len(df) - len(df['Mã số thuế'].dropna().unique()) if len(df['Mã số thuế'].dropna()) > 0 else 0

    stats.append({'Chỉ số': 'Mã số thuế unique', 'Giá trị': unique_tax_codes})
    stats.append({'Chỉ số': 'Mã số thuế trùng lặp', 'Giá trị': duplicate_tax_codes})

    return stats

def create_summary_sheet(df: pd.DataFrame, timestamp: str) -> list:
    """Tạo sheet tóm tắt"""
    summary = []

    summary.append({'Thông tin': 'Thời gian tạo', 'Giá trị': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    summary.append({'Thông tin': 'File nguồn', 'Giá trị': 'quang_ninh_female_1965_1975.xlsx'})
    summary.append({'Thông tin': 'Scraper version', 'Giá trị': 'Fixed v1.0'})
    summary.append({'Thông tin': 'API Endpoint', 'Giá trị': 'http://localhost:8000/api/v1/check'})
    summary.append({'Thông tin': 'Batch size', 'Giá trị': '5 CCCD/batch'})
    summary.append({'Thông tin': 'Delay giữa batches', 'Giá trị': '3 giây'})

    # Status distribution
    status_counts = df['Trạng thái check'].value_counts()
    for status, count in status_counts.items():
        summary.append({'Thông tin': f'Status {status}', 'Giá trị': f"{count} CCCD"})

    return summary

def main():
    """Main function"""
    print("🔧 BATCH CHECK CCCD - SCRAPER ĐÃ SỬA")
    print("=" * 60)

    # Load CCCD list from Excel
    excel_file = "quang_ninh_female_1965_1975.xlsx"
    cccd_list = load_cccd_from_excel(excel_file)

    if not cccd_list:
        print("❌ Không thể load danh sách CCCD")
        return

    # Take first 20 CCCD for testing (to avoid long wait)
    test_cccd_list = cccd_list[:20]
    print(f"🧪 Test với {len(test_cccd_list)} CCCD đầu tiên")

    # Run batch check
    results = batch_check_cccd(test_cccd_list, batch_size=5, delay=3.0)

    # Create report
    excel_file = create_comprehensive_report(results)

    # Summary
    print("\n" + "=" * 60)
    print("📊 TÓM TẮT KẾT QUẢ")
    print("=" * 60)

    found_count = sum(1 for r in results if r['Trạng thái check'] == 'found')
    not_found_count = sum(1 for r in results if r['Trạng thái check'] == 'not_found')
    error_count = sum(1 for r in results if r['Trạng thái check'] == 'error')

    print(f"✅ Tìm thấy công ty: {found_count}")
    print(f"❌ Không tìm thấy: {not_found_count}")
    print(f"⚠️  Lỗi: {error_count}")

    # Check for duplicate tax codes
    tax_codes = [r['Mã số thuế'] for r in results if r['Mã số thuế']]
    unique_tax_codes = len(set(tax_codes))
    duplicate_count = len(tax_codes) - unique_tax_codes

    print(f"🔢 Mã số thuế unique: {unique_tax_codes}")
    print(f"🔄 Mã số thuế trùng lặp: {duplicate_count}")

    if duplicate_count == 0:
        print("🎉 KHÔNG CÒN MÃ SỐ THUẾ TRÙNG LẶP!")
    else:
        print("⚠️  Vẫn còn mã số thuế trùng lặp")

    print(f"\n📁 File kết quả: {excel_file}")

if __name__ == "__main__":
    main()