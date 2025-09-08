#!/usr/bin/env python3
"""
Extract complete business data from HTML content for CCCD 031089011929
"""

import re
import json
from bs4 import BeautifulSoup

def extract_complete_business_data():
    """Extract complete business data from the HTML content"""
    
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
        "main_company": {},
        "branch_office": {},
        "raw_text_sections": []
    }
    
    # Split text into sections and look for business information
    sections = text_content.split('\n')
    
    # Look for the main company section
    main_company_found = False
    branch_office_found = False
    
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
            
        # Look for main company information
        if 'CÔNG TY TNHH' in section and not main_company_found:
            main_company_found = True
            result["main_company"]["company_name"] = section
            
            # Look for tax code in next few sections
            for j in range(i+1, min(i+5, len(sections))):
                next_section = sections[j].strip()
                if 'Mã số thuế:' in next_section:
                    tax_match = re.search(r'(\d{10})', next_section)
                    if tax_match:
                        result["main_company"]["tax_code"] = tax_match.group(1)
                elif 'Người đại diện:' in next_section:
                    rep_name = next_section.replace('Người đại diện:', '').strip()
                    if rep_name:
                        result["main_company"]["representative"] = rep_name
                elif re.search(r'\d+.*Đường.*Phường.*Thành phố', next_section):
                    result["main_company"]["address"] = next_section
        
        # Look for branch office information
        elif 'VĂN PHÒNG ĐẠI DIỆN' in section and not branch_office_found:
            branch_office_found = True
            result["branch_office"]["office_name"] = section
            
            # Look for branch information in next few sections
            for j in range(i+1, min(i+5, len(sections))):
                next_section = sections[j].strip()
                if 'Mã số thuế:' in next_section:
                    tax_match = re.search(r'(\d{10}-\d{3})', next_section)
                    if tax_match:
                        result["branch_office"]["tax_code"] = tax_match.group(1)
                elif 'Người đại diện:' in next_section:
                    rep_name = next_section.replace('Người đại diện:', '').strip()
                    if rep_name:
                        result["branch_office"]["representative"] = rep_name
                elif re.search(r'\d+.*Nguyễn.*Phường.*Quận.*Thành phố', next_section):
                    result["branch_office"]["address"] = next_section
    
    # Alternative method: Look for specific patterns in the full text
    if not result["main_company"].get("company_name"):
        company_match = re.search(r'(CÔNG TY TNHH[^Mã]+)', text_content)
        if company_match:
            result["main_company"]["company_name"] = company_match.group(1).strip()
    
    if not result["main_company"].get("tax_code"):
        tax_match = re.search(r'Mã số thuế:\s*(\d{10})', text_content)
        if tax_match:
            result["main_company"]["tax_code"] = tax_match.group(1)
    
    if not result["main_company"].get("representative"):
        rep_match = re.search(r'Người đại diện:\s*([^0-9\n]+)', text_content)
        if rep_match:
            result["main_company"]["representative"] = rep_match.group(1).strip()
    
    if not result["main_company"].get("address"):
        addr_match = re.search(r'(\d+ Đường số 2[^Mã]+Việt Nam)', text_content)
        if addr_match:
            result["main_company"]["address"] = addr_match.group(1).strip()
    
    # Branch office information
    if not result["branch_office"].get("office_name"):
        branch_match = re.search(r'(VĂN PHÒNG ĐẠI DIỆN[^Mã]+)', text_content)
        if branch_match:
            result["branch_office"]["office_name"] = branch_match.group(1).strip()
    
    if not result["branch_office"].get("tax_code"):
        branch_tax_match = re.search(r'(\d{10}-\d{3})', text_content)
        if branch_tax_match:
            result["branch_office"]["tax_code"] = branch_tax_match.group(1)
    
    if not result["branch_office"].get("representative"):
        branch_rep_match = re.search(r'PHẠM VĂN KHOA', text_content)
        if branch_rep_match:
            result["branch_office"]["representative"] = "PHẠM VĂN KHOA"
    
    if not result["branch_office"].get("address"):
        branch_addr_match = re.search(r'(42 Nguyễn Văn Cừ[^,]+Việt Nam)', text_content)
        if branch_addr_match:
            result["branch_office"]["address"] = branch_addr_match.group(1).strip()
    
    return result

def main():
    """Main function to extract and display complete business data"""
    print("🔍 EXTRACTING COMPLETE BUSINESS DATA FOR CCCD 031089011929")
    print("="*70)
    
    business_data = extract_complete_business_data()
    
    print(f"CCCD: {business_data['cccd']}")
    print()
    
    # Main Company Information
    print("🏢 THÔNG TIN CÔNG TY CHÍNH:")
    print("-" * 40)
    
    main_company = business_data["main_company"]
    if main_company.get("company_name"):
        print(f"Tên công ty: {main_company['company_name']}")
    else:
        print("Tên công ty: Không tìm thấy")
    
    if main_company.get("tax_code"):
        print(f"Mã số thuế: {main_company['tax_code']}")
    else:
        print("Mã số thuế: Không tìm thấy")
    
    if main_company.get("representative"):
        print(f"Người đại diện: {main_company['representative']}")
    else:
        print("Người đại diện: Không tìm thấy")
    
    if main_company.get("address"):
        print(f"Địa chỉ: {main_company['address']}")
    else:
        print("Địa chỉ: Không tìm thấy")
    
    print()
    
    # Branch Office Information
    print("🏢 THÔNG TIN VĂN PHÒNG ĐẠI DIỆN:")
    print("-" * 40)
    
    branch_office = business_data["branch_office"]
    if branch_office.get("office_name"):
        print(f"Tên văn phòng: {branch_office['office_name']}")
    else:
        print("Tên văn phòng: Không tìm thấy")
    
    if branch_office.get("tax_code"):
        print(f"Mã số thuế: {branch_office['tax_code']}")
    else:
        print("Mã số thuế: Không tìm thấy")
    
    if branch_office.get("representative"):
        print(f"Người đại diện: {branch_office['representative']}")
    else:
        print("Người đại diện: Không tìm thấy")
    
    if branch_office.get("address"):
        print(f"Địa chỉ: {branch_office['address']}")
    else:
        print("Địa chỉ: Không tìm thấy")
    
    # Save complete data
    with open("cccd_031089011929_complete_data.json", "w", encoding="utf-8") as f:
        json.dump(business_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("💾 Dữ liệu hoàn chỉnh đã lưu vào: cccd_031089011929_complete_data.json")

if __name__ == "__main__":
    main()