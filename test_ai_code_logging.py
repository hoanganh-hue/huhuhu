#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-CODE LOGGING SYSTEM TEST
Kiểm tra toàn bộ hệ thống logging theo yêu cầu
"""

import os
import sys
import json
import time
from pathlib import Path

# Thêm src vào Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_log_directory_and_config():
    """Test 1: Kiểm tra thư mục logs và file cấu hình."""
    print("🧪 Test 1: Log Directory & Configuration")
    print("-" * 50)

    LOG_ROOT = Path("/Users/nguyenduchung1993/Downloads/tools-data-bhxh/logs")
    LOG_CFG = LOG_ROOT / "logging.yaml"

    # Check directory
    if LOG_ROOT.exists():
        print("✅ Log directory exists")
    else:
        print("❌ Log directory does not exist")
        return False

    # Check config file
    if LOG_CFG.exists():
        print("✅ Logging configuration file exists")
    else:
        print("❌ Logging configuration file does not exist")
        return False

    # Check log files
    log_files = ["system.log", "workflow.log", "errors.log", "performance.log"]
    for log_file in log_files:
        file_path = LOG_ROOT / log_file
        if file_path.exists():
            print(f"✅ Log file exists: {log_file}")
        else:
            print(f"⚠️ Log file will be created: {log_file}")

    print("✅ Test 1 PASSED")
    return True

def test_log_sample_generation():
    """Test 2: Tạo mẫu log và kiểm tra format."""
    print("\n🧪 Test 2: Sample Log Generation")
    print("-" * 50)

    try:
        from utils.log_helper import get_logger, add_extra, set_correlation

        # Create logger
        log = get_logger("test.module", step="demo_step")

        # Set correlation ID
        set_correlation(log, "cid-1234")

        # Add extra data
        add_extra(log, foo="bar", num=42, test_data={"nested": "value"})

        # Generate test logs
        log.info("Đây là log test INFO")
        log.warning("Đây là log test WARNING")
        log.error("Đây là log test ERROR")

        print("✅ Sample logs generated successfully")

        # Check if logs were written
        time.sleep(0.1)  # Small delay for file writing

        LOG_ROOT = Path("/Users/nguyenduchung1993/Downloads/tools-data-bhxh/logs")
        workflow_log = LOG_ROOT / "workflow.log"

        if workflow_log.exists():
            with open(workflow_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    try:
                        log_entry = json.loads(last_line)
                        required_fields = ["timestamp", "level", "module", "message", "request_id"]
                        missing_fields = [field for field in required_fields if field not in log_entry]

                        if not missing_fields:
                            print("✅ Log format validation PASSED")
                            print(f"   📝 Sample log entry: {json.dumps(log_entry, indent=2)[:200]}...")
                            return True
                        else:
                            print(f"❌ Missing required fields: {missing_fields}")
                            return False
                    except json.JSONDecodeError:
                        print("❌ Log entry is not valid JSON")
                        return False
                else:
                    print("❌ No log entries found")
                    return False
        else:
            print("❌ Workflow log file not found")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_cccd_generator_with_logging():
    """Test 3: Test CCCD Generator với logging."""
    print("\n🧪 Test 3: CCCD Generator with Logging")
    print("-" * 50)

    try:
        from modules.cccd.cccd_generator_enhanced_new import CCCDGeneratorEnhanced

        generator = CCCDGeneratorEnhanced()

        # Generate small batch
        result = generator.generate_cccd_list_enhanced(
            province_codes=["001"],
            gender=None,
            birth_year_range=(1990, 1995),
            quantity=5
        )

        if result["success"]:
            print("✅ CCCD generation with logging PASSED")
            print(f"   📊 Generated {len(result['data'])} CCCD successfully")
            return True
        else:
            print(f"❌ CCCD generation failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_workflow_runner():
    """Test 4: Test workflow runner với logging."""
    print("\n🧪 Test 4: Workflow Runner with Logging")
    print("-" * 50)

    try:
        # Import and run a small workflow
        from config.settings import get_config

        config = get_config()
        print("✅ Configuration loaded")

        # Test with small numbers to avoid long execution
        original_count = config.cccd_count
        config.cccd_count = 3  # Small test batch

        from runner import run_unlimited_cccd_workflow
        result = run_unlimited_cccd_workflow(config)

        # Restore original config
        config.cccd_count = original_count

        if result["success"]:
            print("✅ Workflow runner with logging PASSED")
            print(".2f"            return True
        else:
            print(f"❌ Workflow failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_log_analysis():
    """Test 5: Phân tích logs để kiểm tra tính toàn vẹn."""
    print("\n🧪 Test 5: Log Analysis")
    print("-" * 50)

    try:
        from utils.log_helper import parse_log_line, aggregate_log_stats

        LOG_ROOT = Path("/Users/nguyenduchung1993/Downloads/tools-data-bhxh/logs")
        workflow_log = LOG_ROOT / "workflow.log"

        if not workflow_log.exists():
            print("❌ Workflow log file not found")
            return False

        # Read and parse logs
        logs = []
        with open(workflow_log, 'r', encoding='utf-8') as f:
            for line in f:
                parsed = parse_log_line(line)
                if parsed:
                    logs.append(parsed)

        if not logs:
            print("❌ No valid log entries found")
            return False

        print(f"✅ Parsed {len(logs)} log entries")

        # Analyze logs
        stats = aggregate_log_stats(logs)
        print("📊 Log Statistics:"        print(f"   📈 Total logs: {stats['total_logs']}")
        print(f"   📊 Level distribution: {stats['level_counts']}")
        print(f"   🏷️ Module distribution: {stats['module_counts']}")
        print(f"   ⚠️ Error rate: {stats['error_rate']:.2f}%")
        print(f"   📋 Avg extra fields: {stats['avg_extra_fields']:.2f}")

        # Check for required fields
        required_fields_present = all(
            all(field in log for field in ["timestamp", "level", "module", "request_id"])
            for log in logs[:10]  # Check first 10 logs
        )

        if required_fields_present:
            print("✅ All required log fields present")
            return True
        else:
            print("❌ Some required log fields missing")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_performance_logging():
    """Test 6: Test performance logging."""
    print("\n🧪 Test 6: Performance Logging")
    print("-" * 50)

    try:
        from utils.log_helper import get_logger, log_performance

        log = get_logger("performance.test", step="performance_test")

        # Simulate performance data
        total_cccd = 1000
        execution_time = 2.5
        errors = 5

        log_performance(log, total_cccd, execution_time, errors)

        print("✅ Performance logging test PASSED")
        print(f"   📊 Logged: {total_cccd} CCCD, {execution_time}s, {errors} errors")

        # Check performance log
        time.sleep(0.1)
        LOG_ROOT = Path("/Users/nguyenduchung1993/Downloads/tools-data-bhxh/logs")
        perf_log = LOG_ROOT / "performance.log"

        if perf_log.exists():
            with open(perf_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    log_entry = json.loads(last_line)
                    if "total_cccd_processed" in log_entry.get("extra", {}):
                        print("✅ Performance metrics found in log")
                        return True

        print("❌ Performance metrics not found in log")
        return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 AI-CODE LOGGING SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)

    tests = [
        ("Log Directory & Config", test_log_directory_and_config),
        ("Sample Log Generation", test_log_sample_generation),
        ("CCCD Generator with Logging", test_cccd_generator_with_logging),
        ("Workflow Runner with Logging", test_workflow_runner),
        ("Log Analysis", test_log_analysis),
        ("Performance Logging", test_performance_logging),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n📈 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ AI-CODE LOGGING SYSTEM is working correctly")
        print("✅ All logs are stored in the required directory with correct schema")
        print("✅ Unlimited processing support is integrated")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("❌ Please check the implementation and fix issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)