#!/usr/bin/env python3
"""
Monitoring Dashboard for Check CCCD
Real-time performance tracking and metrics visualization
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import statistics

# Thêm src vào Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from check_cccd.cache_layer import get_cache_statistics


class MonitoringDashboard:
    """Real-time monitoring dashboard for CCCD scraping performance."""

    def __init__(self):
        self.metrics_history = []
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.response_times = []

    def record_request(self, cccd: str, status: str, duration_ms: float, cached: bool = False):
        """Record a request for monitoring."""
        self.request_count += 1

        if status == "error":
            self.error_count += 1

        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        self.response_times.append(duration_ms)

        # Keep only last 1000 response times for memory efficiency
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

        # Record metrics snapshot every 10 requests
        if self.request_count % 10 == 0:
            self._record_metrics_snapshot()

    def _record_metrics_snapshot(self):
        """Record current metrics snapshot."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "success_rate": ((self.request_count - self.error_count) / self.request_count * 100) if self.request_count > 0 else 0,
            "cache_hit_rate": (self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times) if self.response_times else 0,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else 0
        }

        self.metrics_history.append(snapshot)

        # Keep only last 100 snapshots
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics."""
        cache_stats = get_cache_statistics()

        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.start_time),
            "total_requests": self.request_count,
            "successful_requests": self.request_count - self.error_count,
            "error_requests": self.error_count,
            "success_rate": f"{((self.request_count - self.error_count) / self.request_count * 100):.1f}%" if self.request_count > 0 else "0%",
            "cache_performance": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": f"{(self.cache_hits / (self.cache_hits + self.cache_misses) * 100):.1f}%" if (self.cache_hits + self.cache_misses) > 0 else "0%",
                "redis_status": "Connected" if cache_stats.get("redis_connected") else "Disconnected",
                "cached_keys": cache_stats.get("cached_keys", 0)
            },
            "response_time_stats": {
                "average": f"{statistics.mean(self.response_times):.2f}ms" if self.response_times else "0ms",
                "minimum": f"{min(self.response_times):.2f}ms" if self.response_times else "0ms",
                "maximum": f"{max(self.response_times):.2f}ms" if self.response_times else "0ms",
                "p95": f"{statistics.quantiles(self.response_times, n=20)[18]:.2f}ms" if len(self.response_times) >= 20 else "N/A"
            },
            "system_health": {
                "status": "Healthy" if self._calculate_health_score() > 80 else "Warning",
                "health_score": f"{self._calculate_health_score():.1f}%"
            }
        }

    def _calculate_health_score(self) -> float:
        """Calculate system health score (0-100)."""
        score = 100.0

        # Success rate penalty
        success_rate = ((self.request_count - self.error_count) / self.request_count * 100) if self.request_count > 0 else 100
        if success_rate < 95:
            score -= (100 - success_rate) * 2

        # Response time penalty
        if self.response_times:
            avg_time = statistics.mean(self.response_times)
            if avg_time > 15000:  # > 15s penalty
                score -= min(20, (avg_time - 15000) / 1000)

        # Cache hit rate bonus
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0
        if cache_hit_rate > 50:
            score += min(10, cache_hit_rate / 10)

        return max(0, min(100, score))

    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time."""
        if len(self.metrics_history) < 2:
            return {"message": "Not enough data for trends analysis"}

        recent = self.metrics_history[-10:]  # Last 10 snapshots

        return {
            "response_time_trend": self._calculate_trend([m["avg_response_time"] for m in recent]),
            "success_rate_trend": self._calculate_trend([m["success_rate"] for m in recent]),
            "cache_hit_trend": self._calculate_trend([m["cache_hit_rate"] for m in recent]),
            "request_rate": self._calculate_request_rate(recent)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"

        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])

        diff = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0

        if diff > 5:
            return f"increasing (+{diff:.1f}%)"
        elif diff < -5:
            return f"decreasing ({diff:.1f}%)"
        else:
            return "stable"

    def _calculate_request_rate(self, snapshots: List[Dict]) -> str:
        """Calculate requests per minute."""
        if len(snapshots) < 2:
            return "0 req/min"

        time_diff = (datetime.fromisoformat(snapshots[-1]["timestamp"]) -
                    datetime.fromisoformat(snapshots[0]["timestamp"])).total_seconds()
        request_diff = snapshots[-1]["total_requests"] - snapshots[0]["total_requests"]

        if time_diff > 0:
            rate = request_diff / (time_diff / 60)  # requests per minute
            return f"{rate:.1f} req/min"
        return "0 req/min"

    def display_dashboard(self):
        """Display the monitoring dashboard."""
        metrics = self.get_current_metrics()
        trends = self.get_performance_trends()

        print("\n" + "="*80)
        print("📊 CHECK CCCD - MONITORING DASHBOARD")
        print("="*80)

        print(f"⏰ Uptime: {metrics['uptime']}")
        print(f"📈 Total Requests: {metrics['total_requests']}")
        print(f"✅ Successful: {metrics['successful_requests']}")
        print(f"❌ Errors: {metrics['error_requests']}")
        print(f"🎯 Success Rate: {metrics['success_rate']}")

        print("\n💾 CACHE PERFORMANCE:")
        cache = metrics['cache_performance']
        print(f"   Hits: {cache['hits']}")
        print(f"   Misses: {cache['misses']}")
        print(f"   Hit Rate: {cache['hit_rate']}")
        print(f"   Redis: {cache['redis_status']}")
        print(f"   Cached Keys: {cache['cached_keys']}")

        print("\n⚡ RESPONSE TIME STATS:")
        rt = metrics['response_time_stats']
        print(f"   Average: {rt['average']}")
        print(f"   Min: {rt['min']}")
        print(f"   Max: {rt['max']}")
        print(f"   P95: {rt['p95']}")

        print("\n🏥 SYSTEM HEALTH:")
        health = metrics['system_health']
        print(f"   Status: {health['status']}")
        print(f"   Health Score: {health['health_score']}")

        if isinstance(trends, dict) and "response_time_trend" in trends:
            print("\n📉 PERFORMANCE TRENDS:")
            print(f"   Response Time: {trends['response_time_trend']}")
            print(f"   Success Rate: {trends['success_rate_trend']}")
            print(f"   Cache Hit Rate: {trends['cache_hit_trend']}")
            print(f"   Request Rate: {trends['request_rate']}")

        print("="*80)

    def export_metrics(self, filename: str = "monitoring_metrics.json"):
        """Export monitoring metrics to file."""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "current_metrics": self.get_current_metrics(),
            "performance_trends": self.get_performance_trends(),
            "metrics_history": self.metrics_history[-50:]  # Last 50 snapshots
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"📊 Metrics exported to {filename}")


# Global monitoring dashboard instance
monitoring_dashboard = MonitoringDashboard()


def record_request_metrics(cccd: str, status: str, duration_ms: float, cached: bool = False):
    """Record request metrics for monitoring."""
    monitoring_dashboard.record_request(cccd, status, duration_ms, cached)


def display_monitoring_dashboard():
    """Display the monitoring dashboard."""
    monitoring_dashboard.display_dashboard()


def export_monitoring_metrics(filename: str = "monitoring_metrics.json"):
    """Export monitoring metrics."""
    monitoring_dashboard.export_metrics(filename)


if __name__ == "__main__":
    # Example usage
    print("Starting monitoring dashboard...")

    # Simulate some requests
    monitoring_dashboard.record_request("025090000198", "found", 13728.84, False)
    monitoring_dashboard.record_request("036092002342", "found", 12500.50, True)
    monitoring_dashboard.record_request("019084000004", "error", 5000.00, False)

    # Display dashboard
    display_monitoring_dashboard()

    # Export metrics
    export_monitoring_metrics()