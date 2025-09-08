#!/usr/bin/env python3
"""
Configuration Validation Script
Validate tất cả settings tối ưu để đảm bảo hệ thống chạy ổn định
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any

# Thêm src vào Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

class ConfigurationValidator:
    """Validate production configuration for stability and performance."""

    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []

    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🔍 VALIDATING PRODUCTION CONFIGURATION")
        print("=" * 50)

        # Core validations
        self._validate_environment_file()
        self._validate_dependencies()
        self._validate_database_connection()
        self._validate_redis_connection()
        self._validate_network_connectivity()
        self._validate_performance_settings()
        self._validate_security_settings()

        # Generate report
        report = self._generate_validation_report()
        self._save_validation_report(report)

        return report

    def _validate_environment_file(self):
        """Validate .env file exists and has required settings."""
        print("\n📄 Checking environment configuration...")

        env_file = project_root / ".env"
        if not env_file.exists():
            self.errors.append("❌ .env file not found")
            return

        # Check required environment variables
        required_vars = [
            'DATABASE_URL', 'REDIS_URL', 'API_KEY', 'SECRET_KEY',
            'REQUEST_TIMEOUT', 'MAX_RETRIES', 'RATE_LIMIT_PER_MINUTE'
        ]

        try:
            from dotenv import load_dotenv
            load_dotenv()

            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                self.errors.append(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            else:
                self.results.append("✅ All required environment variables configured")

        except ImportError:
            self.warnings.append("⚠️ python-dotenv not installed, skipping .env validation")

    def _validate_dependencies(self):
        """Validate all required dependencies are installed."""
        print("\n📦 Checking dependencies...")

        required_packages = [
            'fastapi', 'httpx', 'beautifulsoup4', 'redis', 'sqlalchemy',
            'pydantic', 'uvicorn', 'lxml'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.results.append(f"✅ {package} installed")
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.errors.append(f"❌ Missing dependencies: {', '.join(missing_packages)}")

    def _validate_database_connection(self):
        """Validate database connection."""
        print("\n🗄️ Checking database connection...")

        try:
            from check_cccd.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.fetchone():
                    self.results.append("✅ Database connection successful")
                else:
                    self.errors.append("❌ Database connection test failed")

        except Exception as e:
            self.errors.append(f"❌ Database connection error: {str(e)}")

    def _validate_redis_connection(self):
        """Validate Redis connection."""
        print("\n🔴 Checking Redis connection...")

        try:
            from check_cccd.cache_layer import get_cache_statistics
            stats = get_cache_statistics()

            if stats.get('redis_connected'):
                self.results.append("✅ Redis connection successful")
                self.results.append(f"   📊 Cached keys: {stats.get('cached_keys', 0)}")
            else:
                self.warnings.append("⚠️ Redis not connected - caching will be disabled")

        except Exception as e:
            self.warnings.append(f"⚠️ Redis connection error: {str(e)}")

    def _validate_network_connectivity(self):
        """Validate network connectivity to target website."""
        print("\n🌐 Checking network connectivity...")

        try:
            import httpx
            with httpx.Client(timeout=10.0) as client:
                response = client.get("https://masothue.com/", follow_redirects=True)
                if response.status_code == 200:
                    self.results.append("✅ Network connectivity to masothue.com OK")
                else:
                    self.warnings.append(f"⚠️ Unexpected response from masothue.com: {response.status_code}")

        except Exception as e:
            self.errors.append(f"❌ Network connectivity error: {str(e)}")

    def _validate_performance_settings(self):
        """Validate performance-related settings."""
        print("\n⚡ Checking performance settings...")

        # Check timeout settings
        timeout = float(os.getenv('REQUEST_TIMEOUT', 15.0))
        if timeout >= 20.0:
            self.results.append(f"✅ Request timeout optimized: {timeout}s")
        else:
            self.warnings.append(f"⚠️ Request timeout may be too low: {timeout}s (recommended: 20.0+)")

        # Check delay settings
        min_delay = float(os.getenv('MIN_DELAY_SECONDS', 1.0))
        max_delay = float(os.getenv('MAX_DELAY_SECONDS', 3.0))
        if min_delay >= 1.5 and max_delay >= 3.0:
            self.results.append(f"✅ Anti-bot delays optimized: {min_delay}-{max_delay}s")
        else:
            self.warnings.append(f"⚠️ Anti-bot delays may be too aggressive: {min_delay}-{max_delay}s")

        # Check rate limiting
        rate_limit = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
        if rate_limit <= 30:
            self.results.append(f"✅ Rate limiting configured: {rate_limit} req/min")
        else:
            self.warnings.append(f"⚠️ Rate limiting may be too high: {rate_limit} req/min")

    def _validate_security_settings(self):
        """Validate security-related settings."""
        print("\n🔒 Checking security settings...")

        # Check API key
        api_key = os.getenv('API_KEY', '')
        if len(api_key) >= 20 and api_key != 'your-api-key-change-in-production':
            self.results.append("✅ API key configured securely")
        else:
            self.errors.append("❌ API key not properly configured")

        # Check secret key
        secret_key = os.getenv('SECRET_KEY', '')
        if len(secret_key) >= 32 and secret_key != 'your-secret-key-change-in-production':
            self.results.append("✅ Secret key configured securely")
        else:
            self.errors.append("❌ Secret key not properly configured")

    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        total_checks = len(self.results) + len(self.errors) + len(self.warnings)
        success_rate = (len(self.results) / total_checks * 100) if total_checks > 0 else 0

        report = {
            "timestamp": "2025-09-07T22:00:00Z",
            "configuration_version": "v3.0.0-production",
            "validation_summary": {
                "total_checks": total_checks,
                "successful": len(self.results),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "success_rate": f"{success_rate:.1f}%"
            },
            "results": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations(),
            "system_readiness": self._calculate_readiness_score()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        if self.errors:
            recommendations.append("🔴 Fix all ERROR issues before production deployment")

        if self.warnings:
            recommendations.append("🟡 Review WARNING issues for optimal performance")

        if not any("Redis connection successful" in result for result in self.results):
            recommendations.append("💾 Consider enabling Redis for better caching performance")

        if not any("Request timeout optimized" in result for result in self.results):
            recommendations.append("⏱️ Increase REQUEST_TIMEOUT to 20.0+ seconds for stability")

        if not any("Anti-bot delays optimized" in result for result in self.results):
            recommendations.append("🤖 Increase MIN_DELAY_SECONDS to 1.5+ for better anti-bot protection")

        return recommendations

    def _calculate_readiness_score(self) -> Dict[str, Any]:
        """Calculate system readiness score."""
        base_score = 100

        # Deduct points for errors
        base_score -= len(self.errors) * 20

        # Deduct points for warnings
        base_score -= len(self.warnings) * 5

        # Ensure score is between 0-100
        readiness_score = max(0, min(100, base_score))

        if readiness_score >= 90:
            status = "🟢 PRODUCTION READY"
            description = "System is fully optimized and ready for production"
        elif readiness_score >= 75:
            status = "🟡 MOSTLY READY"
            description = "System is ready with minor optimizations needed"
        elif readiness_score >= 50:
            status = "🟠 NEEDS ATTENTION"
            description = "Several issues need to be addressed before production"
        else:
            status = "🔴 NOT READY"
            description = "Critical issues must be resolved before deployment"

        return {
            "score": readiness_score,
            "status": status,
            "description": description
        }

    def _save_validation_report(self, report: Dict[str, Any]):
        """Save validation report to file."""
        report_file = project_root / "validation_report.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Validation report saved to: {report_file}")


def main():
    """Main validation function."""
    validator = ConfigurationValidator()
    report = validator.validate_all()

    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    summary = report["validation_summary"]
    readiness = report["system_readiness"]

    print(f"Total Checks: {summary['total_checks']}")
    print(f"✅ Successful: {summary['successful']}")
    print(f"❌ Errors: {summary['errors']}")
    print(f"⚠️ Warnings: {summary['warnings']}")
    print(f"📈 Success Rate: {summary['success_rate']}")

    print(f"\n🏆 READINESS SCORE: {readiness['score']}/100")
    print(f"Status: {readiness['status']}")
    print(f"Description: {readiness['description']}")

    if report["errors"]:
        print("
🔴 ERRORS FOUND:"        for error in report["errors"]:
            print(f"   {error}")

    if report["warnings"]:
        print("
🟡 WARNINGS:"        for warning in report["warnings"]:
            print(f"   {warning}")

    if report["recommendations"]:
        print("
💡 RECOMMENDATIONS:"        for rec in report["recommendations"]:
            print(f"   {rec}")

    print("\n" + "=" * 60)

    if readiness["score"] >= 90:
        print("🎉 CONFIGURATION VALIDATION PASSED!")
        print("   System is ready for production deployment.")
        return True
    elif readiness["score"] >= 75:
        print("⚠️ CONFIGURATION MOSTLY VALID!")
        print("   Minor issues should be addressed before production.")
        return True
    else:
        print("❌ CONFIGURATION VALIDATION FAILED!")
        print("   Critical issues must be resolved before deployment.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)