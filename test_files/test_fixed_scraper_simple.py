#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script đơn giản để kiểm tra scraper đã sửa
"""

import httpx
from bs4 import BeautifulSoup
import re

def test_simple_scraping():
    """Test scraping đơn giản để kiểm tra logic"""

    test_cccd = "022168081341"

    print("🧪 SIMPLE SCRAPING TEST")
    print("=" * 50)
    print(f"Test CCCD: {test_cccd}")
    print()

    try:
        # Direct search request
        search_url = f"https://masothue.com/Search/?q={test_cccd}&type=auto"
        print(f"🌐 Requesting: {search_url}")

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(search_url)
            response.raise_for_status()

        print(f"✅ Response status: {response.status_code}")

        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')

        # Test new logic: exclude navigation and ad links
        print("\n🔍 TESTING NEW LOGIC")
        print("-" * 30)

        all_links = soup.find_all('a', href=True)
        print(f"Total links found: {len(all_links)}")

        # Filter out navigation and ad links
        valid_links = []
        for link in all_links:
            href = link.get('href')
            if not href:
                continue

            # Skip navigation and ad links
            if (href == '#' or
                href.startswith('#') or
                href == '/' or
                '/tra-cuu-ma-so-thue' in href or
                '/Search' in href or
                'zalo.me' in href or
                'facebook.com' in href):
                continue

            # Check if it's a real company profile link
            if re.search(r'/\d{10,}', href):
                valid_links.append((href, link.get_text(strip=True)))

        print(f"Valid company links found: {len(valid_links)}")

        if valid_links:
            print("✅ Found valid company links:")
            for href, text in valid_links[:3]:  # Show first 3
                print(f"  - {href} -> '{text}'")
        else:
            print("❌ No valid company links found")
            print("   This confirms the issue: CCCD has no company data on masothue.com")

        # Check for any actual company data
        print("\n🔍 CHECKING FOR COMPANY DATA")
        print("-" * 30)

        # Look for company names, addresses, etc.
        text_content = soup.get_text()

        company_indicators = [
            'Tên công ty',
            'Địa chỉ',
            'Mã số thuế',
            'Người đại diện',
            'Giám đốc'
        ]

        found_indicators = []
        for indicator in company_indicators:
            if indicator.lower() in text_content.lower():
                found_indicators.append(indicator)

        if found_indicators:
            print(f"✅ Found company indicators: {found_indicators}")
        else:
            print("❌ No company data indicators found")
            print("   This confirms: The CCCD has NO company information on masothue.com")

        print("\n📊 CONCLUSION")
        print("-" * 30)
        if len(valid_links) == 0 and not found_indicators:
            print("✅ CORRECT: Scraper should return 'not_found' for this CCCD")
            print("   The CCCD has no company data on masothue.com")
        else:
            print("⚠️  UNEXPECTED: Found some data - needs further investigation")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_scraping()