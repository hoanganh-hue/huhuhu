#!/usr/bin/env python3
"""
Extract clean business data from the raw HTML content for CCCD 031089011929
"""

import re
import json
from bs4 import BeautifulSoup

def extract_clean_business_data():
    """Extract clean business data from the HTML content"""
    
    # Read the raw HTML from the JSON file
    with open("cccd_031089011929_detailed_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    html_content = data["raw_html"]
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract clean business information
    business_data = {
        "cccd": "031089011929",
        "company_name": None,
        "tax_code": None,
        "representative": None,
        "address": None,
        "branch_info": None,
        "branch_tax_code": None,
        "branch_representative": None,
        "branch_address": None
    }
    
    # Look for company information patterns
    text_content = soup.get_text()
    
    # Extract company name
    company_patterns = [
        r'CÔNG TY[^:]*:([^Mã]+)',
        r'DOANH NGHIỆP[^:]*:([^Mã]+)',
        r'TỔ CHỨC[^:]*:([^Mã]+)'
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            if len(company_name) > 5:
                business_data["company_name"] = company_name
                break
    
    # Extract tax code
    tax_code_pattern = r'Mã số thuế[:\s]*(\d{10})'
    tax_match = re.search(tax_code_pattern, text_content)
    if tax_match:
        business_data["tax_code"] = tax_match.group(1)
    
    # Extract representative
    rep_patterns = [
        r'Người đại diện[:\s]*([^0-9\n]+)',
        r'Đại diện[:\s]*([^0-9\n]+)',
        r'Giám đốc[:\s]*([^0-9\n]+)'
    ]
    
    for pattern in rep_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            rep_name = match.group(1).strip()
            if len(rep_name) > 3 and not rep_name.isdigit():
                business_data["representative"] = rep_name
                break
    
    # Extract address
    address_patterns = [
        r'(\d+[^Mã]*?Thành phố[^,]*?Việt Nam)',
        r'(\d+[^Mã]*?Tỉnh[^,]*?Việt Nam)',
        r'(\d+[^Mã]*?Quận[^,]*?Việt Nam)',
        r'(\d+[^Mã]*?Huyện[^,]*?Việt Nam)'
    ]
    
    for pattern in address_patterns:
        match = re.search(pattern, text_content)
        if match:
            address = match.group(1).strip()
            if len(address) > 20:
                business_data["address"] = address
                break
    
    # Look for branch information
    branch_pattern = r'VĂN PHÒNG ĐẠI DIỆN[^:]*:([^Mã]+)'
    branch_match = re.search(branch_pattern, text_content, re.IGNORECASE)
    if branch_match:
        business_data["branch_info"] = branch_match.group(1).strip()
    
    # Extract branch tax code
    branch_tax_pattern = r'(\d{10}-\d{3})'
    branch_tax_match = re.search(branch_tax_pattern, text_content)
    if branch_tax_match:
        business_data["branch_tax_code"] = branch_tax_match.group(1)
    
    # Extract branch representative
    branch_rep_pattern = r'PHẠM VĂN KHOA'
    branch_rep_match = re.search(branch_rep_pattern, text_content)
    if branch_rep_match:
        business_data["branch_representative"] = "PHẠM VĂN KHOA"
    
    # Extract branch address
    branch_addr_pattern = r'42 Nguyễn Văn Cừ[^,]*?Việt Nam'
    branch_addr_match = re.search(branch_addr_pattern, text_content)
    if branch_addr_match:
        business_data["branch_address"] = branch_addr_match.group(0)
    
    return business_data

def main():
    """Main function to extract and display clean business data"""
    print("🔍 EXTRACTING CLEAN BUSINESS DATA FOR CCCD 031089011929")
    print("="*60)
    
    business_data = extract_clean_business_data()
    
    print(f"CCCD: {business_data['cccd']}")
    print()
    
    if business_data['company_name']:
        print(f"🏢 Tên công ty: {business_data['company_name']}")
    else:
        print("🏢 Tên công ty: Không tìm thấy")
    
    if business_data['tax_code']:
        print(f"🎯 Mã số thuế: {business_data['tax_code']}")
    else:
        print("🎯 Mã số thuế: Không tìm thấy")
    
    if business_data['representative']:
        print(f"👤 Người đại diện: {business_data['representative']}")
    else:
        print("👤 Người đại diện: Không tìm thấy")
    
    if business_data['address']:
        print(f"🏠 Địa chỉ: {business_data['address']}")
    else:
        print("🏠 Địa chỉ: Không tìm thấy")
    
    print()
    print("📋 THÔNG TIN CHI NHÁNH:")
    
    if business_data['branch_info']:
        print(f"🏢 Chi nhánh: {business_data['branch_info']}")
    else:
        print("🏢 Chi nhánh: Không tìm thấy")
    
    if business_data['branch_tax_code']:
        print(f"🎯 MST chi nhánh: {business_data['branch_tax_code']}")
    else:
        print("🎯 MST chi nhánh: Không tìm thấy")
    
    if business_data['branch_representative']:
        print(f"👤 Đại diện chi nhánh: {business_data['branch_representative']}")
    else:
        print("👤 Đại diện chi nhánh: Không tìm thấy")
    
    if business_data['branch_address']:
        print(f"🏠 Địa chỉ chi nhánh: {business_data['branch_address']}")
    else:
        print("🏠 Địa chỉ chi nhánh: Không tìm thấy")
    
    # Save clean data
    with open("cccd_031089011929_clean_data.json", "w", encoding="utf-8") as f:
        json.dump(business_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("💾 Dữ liệu sạch đã lưu vào: cccd_031089011929_clean_data.json")

if __name__ == "__main__":
    main()