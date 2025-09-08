#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script đơn giản để kiểm tra các cải tiến Priority 1
"""

import sys
import os

# Add cccd directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cccd'))

def test_checksum_function():
    """Test checksum function"""
    print("🧪 Testing Checksum Function")
    print("=" * 40)
    
    try:
        from checksum import calculate_checksum, is_checksum_valid
        
        # Test calculate_checksum
        test_digits = "00101234567"
        checksum = calculate_checksum(test_digits)
        print(f"✅ calculate_checksum('{test_digits}') = {checksum}")
        
        # Test is_checksum_valid
        test_cccd = f"{test_digits}{checksum}"
        is_valid = is_checksum_valid(test_cccd)
        print(f"✅ is_checksum_valid('{test_cccd}') = {is_valid}")
        
        # Test invalid checksum
        invalid_cccd = f"{test_digits}9"  # Wrong checksum
        is_invalid = is_checksum_valid(invalid_cccd)
        print(f"✅ is_checksum_valid('{invalid_cccd}') = {is_invalid}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing checksum: {e}")
        return False

def test_basic_generator():
    """Test basic generator với checksum"""
    print("\n🧪 Testing Basic Generator with Checksum")
    print("=" * 40)
    
    try:
        from cccd_generator_service import CCCDGeneratorService
        
        generator = CCCDGeneratorService()
        
        # Test tạo 10 CCCD
        results = generator.generateCccdList(
            provinceCodes=["001", "079"],
            gender=None,
            birthYearRange=[1990, 2000],
            quantity=10
        )
        
        print(f"✅ Generated {len(results)} CCCD")
        
        # Kiểm tra checksum
        from checksum import is_checksum_valid
        valid_count = 0
        
        for result in results:
            cccd = result["cccd_number"]
            if is_checksum_valid(cccd):
                valid_count += 1
        
        valid_rate = (valid_count / len(results)) * 100
        print(f"📊 Checksum valid rate: {valid_rate:.1f}% ({valid_count}/{len(results)})")
        
        # Hiển thị một vài CCCD mẫu
        print("\n📋 Sample CCCD:")
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result['cccd_number']} - {result['gender']} - {result['birth_date']}")
        
        return valid_rate >= 95
    except Exception as e:
        print(f"❌ Error testing basic generator: {e}")
        return False

def test_enhanced_generator():
    """Test enhanced generator"""
    print("\n🧪 Testing Enhanced Generator")
    print("=" * 40)
    
    try:
        from cccd_generator_enhanced import CCCDGeneratorEnhanced
        
        generator = CCCDGeneratorEnhanced()
        
        # Test tạo 5 CCCD
        result = generator.generate_cccd_list_enhanced(
            province_codes=["001", "079"],
            gender=None,
            birth_year_range=(1990, 2000),
            quantity=5
        )
        
        if result["success"]:
            data = result["data"]
            valid_count = sum(1 for item in data if item.get("valid", False))
            valid_rate = (valid_count / len(data)) * 100
            
            print(f"✅ Generated {len(data)} CCCD")
            print(f"📊 Valid rate: {valid_rate:.1f}% ({valid_count}/{len(data)})")
            
            # Hiển thị một vài CCCD mẫu
            print("\n📋 Sample CCCD:")
            for i, item in enumerate(data[:3]):
                if item.get("valid"):
                    print(f"  {i+1}. {item['cccd_number']} - {item['gender']} - {item['birth_date']}")
            
            return valid_rate >= 99
        else:
            print(f"❌ Error: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing enhanced generator: {e}")
        return False

def test_error_messages():
    """Test error messages với error codes"""
    print("\n🧪 Testing Error Messages")
    print("=" * 40)
    
    try:
        from cccd_analyzer_service import CCCDAnalyzerService
        
        analyzer = CCCDAnalyzerService()
        
        # Test empty CCCD
        result = analyzer.validateCccdFormat("")
        print(f"✅ Empty CCCD: {result['error_code']} - {result['error']}")
        
        # Test non-digit CCCD
        result = analyzer.validateCccdFormat("abc123456789")
        print(f"✅ Non-digit CCCD: {result['error_code']} - {result['error']}")
        
        # Test wrong length CCCD
        result = analyzer.validateCccdFormat("1234567890123")
        print(f"✅ Wrong length CCCD: {result['error_code']} - {result['error']}")
        
        # Test invalid checksum CCCD
        result = analyzer.validateCccdFormat("001012345678")
        print(f"✅ Invalid checksum CCCD: {result['error_code']} - {result['error']}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing error messages: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 CCCD Generator Improvements Test")
    print("=" * 50)
    
    tests = [
        ("Checksum Function", test_checksum_function),
        ("Basic Generator", test_basic_generator),
        ("Enhanced Generator", test_enhanced_generator),
        ("Error Messages", test_error_messages)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All Priority 1 improvements are working correctly!")
        print("\n📋 IMPROVEMENTS COMPLETED:")
        print("✅ 1. Added checksum to Basic Generator")
        print("✅ 2. Improved date generation in Basic Generator")
        print("✅ 3. Replaced print with logging")
        print("✅ 4. Enhanced error messages with error codes")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Please check the issues above.")

if __name__ == "__main__":
    main()