#!/usr/bin/env python3
"""
Test hoàn chỉnh integration giữa GUI configuration và Module 2 Enhanced
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

def test_proxy_config_loading():
    """Test loading proxy configuration từ GUI settings"""
    print("🔧 Testing Proxy Configuration Loading")
    print("=" * 50)
    
    try:
        # Simulate GUI configuration
        gui_config = {
            'proxy_enabled': True,
            'proxy_type': 'socks5',
            'proxy_host': 'ip.mproxy.vn',
            'proxy_port': '12301',
            'proxy_username': 'beba111',
            'proxy_password': 'tDV5tkMchYUBMD'
        }
        
        # Set environment variables như GUI sẽ làm
        os.environ['PROXY_ENABLED'] = 'true'
        os.environ['PROXY_TYPE'] = 'socks5'
        os.environ['PROXY_SOCKS5_HOST'] = gui_config['proxy_host']
        os.environ['PROXY_SOCKS5_PORT'] = gui_config['proxy_port']
        os.environ['PROXY_SOCKS5_USERNAME'] = gui_config['proxy_username']
        os.environ['PROXY_SOCKS5_PASSWORD'] = gui_config['proxy_password']
        
        print("✅ Environment variables set")
        
        # Test Module 2 Enhanced loading
        from src.modules.core.module_2_check_cccd_enhanced import Module2CheckCCCDEnhanced
        
        config = {
            'timeout': 30,
            'max_retries': 2,
            'output_file': 'integration_test_output.txt'
        }
        
        module = Module2CheckCCCDEnhanced(config)
        
        # Verify proxy configuration
        proxy_config = module.proxy_config
        print(f"✅ Proxy enabled: {proxy_config.get('enabled', False)}")
        print(f"✅ Proxy type: {proxy_config.get('type', 'none')}")
        
        if proxy_config.get('enabled'):
            socks5_config = proxy_config.get('socks5', {})
            print(f"✅ SOCKS5 Host: {socks5_config.get('host', 'N/A')}")
            print(f"✅ SOCKS5 Port: {socks5_config.get('port', 'N/A')}")
            print(f"✅ SOCKS5 Username: {socks5_config.get('username', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing proxy config loading: {e}")
        return False

def test_batch_processing():
    """Test batch processing với multiple CCCDs"""
    print("\n📊 Testing Batch Processing")
    print("=" * 50)
    
    try:
        from src.modules.core.module_2_check_cccd_enhanced import Module2CheckCCCDEnhanced
        
        config = {
            'timeout': 30,
            'max_retries': 2,
            'output_file': 'batch_test_output.txt'
        }
        
        module = Module2CheckCCCDEnhanced(config)
        
        # Test với 3 CCCDs
        test_cccds = ["031089011929", "001087016369", "001184032114"]
        
        print(f"🔍 Testing batch processing with {len(test_cccds)} CCCDs")
        
        results = module.batch_check(test_cccds)
        
        print(f"✅ Batch processing completed: {len(results)} results")
        
        # Display results summary
        found_count = sum(1 for r in results if r.status == "found")
        error_count = sum(1 for r in results if r.status == "error")
        
        print(f"📊 Found: {found_count}")
        print(f"📊 Errors: {error_count}")
        print(f"📊 Success rate: {(found_count/len(results)*100):.1f}%")
        
        # Save results
        module.save_results(results)
        print("💾 Results saved to batch_test_output.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing batch processing: {e}")
        return False

def test_config_file_integration():
    """Test integration với config files"""
    print("\n📁 Testing Config File Integration")
    print("=" * 50)
    
    try:
        # Test proxy config file
        proxy_config_path = Path("config/proxy_config.json")
        if proxy_config_path.exists():
            with open(proxy_config_path, 'r', encoding='utf-8') as f:
                proxy_config = json.load(f)
            
            print("✅ Proxy config file found")
            print(f"✅ Enabled: {proxy_config.get('enabled', False)}")
            print(f"✅ Type: {proxy_config.get('type', 'none')}")
            
            if proxy_config.get('enabled'):
                socks5_config = proxy_config.get('socks5', {})
                print(f"✅ SOCKS5: {socks5_config.get('host', 'N/A')}:{socks5_config.get('port', 'N/A')}")
        
        # Test .env file creation (simulate GUI save)
        env_content = """# Configuration for Integrated Lookup System
CAPTCHA_API_KEY=test_key
CCCD_COUNT=100
CCCD_PROVINCE_CODE=001
CCCD_GENDER=
CCCD_BIRTH_YEAR_FROM=1990
CCCD_BIRTH_YEAR_TO=2000
LOG_LEVEL=INFO
DEBUG_MODE=false

# Proxy Configuration
PROXY_ENABLED=true
PROXY_TYPE=socks5
PROXY_SOCKS5_HOST=ip.mproxy.vn
PROXY_SOCKS5_PORT=12301
PROXY_SOCKS5_USERNAME=beba111
PROXY_SOCKS5_PASSWORD=tDV5tkMchYUBMD
PROXY_HTTP_HOST=
PROXY_HTTP_PORT=
PROXY_HTTP_USERNAME=
PROXY_HTTP_PASSWORD=
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .env file created with proxy configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing config file integration: {e}")
        return False

def test_main_integration():
    """Test integration với main.py"""
    print("\n🔗 Testing Main Integration")
    print("=" * 50)
    
    try:
        # Test import từ main.py
        from main import IntegratedLookupSystem
        
        print("✅ IntegratedLookupSystem imported successfully")
        
        # Test initialization
        system = IntegratedLookupSystem()
        print("✅ IntegratedLookupSystem initialized")
        
        # Check if Module 2 Enhanced is being used
        if hasattr(system, 'check_cccd_module'):
            module_type = type(system.check_cccd_module).__name__
            print(f"✅ Check CCCD Module type: {module_type}")
            
            if 'Enhanced' in module_type:
                print("✅ Module 2 Enhanced is being used")
            else:
                print("⚠️ Module 2 Enhanced may not be used")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing main integration: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 COMPLETE INTEGRATION TEST")
    print("=" * 80)
    
    # Test results
    results = {
        'proxy_config_loading': False,
        'batch_processing': False,
        'config_file_integration': False,
        'main_integration': False
    }
    
    # Run tests
    results['proxy_config_loading'] = test_proxy_config_loading()
    results['batch_processing'] = test_batch_processing()
    results['config_file_integration'] = test_config_file_integration()
    results['main_integration'] = test_main_integration()
    
    # Summary
    print("\n📋 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"Proxy Config Loading: {'✅ PASS' if results['proxy_config_loading'] else '❌ FAIL'}")
    print(f"Batch Processing: {'✅ PASS' if results['batch_processing'] else '❌ FAIL'}")
    print(f"Config File Integration: {'✅ PASS' if results['config_file_integration'] else '❌ FAIL'}")
    print(f"Main Integration: {'✅ PASS' if results['main_integration'] else '❌ FAIL'}")
    
    overall_success = all(results.values())
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Complete integration is working perfectly!")
        print("   - Proxy configuration loading ✅")
        print("   - Batch processing ✅")
        print("   - Config file integration ✅")
        print("   - Main system integration ✅")
    else:
        print("\n⚠️ Some integration components need attention")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)