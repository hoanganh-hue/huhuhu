#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script debug để kiểm tra vấn đề scraper trả về dữ liệu giống nhau
"""

import httpx
from bs4 import BeautifulSoup
import re
import json

def debug_masothue_scraping():
    """Debug scraping để tìm hiểu tại sao tất cả dữ liệu giống nhau"""

    test_cccd = "022168081341"

    print("🔍 DEBUGGING MASOTHUE.COM SCRAPING")
    print("=" * 60)
    print(f"Test CCCD: {test_cccd}")
    print()

    try:
        # Step 1: Direct search request
        search_url = f"https://masothue.com/Search/?q={test_cccd}&type=auto"
        print(f"🌐 Requesting: {search_url}")

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(search_url)
            response.raise_for_status()

        print(f"✅ Response status: {response.status_code}")
        print(f"📏 Response length: {len(response.text)} characters")
        print()

        # Step 2: Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')

        # Step 3: Debug HTML structure
        print("🔍 HTML STRUCTURE ANALYSIS")
        print("-" * 40)

        # Check for common elements
        title = soup.find('title')
        print(f"Page title: {title.text if title else 'No title found'}")

        # Look for any links
        all_links = soup.find_all('a', href=True)
        print(f"Total links found: {len(all_links)}")

        # Show first few links
        print("First 5 links:")
        for i, link in enumerate(all_links[:5]):
            href = link.get('href')
            text = link.get_text(strip=True)[:50]
            print(f"  {i+1}. {href} -> '{text}'")

        print()

        # Step 4: Look for specific patterns
        print("🔍 PATTERN ANALYSIS")
        print("-" * 40)

        # Check for Zalo links
        zalo_links = soup.find_all('a', href=re.compile(r'zalo\.me'))
        print(f"Zalo links found: {len(zalo_links)}")
        for link in zalo_links[:3]:
            print(f"  Zalo: {link.get('href')} -> '{link.get_text(strip=True)}'")

        # Check for any numbers that might be tax codes
        text_content = soup.get_text()
        tax_code_candidates = re.findall(r'\d{10,13}', text_content)
        print(f"Tax code candidates found: {len(tax_code_candidates)}")
        print(f"Unique tax codes: {len(set(tax_code_candidates))}")
        print(f"Sample tax codes: {list(set(tax_code_candidates))[:5]}")

        # Step 5: Check for specific keywords
        print()
        print("🔍 KEYWORD ANALYSIS")
        print("-" * 40)

        keywords = ['Tra cứu', 'mã số thuế', 'doanh nghiệp', 'MST', 'tax']
        for keyword in keywords:
            count = text_content.lower().count(keyword.lower())
            print(f"'{keyword}' appears: {count} times")

        # Step 6: Check for JSON data in page
        print()
        print("🔍 JSON DATA ANALYSIS")
        print("-" * 40)

        # Look for script tags that might contain JSON
        scripts = soup.find_all('script')
        json_found = False
        for script in scripts:
            if script.string:
                # Look for JSON-like content
                if '{' in script.string and '}' in script.string:
                    print("Found potential JSON in script tag:")
                    # Extract first 200 chars for preview
                    json_preview = script.string.strip()[:200]
                    print(f"  {json_preview}...")
                    json_found = True
                    break

        if not json_found:
            print("No JSON data found in script tags")

        # Step 7: Save raw HTML for manual inspection
        print()
        print("💾 SAVING RAW HTML")
        print("-" * 40)

        with open('debug_masothue_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        print("✅ Raw HTML saved to: debug_masothue_response.html")
        print("📏 File size:", len(response.text), "characters")

        # Step 8: Summary
        print()
        print("📊 SUMMARY")
        print("-" * 40)
        print("✅ Request successful")
        print(f"📏 HTML size: {len(response.text)} chars")
        print(f"🔗 Links found: {len(all_links)}")
        print(f"📱 Zalo links: {len(zalo_links)}")
        print(f"🔢 Tax code candidates: {len(set(tax_code_candidates))}")

        if len(set(tax_code_candidates)) == 1:
            print("⚠️  WARNING: All tax codes are identical!")
            print(f"   Tax code: {list(set(tax_code_candidates))[0]}")
        elif len(set(tax_code_candidates)) == 0:
            print("❌ ERROR: No tax codes found!")
        else:
            print("✅ Found multiple unique tax codes")

    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_masothue_scraping()