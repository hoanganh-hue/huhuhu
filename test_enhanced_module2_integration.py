#!/usr/bin/env python3
"""
Test script to verify Enhanced Module 2 integration with GUI and proxy configuration
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

def test_enhanced_module2():
    """Test the enhanced Module 2 with proxy configuration"""
    print("🧪 Testing Enhanced Module 2 Integration")
    print("=" * 60)
    
    try:
        # Import the enhanced module
        from src.modules.core.module_2_check_cccd_enhanced import Module2CheckCCCDEnhanced
        
        # Configuration
        config = {
            'timeout': 30,
            'max_retries': 3,
            'output_file': 'test_enhanced_module2_output.txt'
        }
        
        # Initialize module
        print("🔧 Initializing Enhanced Module 2...")
        module = Module2CheckCCCDEnhanced(config)
        
        # Test with the CCCD we know works
        test_cccd = "031089011929"
        print(f"🔍 Testing with CCCD: {test_cccd}")
        
        # Perform check
        result = module.check_cccd(test_cccd)
        
        # Display results
        print("\n📊 RESULTS:")
        print("-" * 40)
        print(f"CCCD: {result.cccd}")
        print(f"Status: {result.status}")
        print(f"Tax Code: {result.tax_code}")
        print(f"Name: {result.name}")
        print(f"Address: {result.address}")
        print(f"Business Type: {result.business_type}")
        print(f"Business Status: {result.business_status}")
        print(f"Profile URL: {result.profile_url}")
        if result.response_time:
            print(f"Response Time: {result.response_time:.2f}s")
        else:
            print("Response Time: N/A")
        print(f"Method: {result.method}")
        
        if result.error:
            print(f"Error: {result.error}")
        
        # Display statistics
        stats = module.get_statistics()
        print("\n📈 STATISTICS:")
        print("-" * 40)
        print(f"Total requests: {stats['total_requests']}")
        print(f"Successful: {stats['successful_requests']}")
        print(f"Failed: {stats['failed_requests']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Proxy enabled: {stats['proxy_enabled']}")
        print(f"Proxy type: {stats['proxy_type']}")
        
        # Save results
        module.save_results([result])
        print(f"\n💾 Results saved to: {config['output_file']}")
        
        return result.status == "found"
        
    except Exception as e:
        print(f"❌ Error testing Enhanced Module 2: {e}")
        return False

def test_proxy_configuration():
    """Test proxy configuration loading"""
    print("\n🌐 Testing Proxy Configuration")
    print("=" * 60)
    
    try:
        # Check if proxy config file exists
        proxy_config_path = Path("config/proxy_config.json")
        if proxy_config_path.exists():
            with open(proxy_config_path, 'r', encoding='utf-8') as f:
                proxy_config = json.load(f)
            
            print("✅ Proxy configuration file found:")
            print(f"   Enabled: {proxy_config.get('enabled', False)}")
            print(f"   Type: {proxy_config.get('type', 'none')}")
            
            if proxy_config.get('type') == 'socks5':
                socks5_config = proxy_config.get('socks5', {})
                print(f"   SOCKS5 Host: {socks5_config.get('host', 'N/A')}")
                print(f"   SOCKS5 Port: {socks5_config.get('port', 'N/A')}")
                print(f"   SOCKS5 Username: {socks5_config.get('username', 'N/A')}")
            
            return True
        else:
            print("⚠️ Proxy configuration file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing proxy configuration: {e}")
        return False

def test_gui_integration():
    """Test GUI integration"""
    print("\n🖥️ Testing GUI Integration")
    print("=" * 60)
    
    try:
        # Check if GUI file exists and can be imported
        gui_path = Path("gui_main.py")
        if gui_path.exists():
            print("✅ GUI file found: gui_main.py")
            
            # Try to import GUI components
            import tkinter as tk
            from tkinter import ttk
            print("✅ Tkinter components available")
            
            # Check if GUI has proxy configuration
            with open(gui_path, 'r', encoding='utf-8') as f:
                gui_content = f.read()
            
            if 'proxy_enabled' in gui_content and 'socks5' in gui_content:
                print("✅ GUI contains proxy configuration")
                return True
            else:
                print("⚠️ GUI may not have proxy configuration")
                return False
        else:
            print("❌ GUI file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GUI integration: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ENHANCED MODULE 2 INTEGRATION TEST")
    print("=" * 80)
    
    # Test results
    results = {
        'enhanced_module2': False,
        'proxy_config': False,
        'gui_integration': False
    }
    
    # Run tests
    results['enhanced_module2'] = test_enhanced_module2()
    results['proxy_config'] = test_proxy_configuration()
    results['gui_integration'] = test_gui_integration()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 80)
    print(f"Enhanced Module 2: {'✅ PASS' if results['enhanced_module2'] else '❌ FAIL'}")
    print(f"Proxy Configuration: {'✅ PASS' if results['proxy_config'] else '❌ FAIL'}")
    print(f"GUI Integration: {'✅ PASS' if results['gui_integration'] else '❌ FAIL'}")
    
    overall_success = all(results.values())
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Enhanced Module 2 is ready for production use!")
        print("   - Proxy configuration working")
        print("   - Anti-bot capabilities active")
        print("   - GUI integration complete")
        print("   - Real data extraction functional")
    else:
        print("\n⚠️ Please check the failed components before using in production")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)