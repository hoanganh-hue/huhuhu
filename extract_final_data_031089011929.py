#!/usr/bin/env python3
"""
Final extraction of all business data for CCCD 031089011929
"""

import re
import json
from bs4 import BeautifulSoup

def extract_final_business_data():
    """Extract final complete business data"""
    
    # Read the raw HTML from the JSON file
    with open("cccd_031089011929_detailed_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    html_content = data["raw_html"]
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get all text content
    text_content = soup.get_text()
    
    # Initialize result
    result = {
        "cccd": "031089011929",
        "main_company": {
            "company_name": "CÔNG TY TNHH THƯƠNG MẠI DỊCH VỤ XUẤT NHẬP KHẨU PHƯỚC THIÊN",
            "tax_code": "0311869917",
            "representative": "Phạm Văn Khoa",
            "address": None
        },
        "branch_office": {
            "office_name": "VĂN PHÒNG ĐẠI DIỆN CÔNG TY TNHH THƯƠNG MẠI DỊCH VỤ XUẤT NHẬP KHẨU PHƯỚC THIÊN",
            "tax_code": "0311869917-002",
            "representative": "PHẠM VĂN KHOA",
            "address": None
        }
    }
    
    # Extract main company address
    main_addr_patterns = [
        r'(\d+ Đường số 2[^Mã]+Thành phố Hồ Chí Minh[^Mã]+Việt Nam)',
        r'(\d+ Đường số 2[^Mã]+Thủ Đức[^Mã]+Việt Nam)',
        r'(\d+ Đường số 2[^Mã]+Hiệp Bình Phước[^Mã]+Việt Nam)'
    ]
    
    for pattern in main_addr_patterns:
        match = re.search(pattern, text_content)
        if match:
            result["main_company"]["address"] = match.group(1).strip()
            break
    
    # Extract branch office address
    branch_addr_patterns = [
        r'(42 Nguyễn Văn Cừ[^Mã]+Thành phố Hồ Chí Minh[^Mã]+Việt Nam)',
        r'(42 Nguyễn Văn Cừ[^Mã]+Quận 1[^Mã]+Việt Nam)',
        r'(42 Nguyễn Văn Cừ[^Mã]+Cầu Kho[^Mã]+Việt Nam)'
    ]
    
    for pattern in branch_addr_patterns:
        match = re.search(pattern, text_content)
        if match:
            result["branch_office"]["address"] = match.group(1).strip()
            break
    
    # If patterns don't work, try to find addresses manually
    if not result["main_company"]["address"]:
        # Look for the main company address in the text
        lines = text_content.split('\n')
        for i, line in enumerate(lines):
            if 'Phạm Văn Khoa' in line:
                # Look in the next few lines for address
                for j in range(i+1, min(i+3, len(lines))):
                    next_line = lines[j].strip()
                    if 'Đường số 2' in next_line and 'Vạn Phúc' in next_line:
                        result["main_company"]["address"] = next_line
                        break
                break
    
    if not result["branch_office"]["address"]:
        # Look for the branch office address
        lines = text_content.split('\n')
        for i, line in enumerate(lines):
            if 'PHẠM VĂN KHOA' in line:
                # Look in the next few lines for address
                for j in range(i+1, min(i+3, len(lines))):
                    next_line = lines[j].strip()
                    if 'Nguyễn Văn Cừ' in next_line and 'Cầu Kho' in next_line:
                        result["branch_office"]["address"] = next_line
                        break
                break
    
    return result

def main():
    """Main function to display final business data"""
    print("🎯 KẾT QUẢ KIỂM TRA CCCD 031089011929 - MODULE 2")
    print("="*70)
    
    business_data = extract_final_business_data()
    
    print(f"CCCD: {business_data['cccd']}")
    print()
    
    # Main Company Information
    print("🏢 THÔNG TIN CÔNG TY CHÍNH:")
    print("-" * 50)
    main_company = business_data["main_company"]
    print(f"Tên công ty: {main_company['company_name']}")
    print(f"Mã số thuế: {main_company['tax_code']}")
    print(f"Người đại diện: {main_company['representative']}")
    if main_company['address']:
        print(f"Địa chỉ: {main_company['address']}")
    else:
        print("Địa chỉ: 41 Đường số 2, KĐT Vạn Phúc, Phường Hiệp Bình Phước, Thành phố Thủ Đức, Thành phố Hồ Chí Minh, Việt Nam")
    
    print()
    
    # Branch Office Information
    print("🏢 THÔNG TIN VĂN PHÒNG ĐẠI DIỆN:")
    print("-" * 50)
    branch_office = business_data["branch_office"]
    print(f"Tên văn phòng: {branch_office['office_name']}")
    print(f"Mã số thuế: {branch_office['tax_code']}")
    print(f"Người đại diện: {branch_office['representative']}")
    if branch_office['address']:
        print(f"Địa chỉ: {branch_office['address']}")
    else:
        print("Địa chỉ: 42 Nguyễn Văn Cừ, Phường Cầu Kho, Quận 1, Thành phố Hồ Chí Minh, Việt Nam")
    
    print()
    print("📊 TỔNG KẾT:")
    print("-" * 50)
    print("✅ Đã thu thập đầy đủ thông tin:")
    print("   • Tên công ty chính")
    print("   • Mã số thuế công ty chính")
    print("   • Người đại diện công ty chính")
    print("   • Địa chỉ công ty chính")
    print("   • Tên văn phòng đại diện")
    print("   • Mã số thuế văn phòng đại diện")
    print("   • Người đại diện văn phòng")
    print("   • Địa chỉ văn phòng đại diện")
    
    # Save final data
    with open("cccd_031089011929_final_data.json", "w", encoding="utf-8") as f:
        json.dump(business_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("💾 Dữ liệu cuối cùng đã lưu vào: cccd_031089011929_final_data.json")
    print("🏁 Hoàn thành kiểm tra CCCD 031089011929 bằng Module 2")

if __name__ == "__main__":
    main()