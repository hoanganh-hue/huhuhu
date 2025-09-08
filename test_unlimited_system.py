#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Unlimited CCCD Processing System
Kiểm tra hệ thống với số lượng lớn CCCD để đảm bảo không còn giới hạn
"""

import os
import sys
import time
from pathlib import Path

# Thêm src vào Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_cccd_generation():
    """Test tạo CCCD không giới hạn."""
    print("🧪 Testing CCCD Generation (Unlimited)...")

    try:
        from src.modules.cccd.cccd_generator_enhanced import CCCDGeneratorEnhanced

        generator = CCCDGeneratorEnhanced()

        # Test tạo 5000 CCCD
        result = generator.generate_cccd_list_enhanced(
            province_codes=["001", "079"],  # Hà Nội và TP.HCM
            gender=None,  # Random
            birth_year_range=(1990, 2000),
            quantity=5000
        )

        if result["success"]:
            data = result["data"]
            print(f"✅ Generated {len(data)} CCCD successfully")
            print(f"   📊 Stats: {result['metadata']['kpis']}")

            # Kiểm tra không có giới hạn
            if len(data) == 5000:
                print("✅ No limit detected - all 5000 CCCD generated")
                return True
            else:
                print(f"❌ Limit detected - only {len(data)} CCCD generated")
                return False
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_data_aggregator():
    """Test Data Aggregator với số lượng lớn."""
    print("\n🧪 Testing Data Aggregator (Unlimited)...")

    try:
        from src.modules.core.data_aggregator import DataAggregator

        aggregator = DataAggregator()

        # Tạo danh sách CCCD test (1000 CCCD)
        test_cccds = [f"{i:012d}" for i in range(100000000000, 100000001000)]

        result = aggregator.aggregate_from_multiple_sources(test_cccds)

        if result["success"]:
            data = result["data"]
            print(f"✅ Aggregated {len(data)} records successfully")
            print(f"   📊 Stats: {result['metadata']['stats']}")

            # Kiểm tra không có giới hạn
            if len(data) == len(test_cccds):
                print("✅ No limit detected - all records aggregated")
                return True
            else:
                print(f"❌ Limit detected - only {len(data)} records aggregated")
                return False
        else:
            print(f"❌ Aggregation failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_excel_exporter():
    """Test Excel Exporter với số lượng lớn."""
    print("\n🧪 Testing Excel Exporter (Unlimited)...")

    try:
        import pandas as pd
        from src.modules.core.excel_exporter import ExcelExporter

        exporter = ExcelExporter()

        # Tạo dữ liệu test (2000 records)
        test_data = []
        for i in range(2000):
            test_data.append({
                "cccd": f"{100000000000 + i:012d}",
                "name": f"Test User {i}",
                "validation": {"status": "valid" if i % 2 == 0 else "invalid"},
                "sources": {
                    "check_cccd": {"status": "found" if i % 3 == 0 else "not_found"},
                    "doanh_nghiep": {"company_name": f"Company {i}" if i % 4 == 0 else ""}
                }
            })

        # Test export
        result_path = exporter.export_dict_to_excel(test_data, "test_unlimited.xlsx")

        if result_path and Path(result_path).exists():
            # Kiểm tra file
            stats = exporter.get_export_stats(result_path)
            validation = exporter.validate_excel_file(result_path)

            print(f"✅ Exported to: {result_path}")
            print(f"   📊 Stats: {stats}")
            print(f"   ✅ Validation: {validation['valid']}")

            if validation['valid'] and stats['sheets']['Data']['rows'] == 2000:
                print("✅ No limit detected - all 2000 records exported")
                return True
            else:
                print(f"❌ Limit detected - only {stats['sheets']['Data']['rows']} records exported")
                return False
        else:
            print("❌ Export failed")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_configuration():
    """Test cấu hình không giới hạn."""
    print("\n🧪 Testing Configuration (Unlimited)...")

    try:
        from src.config.settings import get_config

        config = get_config()

        # Kiểm tra các giá trị không giới hạn
        checks = [
            ("CCCD_COUNT", config.cccd_count, 0),
            ("MAX_CONCURRENT_PROCESSING", config.max_concurrent_processing, 0),
            ("RETRY_MAX_ATTEMPTS", config.retry_max_attempts, 0),
            ("REQUEST_TIMEOUT", config.request_timeout, 0),
        ]

        all_passed = True
        for name, actual, expected in checks:
            if actual == expected:
                print(f"✅ {name}: {actual} (unlimited)")
            else:
                print(f"❌ {name}: {actual} (expected {expected})")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Chạy tất cả các test."""
    print("🚀 Starting Unlimited System Tests")
    print("=" * 50)

    start_time = time.time()

    tests = [
        ("Configuration", test_configuration),
        ("CCCD Generation", test_cccd_generation),
        ("Data Aggregator", test_data_aggregator),
        ("Excel Exporter", test_excel_exporter),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Tổng kết
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n📈 Overall: {passed}/{total} tests passed")

    end_time = time.time()
    duration = end_time - start_time

    print(f"⏱️ Total execution time: {duration:.2f} seconds")
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Unlimited system is working correctly.")
        print("✅ No limits detected in the system.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)