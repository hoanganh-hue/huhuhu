#!/usr/bin/env python3
"""
Test script để kiểm tra module scraper với danh sách CCCD
Thu thập metrics về thời gian, tỷ lệ thành công và phát hiện rate limiting
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import statistics

# Thêm src vào Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from check_cccd.scraper import scrape_cccd_sync
from check_cccd.logging import logger

# Danh sách CCCD cần test
TEST_CCCD_LIST = [
    "025090000198",
    "036092002342",
    "019084000004",
    "001091021084",
    "001087016369",
    "079199030020",
    "001161041024"
]

class CCCDTestRunner:
    """Class để chạy test với danh sách CCCD và thu thập metrics."""

    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None

    def run_single_test(self, cccd: str) -> Dict:
        """Chạy test cho một CCCD."""
        test_start = time.time()

        try:
            result = scrape_cccd_sync(cccd)
            test_duration = time.time() - test_start

            test_result = {
                "cccd": cccd,
                "status": result.get("status"),
                "duration_ms": test_duration * 1000,
                "matches_count": len(result.get("matches", [])),
                "error_message": result.get("error_message"),
                "timestamp": datetime.now().isoformat(),
                "success": result.get("status") in ["found", "not_found"]
            }

            return test_result

        except Exception as e:
            test_duration = time.time() - test_start
            return {
                "cccd": cccd,
                "status": "error",
                "duration_ms": test_duration * 1000,
                "matches_count": 0,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }

    def run_all_tests(self, delay_between_tests: float = 1.5) -> List[Dict]:
        """Chạy test cho tất cả CCCD trong danh sách."""
        self.start_time = time.time()
        logger.info("🚀 Bắt đầu test với danh sách CCCD", count=len(TEST_CCCD_LIST))

        for i, cccd in enumerate(TEST_CCCD_LIST):
            logger.info(f"📋 Test CCCD {i+1}/{len(TEST_CCCD_LIST)}: {cccd}")

            # Chạy test
            result = self.run_single_test(cccd)
            self.results.append(result)

            # Log kết quả
            if result["success"]:
                logger.info("✅ Test thành công",
                           cccd=cccd,
                           status=result["status"],
                           duration_ms=round(result["duration_ms"], 2),
                           matches=result["matches_count"])
            else:
                logger.error("❌ Test thất bại",
                            cccd=cccd,
                            error=result["error_message"],
                            duration_ms=round(result["duration_ms"], 2))

            # Delay giữa các test để tránh rate limiting
            if i < len(TEST_CCCD_LIST) - 1:
                logger.info(f"⏳ Đợi {delay_between_tests}s trước test tiếp theo...")
                time.sleep(delay_between_tests)

        self.end_time = time.time()
        total_duration = self.end_time - self.start_time

        logger.info("🎉 Hoàn thành test",
                   total_tests=len(self.results),
                   successful=sum(1 for r in self.results if r["success"]),
                   total_duration_s=round(total_duration, 2))

        return self.results

    def analyze_results(self) -> Dict:
        """Phân tích kết quả test."""
        if not self.results:
            return {}

        successful_tests = [r for r in self.results if r["success"]]
        failed_tests = [r for r in self.results if not r["success"]]

        durations = [r["duration_ms"] for r in self.results]
        successful_durations = [r["duration_ms"] for r in successful_tests]

        analysis = {
            "total_tests": len(self.results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(self.results) * 100,
            "total_duration_s": self.end_time - self.start_time if self.end_time else 0,

            # Thống kê thời gian
            "duration_stats": {
                "min_ms": min(durations) if durations else 0,
                "max_ms": max(durations) if durations else 0,
                "avg_ms": statistics.mean(durations) if durations else 0,
                "median_ms": statistics.median(durations) if durations else 0,
            },

            # Thống kê thời gian thành công
            "successful_duration_stats": {
                "min_ms": min(successful_durations) if successful_durations else 0,
                "max_ms": max(successful_durations) if successful_durations else 0,
                "avg_ms": statistics.mean(successful_durations) if successful_durations else 0,
                "median_ms": statistics.median(successful_durations) if successful_durations else 0,
            },

            # Chi tiết từng test
            "test_details": self.results,

            # Phát hiện rate limiting
            "rate_limiting_indicators": self._detect_rate_limiting(),

            # Đề xuất tối ưu
            "recommendations": self._generate_recommendations()
        }

        return analysis

    def _detect_rate_limiting(self) -> List[str]:
        """Phát hiện dấu hiệu rate limiting."""
        indicators = []

        # Kiểm tra thời gian response tăng dần
        durations = [r["duration_ms"] for r in self.results]
        if len(durations) >= 3:
            # So sánh thời gian của test đầu và cuối
            first_avg = statistics.mean(durations[:3])
            last_avg = statistics.mean(durations[-3:])
            if last_avg > first_avg * 1.5:  # Tăng 50%
                indicators.append("Thời gian response tăng dần - có thể bị rate limiting")

        # Kiểm tra tỷ lệ lỗi cao
        error_rate = sum(1 for r in self.results if not r["success"]) / len(self.results)
        if error_rate > 0.5:  # > 50% lỗi
            indicators.append(f"Tỷ lệ lỗi cao: {error_rate*100:.1f}%")

        # Kiểm tra lỗi liên tiếp
        consecutive_failures = 0
        max_consecutive_failures = 0
        for result in self.results:
            if not result["success"]:
                consecutive_failures += 1
                max_consecutive_failures = max(max_consecutive_failures, consecutive_failures)
            else:
                consecutive_failures = 0

        if max_consecutive_failures >= 3:
            indicators.append(f"Lỗi liên tiếp nhiều lần: {max_consecutive_failures} test liên tiếp thất bại")

        return indicators

    def _generate_recommendations(self) -> List[str]:
        """Tạo đề xuất tối ưu."""
        recommendations = []

        analysis = self.analyze_results()

        if analysis.get("success_rate", 0) < 80:
            recommendations.append("⚠️ Tăng delay giữa các request nếu tỷ lệ thành công thấp")

        if analysis.get("duration_stats", {}).get("avg_ms", 0) > 15000:  # > 15s
            recommendations.append("⚠️ Tăng timeout request nếu thời gian quá lâu")

        if len(self._detect_rate_limiting()) > 0:
            recommendations.append("🚨 Phát hiện rate limiting - tăng delay hoặc thêm proxy")
            recommendations.append("🚨 Kích hoạt anti-bot strategies mạnh hơn")

        # Đánh giá hiệu quả tối ưu
        if analysis.get("successful_duration_stats", {}).get("avg_ms", 0) < 8000:  # < 8s
            recommendations.append("✅ Cấu hình tối ưu hoạt động tốt")
        else:
            recommendations.append("🔄 Cần tối ưu thêm delay trong anti-bot")

        return recommendations

    def save_results(self, output_file: str = "test_results.json"):
        """Lưu kết quả test ra file."""
        analysis = self.analyze_results()

        output_data = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "cccd_list": TEST_CCCD_LIST,
                "total_duration_s": analysis.get("total_duration_s", 0)
            },
            "analysis": analysis
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Đã lưu kết quả test vào: {output_file}")


def main():
    """Main function."""
    print("=" * 60)
    print("🧪 Test Module Scraper - Check CCCD")
    print("=" * 60)

    # Khởi tạo test runner
    runner = CCCDTestRunner()

    # Chạy test
    try:
        results = runner.run_all_tests(delay_between_tests=1.5)

        # Phân tích kết quả
        analysis = runner.analyze_results()

        # Hiển thị kết quả tổng quan
        print("\n📊 KẾT QUẢ TEST:")
        print(f"   Tổng số test: {analysis['total_tests']}")
        print(f"   Thành công: {analysis['successful_tests']}")
        print(f"   Thất bại: {analysis['failed_tests']}")
        print(f"   Tỷ lệ thành công: {analysis['success_rate']:.1f}%")
        print(f"   Tổng thời gian: {analysis['total_duration_s']:.2f}s")

        # Thống kê thời gian
        duration_stats = analysis['duration_stats']
        print("\n⏱️  THỜI GIAN:")
        print(f"   Min: {duration_stats['min_ms']:.2f}ms")
        print(f"   Max: {duration_stats['max_ms']:.2f}ms")
        print(f"   Trung bình: {duration_stats['avg_ms']:.2f}ms")
        print(f"   Trung vị: {duration_stats['median_ms']:.2f}ms")

        # Phát hiện rate limiting
        if analysis['rate_limiting_indicators']:
            print("\n🚨 CẢNH BÁO RATE LIMITING:")
            for indicator in analysis['rate_limiting_indicators']:
                print(f"   - {indicator}")

        # Đề xuất tối ưu
        if analysis['recommendations']:
            print("\n💡 ĐỀ XUẤT TỐI ƯU:")
            for rec in analysis['recommendations']:
                print(f"   - {rec}")

        # Lưu kết quả
        runner.save_results()

        print("\n✅ Test hoàn thành! Kết quả đã được lưu vào test_results.json")
        return True

    except KeyboardInterrupt:
        print("\n👋 Test bị hủy bởi người dùng")
        return False
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)