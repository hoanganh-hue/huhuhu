#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced Anti-Bot Module 7
Tests all methods: requests session, httpx SOCKS5, and Playwright fallback
"""

import asyncio
import time
import logging
import sys
import os
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.core.module_7_enhanced_anti_bot import EnhancedAntiBotScraper, SearchResult
from modules.core.module_7_playwright_fallback import PlaywrightScraper, PlaywrightConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTester:
    """Comprehensive tester for all anti-bot methods"""
    
    def __init__(self):
        self.test_cccds = [
            "001087016369",
            "001184032114", 
            "001098021288",
            "001094001628",
            "036092002342"
        ]
        self.results = []
        self.stats = {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "methods_tested": []
        }
    
    def test_enhanced_anti_bot(self) -> List[SearchResult]:
        """Test enhanced anti-bot scraper"""
        logger.info("🚀 Testing Enhanced Anti-Bot Scraper...")
        logger.info("="*60)
        
        scraper = EnhancedAntiBotScraper()
        results = []
        
        for i, cccd in enumerate(self.test_cccds):
            logger.info(f"\n🔍 Test {i+1}/{len(self.test_cccds)}: {cccd}")
            logger.info("-" * 40)
            
            start_time = time.time()
            result = scraper.search_with_fallback(cccd)
            test_time = time.time() - start_time
            
            results.append(result)
            self.stats["total_tests"] += 1
            
            # Log result
            if result.status == "found":
                logger.info(f"✅ SUCCESS: {result.tax_code} - {result.name}")
                if result.profile_url:
                    logger.info(f"🔗 Profile: {result.profile_url}")
                self.stats["successful_tests"] += 1
            elif result.status == "not_found":
                logger.info("❌ NOT FOUND")
                self.stats["failed_tests"] += 1
            else:
                logger.info(f"⚠️ ERROR: {result.error_message}")
                self.stats["failed_tests"] += 1
            
            logger.info(f"⏱️ Test time: {test_time:.2f}s")
            logger.info(f"🔧 Method: {result.method_used}")
            logger.info(f"📊 Response time: {result.response_time:.2f}s")
            
            # Add delay between tests
            if i < len(self.test_cccds) - 1:
                delay = 5
                logger.info(f"⏳ Waiting {delay}s before next test...")
                time.sleep(delay)
        
        # Log scraper statistics
        scraper_stats = scraper.get_stats()
        logger.info(f"\n📊 Enhanced Anti-Bot Statistics:")
        for key, value in scraper_stats.items():
            logger.info(f"  {key}: {value}")
        
        self.stats["methods_tested"].append("enhanced_anti_bot")
        return results
    
    async def test_playwright_fallback(self) -> List[Dict[str, Any]]:
        """Test Playwright fallback"""
        logger.info("\n🚀 Testing Playwright Fallback...")
        logger.info("="*60)
        
        config = PlaywrightConfig(
            headless=True,
            proxy_server="socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301"
        )
        
        results = []
        
        async with PlaywrightScraper(config) as scraper:
            for i, cccd in enumerate(self.test_cccds):
                logger.info(f"\n🔍 Playwright Test {i+1}/{len(self.test_cccds)}: {cccd}")
                logger.info("-" * 40)
                
                start_time = time.time()
                result = await scraper.search_with_browser(cccd)
                test_time = time.time() - start_time
                
                results.append(result)
                self.stats["total_tests"] += 1
                
                # Log result
                if result["status"] == "found":
                    logger.info(f"✅ SUCCESS: {result['tax_code']} - {result['name']}")
                    if result.get("profile_url"):
                        logger.info(f"🔗 Profile: {result['profile_url']}")
                    self.stats["successful_tests"] += 1
                elif result["status"] == "not_found":
                    logger.info("❌ NOT FOUND")
                    self.stats["failed_tests"] += 1
                else:
                    logger.info(f"⚠️ ERROR: {result.get('error_message', 'Unknown error')}")
                    self.stats["failed_tests"] += 1
                
                logger.info(f"⏱️ Test time: {test_time:.2f}s")
                logger.info(f"🔧 Method: {result.get('method_used', 'unknown')}")
                logger.info(f"📊 Response time: {result.get('response_time', 0):.2f}s")
                
                # Add delay between tests
                if i < len(self.test_cccds) - 1:
                    delay = 8  # Longer delay for browser tests
                    logger.info(f"⏳ Waiting {delay}s before next test...")
                    await asyncio.sleep(delay)
            
            # Log scraper statistics
            scraper_stats = scraper.get_stats()
            logger.info(f"\n📊 Playwright Statistics:")
            for key, value in scraper_stats.items():
                logger.info(f"  {key}: {value}")
        
        self.stats["methods_tested"].append("playwright_fallback")
        return results
    
    def compare_results(self, enhanced_results: List[SearchResult], playwright_results: List[Dict[str, Any]]):
        """Compare results between methods"""
        logger.info("\n🔍 COMPARING RESULTS")
        logger.info("="*60)
        
        for i, cccd in enumerate(self.test_cccds):
            logger.info(f"\n📋 CCCD: {cccd}")
            logger.info("-" * 30)
            
            enhanced = enhanced_results[i]
            playwright = playwright_results[i]
            
            # Enhanced results
            logger.info(f"Enhanced Anti-Bot:")
            logger.info(f"  Status: {enhanced.status}")
            if enhanced.status == "found":
                logger.info(f"  Tax Code: {enhanced.tax_code}")
                logger.info(f"  Name: {enhanced.name}")
            logger.info(f"  Method: {enhanced.method_used}")
            logger.info(f"  Response Time: {enhanced.response_time:.2f}s")
            
            # Playwright results
            logger.info(f"Playwright:")
            logger.info(f"  Status: {playwright['status']}")
            if playwright['status'] == "found":
                logger.info(f"  Tax Code: {playwright['tax_code']}")
                logger.info(f"  Name: {playwright['name']}")
            logger.info(f"  Method: {playwright.get('method_used', 'unknown')}")
            logger.info(f"  Response Time: {playwright.get('response_time', 0):.2f}s")
            
            # Comparison
            if enhanced.status == "found" and playwright['status'] == "found":
                if enhanced.tax_code == playwright['tax_code']:
                    logger.info("✅ Both methods found same result")
                else:
                    logger.warning("⚠️ Different results found")
            elif enhanced.status == "found" and playwright['status'] != "found":
                logger.info("📊 Only Enhanced Anti-Bot found result")
            elif enhanced.status != "found" and playwright['status'] == "found":
                logger.info("📊 Only Playwright found result")
            else:
                logger.info("❌ Neither method found result")
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        logger.info("\n" + "="*60)
        logger.info("📊 COMPREHENSIVE TEST FINAL REPORT")
        logger.info("="*60)
        
        # Overall statistics
        total_tests = self.stats["total_tests"]
        successful_tests = self.stats["successful_tests"]
        failed_tests = self.stats["failed_tests"]
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Methods Tested: {', '.join(self.stats['methods_tested'])}")
        
        # Recommendations
        logger.info(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 80:
            logger.info("✅ Excellent success rate! The enhanced anti-bot methods are working well.")
        elif success_rate >= 50:
            logger.info("⚠️ Moderate success rate. Consider using paid proxies or additional methods.")
        else:
            logger.info("❌ Low success rate. Strong anti-bot protection detected. Consider:")
            logger.info("   - Using residential proxies")
            logger.info("   - Implementing CAPTCHA solving")
            logger.info("   - Using VPN rotation")
            logger.info("   - Implementing more sophisticated browser automation")
        
        # Next steps
        logger.info(f"\n🚀 NEXT STEPS:")
        logger.info("1. Analyze the logs for specific error patterns")
        logger.info("2. Test with different proxy providers")
        logger.info("3. Implement additional anti-detection measures")
        logger.info("4. Consider using the working method for production")
        
        # Save results to file
        self.save_results_to_file()
    
    def save_results_to_file(self):
        """Save test results to file"""
        try:
            with open("comprehensive_test_results.txt", "w", encoding="utf-8") as f:
                f.write("COMPREHENSIVE ANTI-BOT TEST RESULTS\n")
                f.write("="*50 + "\n\n")
                
                f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Tests: {self.stats['total_tests']}\n")
                f.write(f"Successful: {self.stats['successful_tests']}\n")
                f.write(f"Failed: {self.stats['failed_tests']}\n")
                f.write(f"Success Rate: {(self.stats['successful_tests'] / self.stats['total_tests'] * 100):.1f}%\n")
                f.write(f"Methods Tested: {', '.join(self.stats['methods_tested'])}\n\n")
                
                f.write("DETAILED RESULTS:\n")
                f.write("-" * 30 + "\n")
                
                for i, cccd in enumerate(self.test_cccds):
                    f.write(f"\nCCCD: {cccd}\n")
                    # Add detailed results here if needed
                
            logger.info("📄 Results saved to comprehensive_test_results.txt")
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

async def main():
    """Main test function"""
    logger.info("🚀 Starting Comprehensive Anti-Bot Test")
    logger.info("Testing with SOCKS5 proxy: ip.mproxy.vn:12301")
    logger.info("="*60)
    
    tester = ComprehensiveTester()
    
    try:
        # Test 1: Enhanced Anti-Bot Scraper
        enhanced_results = tester.test_enhanced_anti_bot()
        
        # Wait between test suites
        logger.info("\n⏳ Waiting 10s before Playwright tests...")
        time.sleep(10)
        
        # Test 2: Playwright Fallback
        playwright_results = await tester.test_playwright_fallback()
        
        # Compare results
        tester.compare_results(enhanced_results, playwright_results)
        
        # Generate final report
        tester.generate_final_report()
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        raise
    
    logger.info("\n✅ Comprehensive test completed!")

if __name__ == "__main__":
    asyncio.run(main())