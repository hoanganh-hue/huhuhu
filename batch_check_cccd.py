#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để batch check 5000 CCCD Quảng Ninh nữ (1965-1975) qua hệ thống check CCCD
Đọc dữ liệu từ file Excel, gửi request batch, và xuất kết quả tổng hợp
"""

import pandas as pd
import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Any
import sys
from src.utils.output_manager import get_output_manager, save_to_output, save_report, save_data


class BatchCCCDChecker:
    """Class để batch check CCCD qua API."""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.check_endpoint = f"{self.api_base_url}/api/v1/check"
        self.session = requests.Session()
        self.results = []
        self.stats = {
            'total_processed': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'found_matches': 0,
            'not_found': 0,
            'errors': 0,
            'total_time': 0
        }

    def load_cccd_from_excel(self, excel_file: str) -> List[str]:
        """Đọc danh sách CCCD từ file Excel."""
        print(f"📖 Đang đọc file Excel: {excel_file}")

        try:
            # Đọc sheet chính chứa dữ liệu CCCD
            df = pd.read_excel(excel_file, sheet_name='CCCD_Data')

            # Lấy cột CCCD
            if 'CCCD' not in df.columns:
                print("❌ Không tìm thấy cột 'CCCD' trong file Excel")
                return []

            # Convert CCCD to string properly
            cccd_list = []
            for cccd in df['CCCD'].dropna():
                cccd_str = str(int(cccd))  # Convert to int first, then to string
                # Add leading zero if needed to make 12 digits
                if len(cccd_str) == 11:
                    cccd_str = '0' + cccd_str
                cccd_list.append(cccd_str)

            # Validate format CCCD (12 digits)
            valid_cccd = [cccd for cccd in cccd_list if len(cccd) == 12 and cccd.isdigit()]

            print(f"✅ Đã đọc {len(valid_cccd)} CCCD hợp lệ từ {len(cccd_list)} bản ghi")
            return valid_cccd

        except Exception as e:
            print(f"❌ Lỗi khi đọc file Excel: {e}")
            return []

    def check_single_cccd(self, cccd: str) -> Dict[str, Any]:
        """Check một CCCD qua API."""
        try:
            payload = {
                "cccd": cccd,
                "async_mode": False
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Batch-CCCD-Checker/1.0"
            }

            start_time = time.time()
            response = self.session.post(
                self.check_endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    'cccd': cccd,
                    'status': 'success',
                    'response_time': response_time,
                    'api_status': result.get('status'),
                    'data': result.get('result'),
                    'error': None
                }
            else:
                return {
                    'cccd': cccd,
                    'status': 'error',
                    'response_time': response_time,
                    'api_status': None,
                    'data': None,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                'cccd': cccd,
                'status': 'error',
                'response_time': time.time() - time.time(),  # Will be 0
                'api_status': None,
                'data': None,
                'error': str(e)
            }

    def batch_check_cccd(self, cccd_list: List[str], batch_size: int = 10, delay: float = 2.0) -> List[Dict]:
        """Batch check danh sách CCCD."""
        print(f"🚀 Bắt đầu batch check {len(cccd_list)} CCCD")
        print(f"   - Batch size: {batch_size}")
        print(f"   - Delay giữa batches: {delay}s")
        print("-" * 60)

        start_time = time.time()
        results = []

        for i in range(0, len(cccd_list), batch_size):
            batch = cccd_list[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(cccd_list) + batch_size - 1) // batch_size

            print(f"📦 Batch {batch_num}/{total_batches} - Xử lý {len(batch)} CCCD")

            batch_start = time.time()
            batch_results = []

            for j, cccd in enumerate(batch):
                print(f"   {j+1:2d}. Checking CCCD: {cccd}", end=" ... ")

                result = self.check_single_cccd(cccd)
                batch_results.append(result)

                # Update stats
                self.stats['total_processed'] += 1
                if result['status'] == 'success':
                    self.stats['successful_checks'] += 1
                    if result.get('api_status') == 'completed':
                        api_result = result.get('data', {})
                        if api_result.get('status') == 'found':
                            self.stats['found_matches'] += 1
                        elif api_result.get('status') == 'not_found':
                            self.stats['not_found'] += 1
                else:
                    self.stats['failed_checks'] += 1
                    self.stats['errors'] += 1

                print(f"{'✅' if result['status'] == 'success' else '❌'} "
                      f"({result['response_time']:.1f}s)")

            batch_time = time.time() - batch_start
            print(".1f")
            results.extend(batch_results)

            # Delay giữa batches (trừ batch cuối)
            if i + batch_size < len(cccd_list):
                print(f"⏳ Đợi {delay}s trước batch tiếp theo...")
                time.sleep(delay)

        total_time = time.time() - start_time
        self.stats['total_time'] = total_time

        print("\n" + "="*60)
        print("🎉 HOÀN THÀNH BATCH CHECK!")
        print("="*60)
        print(f"⏱️  Tổng thời gian: {total_time:.2f}s")
        print(f"📊 Tổng CCCD xử lý: {self.stats['total_processed']}")
        print(f"✅ Thành công: {self.stats['successful_checks']}")
        print(f"❌ Thất bại: {self.stats['failed_checks']}")
        print(f"🔍 Tìm thấy: {self.stats['found_matches']}")
        print(f"❓ Không tìm thấy: {self.stats['not_found']}")
        print(".1f")
        print(".1f")
        return results

    def create_comprehensive_report(self, results: List[Dict], output_file: str = None) -> str:
        """Tạo báo cáo tổng hợp chi tiết."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"batch_check_results_{timestamp}.xlsx"

        print(f"\n📊 Tạo báo cáo tổng hợp: {output_file}")

        # Chuẩn bị dữ liệu cho Excel
        excel_data = []

        for result in results:
            row = {
                'STT': len(excel_data) + 1,
                'CCCD': result['cccd'],
                'Trạng thái check': 'Thành công' if result['status'] == 'success' else 'Thất bại',
                'Thời gian response (s)': round(result['response_time'], 2),
                'API Status': result.get('api_status', 'N/A'),
                'Kết quả tìm kiếm': 'N/A',
                'Số matches': 0,
                'Tên': '',
                'Mã số thuế': '',
                'Địa chỉ': '',
                'Chức vụ': '',
                'URL': '',
                'Lỗi': result.get('error', '')
            }

            # Nếu thành công, extract thông tin chi tiết
            if result['status'] == 'success' and result.get('data'):
                data = result['data']
                row['Kết quả tìm kiếm'] = data.get('status', 'unknown')
                matches = data.get('matches', [])
                row['Số matches'] = len(matches)

                if matches:
                    match = matches[0]  # Lấy match đầu tiên
                    row['Tên'] = match.get('name', '')
                    row['Mã số thuế'] = match.get('tax_code', '')
                    row['Địa chỉ'] = match.get('address', '')
                    row['Chức vụ'] = match.get('role', '')
                    row['URL'] = match.get('url', '')

            excel_data.append(row)

        # Tạo DataFrame
        df = pd.DataFrame(excel_data)

        # Tạo file Excel với multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet chính
            df.to_excel(writer, sheet_name='Ket_Qua_Check', index=False)

            # Sheet thống kê
            stats_data = self._create_stats_sheet()
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Thong_Ke', index=False)

            # Sheet tóm tắt
            summary_data = self._create_summary_sheet(results)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Tom_Tat', index=False)

        print(f"✅ Báo cáo đã được tạo: {output_file}")
        return output_file

    def _create_stats_sheet(self) -> List[Dict]:
        """Tạo sheet thống kê."""
        stats = self.stats
        return [
            {'Chỉ số': 'Tổng CCCD xử lý', 'Giá trị': stats['total_processed']},
            {'Chỉ số': 'Thành công', 'Giá trị': stats['successful_checks']},
            {'Chỉ số': 'Thất bại', 'Giá trị': stats['failed_checks']},
            {'Chỉ số': 'Tìm thấy thông tin', 'Giá trị': stats['found_matches']},
            {'Chỉ số': 'Không tìm thấy', 'Giá trị': stats['not_found']},
            {'Chỉ số': 'Tỷ lệ thành công', 'Giá trị': f"{(stats['successful_checks'] / max(stats['total_processed'], 1) * 100):.1f}%"},
            {'Chỉ số': 'Tỷ lệ tìm thấy', 'Giá trị': f"{(stats['found_matches'] / max(stats['total_processed'], 1) * 100):.1f}%"},
            {'Chỉ số': 'Tổng thời gian (giây)', 'Giá trị': round(stats['total_time'], 2)},
            {'Chỉ số': 'Thời gian trung bình/CCCD (giây)', 'Giá trị': round(stats['total_time'] / max(stats['total_processed'], 1), 2)},
        ]

    def _create_summary_sheet(self, results: List[Dict]) -> List[Dict]:
        """Tạo sheet tóm tắt."""
        # Phân tích theo trạng thái
        status_counts = {}
        for result in results:
            status = result.get('api_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        summary = [
            {'Thông tin': 'Thời gian thực hiện', 'Giá trị': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'Thông tin': 'File nguồn', 'Giá trị': 'quang_ninh_female_1965_1975.xlsx'},
            {'Thông tin': 'API Endpoint', 'Giá trị': self.check_endpoint},
            {'Thông tin': 'Tổng số CCCD', 'Giá trị': len(results)},
        ]

        for status, count in status_counts.items():
            summary.append({
                'Thông tin': f'API Status: {status}',
                'Giá trị': f'{count} ({count/len(results)*100:.1f}%)'
            })

        return summary

def main():
    """Main function."""
    print("🚀 BATCH CHECK CCCD - Quảng Ninh Nữ (1965-1975)")
    print("=" * 60)

    # Khởi tạo checker
    checker = BatchCCCDChecker()

    # File Excel chứa 5000 CCCD
    excel_file = "quang_ninh_female_1965_1975.xlsx"

    # Kiểm tra file tồn tại
    if not os.path.exists(excel_file):
        print(f"❌ File Excel không tồn tại: {excel_file}")
        sys.exit(1)

    # Đọc danh sách CCCD
    cccd_list = checker.load_cccd_from_excel(excel_file)

    if not cccd_list:
        print("❌ Không có CCCD nào để check")
        sys.exit(1)

    # Batch check (giới hạn 100 CCCD đầu tiên để test)
    test_limit = min(100, len(cccd_list))  # Test với 100 CCCD đầu tiên
    print(f"🧪 Test với {test_limit} CCCD đầu tiên...")

    results = checker.batch_check_cccd(
        cccd_list[:test_limit],
        batch_size=5,  # 5 CCCD per batch
        delay=3.0      # 3 giây delay giữa batches
    )

    # Tạo báo cáo
    output_file = checker.create_comprehensive_report(results)

    print("\n" + "="*60)
    print("🎉 HOÀN THÀNH!")
    print("="*60)
    print(f"📁 File kết quả: {output_file}")
    print(f"📊 Đã check: {len(results)}/{len(cccd_list)} CCCD")
    print(f"✅ Thành công: {checker.stats['successful_checks']}")
    print(f"🔍 Tìm thấy: {checker.stats['found_matches']}")
    print(".1f")
    if len(cccd_list) > test_limit:
        print(f"\n💡 Để check toàn bộ {len(cccd_list)} CCCD, chạy với test_limit = {len(cccd_list)}")

if __name__ == "__main__":
    main()