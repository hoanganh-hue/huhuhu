#!/usr/bin/env python3
"""
Development runner for Check CCCD API.
This script sets up the development environment and runs the API server.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up development environment."""
    print("🚀 Setting up Check CCCD development environment...")
    
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set environment variables for development
    os.environ.setdefault("DATABASE_URL", "sqlite:///./check_cccd_dev.db")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("API_KEY", "dev-api-key-123")
    os.environ.setdefault("SECRET_KEY", "dev-secret-key-123")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("LOG_FORMAT", "text")
    os.environ.setdefault("ENABLE_METRICS", "true")
    os.environ.setdefault("ENVIRONMENT", "development")
    
    print("✅ Environment variables set")

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import httpx
        import beautifulsoup4
        import lxml
        print("✅ Core dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def create_database():
    """Create database tables."""
    print("🗄️ Creating database tables...")
    
    try:
        from check_cccd.database import create_tables
        create_tables()
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️ Database setup warning: {e}")
        print("Continuing with in-memory storage...")

def run_server():
    """Run the development server."""
    print("🌐 Starting development server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "check_cccd.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main function."""
    print("=" * 60)
    print("🔍 Check CCCD API - Development Server")
    print("=" * 60)
    
    if not check_dependencies():
        sys.exit(1)
    
    setup_environment()
    create_database()
    run_server()

if __name__ == "__main__":
    main()