import asyncio
from collections import Counter
import sys
import os

# Thêm các đường dẫn cần thiết vào Python path một cách chính xác
sys.path.insert(0, os.path.abspath('/Users/nguyenduchung1993/Downloads/tools-data-bhxh/bhxh-tool-enhanced-python'))
sys.path.insert(0, os.path.abspath('/Users/nguyenduchung1993/Downloads/tools-data-bhxh'))

from services.excel_service import ExcelService
from cccd.cccd_analyzer_service import CCCDAnalyzerService

async def analyze_cccd_in_excel(file_path):
    """
    Quét file Excel, phân tích cột CCCD và in ra thống kê chi tiết.
    """
    print(f"--- Bắt đầu phân tích file: {file_path} ---")
    
    excel_service = ExcelService()
    analyzer = CCCDAnalyzerService()
    
    try:
        excel_data = await excel_service.read_excel_file(file_path)
        if not excel_data:
            print("Không đọc được dữ liệu từ file Excel hoặc file rỗng.")
            return

        first_sheet_name = next(iter(excel_data))
        sheet_data = excel_data[first_sheet_name]['data']
        total_rows = len(sheet_data)
        print(f"Đã đọc {total_rows} dòng từ sheet: '{first_sheet_name}'.")

        valid_count = 0
        invalid_count = 0
        province_dist = Counter()
        gender_dist = Counter()
        year_dist = Counter()
        month_dist = Counter()

        for i, row in enumerate(sheet_data):
            cccd = row.get('soCCCD', '')
            if not cccd:
                continue

            analysis = analyzer.analyzeCccdStructure(cccd, detailed=False, location=False)
            
            if analysis.get('valid'):
                valid_count += 1
                structure = analysis['structure']
                province_dist[structure['province']['name']] += 1
                gender_dist[structure['genderCentury']['gender']] += 1
                year_dist[structure['birthDate']['fullYear']] += 1
                month_dist[structure['birthDate']['month']] += 1
            else:
                invalid_count += 1
            
            if (i + 1) % 100 == 0 or (i + 1) == total_rows:
                print(f"Đã xử lý {i + 1}/{total_rows} dòng...", end='\r')

        print("\n--- Hoàn thành phân tích ---")

        print("\n📊 KẾT QUẢ PHÂN TÍCH DỮ LIỆU CCCD 📊")
        print("="*40)
        print(f"Tổng số CCCD đã xử lý: {valid_count + invalid_count}")
        print(f"✅ Hợp lệ: {valid_count}")
        print(f"❌ Không hợp lệ: {invalid_count}")
        validity_rate = (valid_count / (valid_count + invalid_count) * 100) if (valid_count + invalid_count) > 0 else 0
        print(f"=> Tỷ lệ hợp lệ: {validity_rate:.2f}%\n")

        print("--- Phân bổ theo Năm sinh ---")
        for year, count in year_dist.most_common():
            print(f"- {year}: {count} người")

        print("\n--- Phân bổ theo Tháng sinh ---")
        for month in sorted(month_dist.keys()):
            print(f"- Tháng {month}: {month_dist[month]} người")

        print("\n--- Phân bổ theo Giới tính ---")
        for gender, count in gender_dist.items():
            print(f"- {gender}: {count} người")

        print("\n--- Phân bổ theo Tỉnh thành ---")
        for province, count in province_dist.most_common():
            print(f"- {province}: {count} người")
        print("="*40)

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn '{file_path}'.")
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn: {e}")

if __name__ == "__main__":
    file_to_analyze = '/Users/nguyenduchung1993/Downloads/tools-data-bhxh/data-bhxh-21-6.xlsx'
    asyncio.run(analyze_cccd_in_excel(file_to_analyze))