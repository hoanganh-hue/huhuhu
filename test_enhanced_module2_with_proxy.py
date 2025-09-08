#!/usr/bin/env python3
"""
Test Enhanced Module 2 with proper proxy configuration
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

def test_with_proxy():
    """Test Enhanced Module 2 with proxy enabled"""
    print("🧪 Testing Enhanced Module 2 with Proxy")
    print("=" * 60)
    
    try:
        # Set environment variables for proxy
        os.environ['PROXY_ENABLED'] = 'true'
        os.environ['PROXY_TYPE'] = 'socks5'
        os.environ['PROXY_SOCKS5_HOST'] = 'ip.mproxy.vn'
        os.environ['PROXY_SOCKS5_PORT'] = '12301'
        os.environ['PROXY_SOCKS5_USERNAME'] = 'beba111'
        os.environ['PROXY_SOCKS5_PASSWORD'] = 'tDV5tkMchYUBMD'
        
        # Import the enhanced module
        from src.modules.core.module_2_check_cccd_enhanced import Module2CheckCCCDEnhanced
        
        # Configuration
        config = {
            'timeout': 30,
            'max_retries': 2,  # Reduced for testing
            'output_file': 'test_enhanced_module2_proxy_output.txt'
        }
        
        # Initialize module
        print("🔧 Initializing Enhanced Module 2 with proxy...")
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
        print(f"❌ Error testing Enhanced Module 2 with proxy: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 ENHANCED MODULE 2 PROXY TEST")
    print("=" * 80)
    
    success = test_with_proxy()
    
    print("\n📋 TEST RESULT")
    print("=" * 80)
    print(f"Enhanced Module 2 with Proxy: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 Enhanced Module 2 with proxy is working!")
        print("   - Proxy configuration loaded")
        print("   - Anti-bot capabilities active")
        print("   - Real data extraction functional")
    else:
        print("\n⚠️ Enhanced Module 2 with proxy needs attention")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)