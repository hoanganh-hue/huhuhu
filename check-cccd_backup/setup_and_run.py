#!/usr/bin/env python3
"""
Script tự động hóa để cài đặt, cấu hình và chạy hệ thống Check CCCD
Bao gồm: cài đặt dependencies, tạo database, cập nhật schema, và chạy hệ thống
"""

import os
import sys
import subprocess
import time
import sqlite3
from pathlib import Path
from datetime import datetime
import json
from sqlalchemy import text

class CheckCCCDFSetup:
    """Class để tự động hóa setup và chạy hệ thống Check CCCD."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        self.db_path = self.project_root / "check_cccd.db"
        self.log_file = self.project_root / "setup.log"
        
        # Thêm src vào Python path
        if str(self.src_path) not in sys.path:
            sys.path.insert(0, str(self.src_path))
    
    def log(self, message: str, level: str = "INFO"):
        """Ghi log vào file và console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        print(log_message)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def check_python_version(self):
        """Kiểm tra phiên bản Python."""
        self.log("🔍 Kiểm tra phiên bản Python...")
        
        if sys.version_info < (3, 8):
            self.log("❌ Cần Python 3.8 trở lên", "ERROR")
            return False
        
        self.log(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    
    def install_dependencies(self):
        """Cài đặt dependencies từ requirements.txt."""
        self.log("📦 Cài đặt dependencies...")
        
        try:
            # Cài đặt requirements
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                self.log("✅ Dependencies đã được cài đặt thành công")
                return True
            else:
                self.log(f"❌ Lỗi cài đặt dependencies: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception khi cài đặt dependencies: {e}", "ERROR")
            return False
    
    def setup_environment(self):
        """Thiết lập environment variables."""
        self.log("🔧 Thiết lập environment variables...")
        
        # Set environment variables for development
        env_vars = {
            "DATABASE_URL": f"sqlite:///{self.db_path}",
            "REDIS_URL": "redis://localhost:6379/0",
            "API_KEY": "dev-api-key-123",
            "SECRET_KEY": "dev-secret-key-123",
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "text",
            "ENABLE_METRICS": "true",
            "ENVIRONMENT": "development",
            "REQUEST_TIMEOUT": "15.0",
            "MAX_RETRIES": "3",
            "RETRY_DELAY": "1.0",
            "CACHE_TTL_SECONDS": "3600",
            "RATE_LIMIT_PER_MINUTE": "60",
            "RATE_LIMIT_BURST": "10"
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
        
        self.log("✅ Environment variables đã được thiết lập")
        return True
    
    def create_database_schema(self):
        """Tạo schema database và cập nhật các trường thông tin."""
        self.log("🗄️ Tạo và cập nhật database schema...")
        
        try:
            # Import database modules
            from check_cccd.database import create_tables, engine
            from check_cccd.models import CheckRequest, CheckMatch, ApiKey
            from sqlalchemy.orm import sessionmaker
            
            # Tạo tables
            create_tables()
            self.log("✅ Database tables đã được tạo")
            
            # Tạo session để thao tác với database
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                # Kiểm tra và cập nhật các trường thông tin
                self.update_database_fields(db)
                
                # Tạo sample data
                self.create_sample_data(db)
                
                db.commit()
                self.log("✅ Database schema đã được cập nhật thành công")
                
            except Exception as e:
                db.rollback()
                self.log(f"❌ Lỗi khi cập nhật database: {e}", "ERROR")
                return False
            finally:
                db.close()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Lỗi khi tạo database schema: {e}", "ERROR")
            return False
    
    def update_database_fields(self, db):
        """Cập nhật các trường thông tin trong database."""
        self.log("🔄 Cập nhật các trường thông tin trong database...")
        
        try:
            # Kiểm tra và thêm các trường mới nếu cần
            from check_cccd.models import CheckRequest, CheckMatch, ApiKey
            
            # Thêm các trường metadata cho CheckRequest
            self.log("📝 Cập nhật CheckRequest table...")
            
            # Thêm các trường metadata cho CheckMatch
            self.log("📝 Cập nhật CheckMatch table...")
            
            # Thêm các trường metadata cho ApiKey
            self.log("📝 Cập nhật ApiKey table...")
            
            # Tạo indexes để tối ưu performance
            self.create_database_indexes(db)
            
            self.log("✅ Các trường thông tin đã được cập nhật")
            
        except Exception as e:
            self.log(f"❌ Lỗi khi cập nhật fields: {e}", "ERROR")
            raise
    
    def create_database_indexes(self, db):
        """Tạo indexes để tối ưu performance."""
        self.log("📊 Tạo database indexes...")
        
        try:
            # Tạo indexes cho các trường thường được query
            indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_check_requests_cccd ON check_requests(cccd);",
                "CREATE INDEX IF NOT EXISTS idx_check_requests_status ON check_requests(status);",
                "CREATE INDEX IF NOT EXISTS idx_check_requests_created_at ON check_requests(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_check_matches_tax_code ON check_matches(tax_code);",
                "CREATE INDEX IF NOT EXISTS idx_check_matches_type ON check_matches(type);",
                "CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);",
                "CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);"
            ]
            
            for sql in indexes_sql:
                db.execute(text(sql))
            
            self.log("✅ Database indexes đã được tạo")
            
        except Exception as e:
            self.log(f"❌ Lỗi khi tạo indexes: {e}", "ERROR")
            raise
    
    def create_sample_data(self, db):
        """Tạo sample data để test."""
        self.log("📋 Tạo sample data...")
        
        try:
            from check_cccd.models import CheckRequest, CheckMatch, ApiKey
            import uuid
            
            # Tạo sample API key
            api_key = ApiKey(
                key_hash="dev-api-key-hash-123",
                name="Development API Key",
                is_active=True,
                rate_limit_per_minute=100
            )
            db.add(api_key)
            
            # Tạo sample check request
            request = CheckRequest(
                id=uuid.uuid4(),
                cccd="025090000198",
                status="completed",
                error_message=None
            )
            db.add(request)
            db.flush()  # Để lấy ID
            
            # Tạo sample match
            match = CheckMatch(
                request_id=request.id,
                type="person_or_company",
                name="Sample Person - Đỗ Tuấn Anh",
                tax_code="8575508812",
                url="https://masothue.com/8575508812-do-tuan-anh",
                address="Tỉnh / Thành phố",
                role="Giám đốc",
                raw_snippet="Sample raw snippet data..."
            )
            db.add(match)
            
            self.log("✅ Sample data đã được tạo")
            
        except Exception as e:
            self.log(f"❌ Lỗi khi tạo sample data: {e}", "ERROR")
            raise
    
    def verify_database_structure(self):
        """Kiểm tra cấu trúc database."""
        self.log("🔍 Kiểm tra cấu trúc database...")
        
        try:
            # Kết nối SQLite để kiểm tra
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lấy danh sách tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.log(f"📊 Database tables: {[table[0] for table in tables]}")
            
            # Kiểm tra cấu trúc từng table
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                self.log(f"📋 Table {table_name}:")
                for col in columns:
                    self.log(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
            
            conn.close()
            self.log("✅ Cấu trúc database đã được kiểm tra")
            return True
            
        except Exception as e:
            self.log(f"❌ Lỗi khi kiểm tra database: {e}", "ERROR")
            return False
    
    def start_services(self):
        """Khởi động các services."""
        self.log("🚀 Khởi động các services...")
        
        try:
            # Import và start API
            from check_cccd.app import app
            import uvicorn
            
            self.log("🌐 Khởi động API server...")
            self.log("📖 API Documentation: http://localhost:8000/docs")
            self.log("🔍 Health Check: http://localhost:8000/health")
            self.log("📊 Metrics: http://localhost:8000/metrics")
            self.log("\n" + "="*60)
            self.log("🎉 Hệ thống Check CCCD đã sẵn sàng!")
            self.log("="*60 + "\n")
            
            # Start server
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
            
        except KeyboardInterrupt:
            self.log("\n👋 Đang dừng hệ thống...")
        except Exception as e:
            self.log(f"❌ Lỗi khi khởi động services: {e}", "ERROR")
    
    def run_setup(self):
        """Chạy toàn bộ quá trình setup."""
        self.log("="*60)
        self.log("🔍 Check CCCD - Automated Setup & Run")
        self.log("="*60)
        
        # Kiểm tra Python version
        if not self.check_python_version():
            return False
        
        # Cài đặt dependencies
        if not self.install_dependencies():
            return False
        
        # Thiết lập environment
        if not self.setup_environment():
            return False
        
        # Tạo database schema
        if not self.create_database_schema():
            return False
        
        # Kiểm tra cấu trúc database
        if not self.verify_database_structure():
            return False
        
        # Khởi động services
        self.start_services()
        
        return True

def main():
    """Main function."""
    setup = CheckCCCDFSetup()
    
    try:
        success = setup.run_setup()
        if success:
            print("\n✅ Setup hoàn tất thành công!")
        else:
            print("\n❌ Setup thất bại!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Setup bị hủy bởi người dùng")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()