#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra scraper đã sửa
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'check-cccd', 'src'))

from check_cccd.scraper_fixed import scrape_cccd_sync
import json

def test_fixed_scraper():
    """Test scraper đã sửa với một vài CCCD"""

    test_cccds = [
        "022168081341",  # CCCD từ file gốc
        "022173062322",  # CCCD khác
        "022171092374"   # CCCD khác
    ]

    print("🧪 TESTING FIXED SCRAPER")
    print("=" * 50)

    for i, cccd in enumerate(test_cccds, 1):
        print(f"\n📋 Test {i}/{len(test_cccds)}: CCCD {cccd}")
        print("-" * 30)

        try:
            result = scrape_cccd_sync(cccd)

            print(f"Status: {result.get('status')}")
            print(f"Matches found: {len(result.get('matches', []))}")

            if result.get('matches'):
                for j, match in enumerate(result['matches'], 1):
                    print(f"  Match {j}:")
                    print(f"    Name: {match.get('name', 'N/A')}")
                    print(f"    Tax Code: {match.get('tax_code', 'N/A')}")
                    print(f"    URL: {match.get('url', 'N/A')}")
                    print(f"    Address: {match.get('address', 'N/A')}")
                    print(f"    Role: {match.get('role', 'N/A')}")
            else:
                print("  No matches found")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_fixed_scraper()