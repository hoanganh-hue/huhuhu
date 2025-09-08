#!/usr/bin/env python3
"""
Database Migration Script
Tự động cập nhật và migrate database schema cho hệ thống Check CCCD
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import text

class DatabaseMigration:
    """Class để migrate và cập nhật database schema."""
    
    def __init__(self, db_path: str = None):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        
        # Thêm src vào Python path
        if str(self.src_path) not in sys.path:
            sys.path.insert(0, str(self.src_path))
        
        # Database path
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = self.project_root / "check_cccd.db"
        
        self.migration_log = self.project_root / "migration.log"
    
    def log(self, message: str, level: str = "INFO"):
        """Ghi log migration."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        print(log_message)
        
        with open(self.migration_log, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def get_current_schema(self) -> Dict[str, List[Dict]]:
        """Lấy schema hiện tại của database."""
        self.log("🔍 Lấy schema hiện tại...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lấy danh sách tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema = {}
            
            for table in tables:
                # Lấy thông tin columns
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                
                schema[table] = []
                for col in columns:
                    schema[table].append({
                        'cid': col[0],
                        'name': col[1],
                        'type': col[2],
                        'notnull': bool(col[3]),
                        'default_value': col[4],
                        'pk': bool(col[5])
                    })
            
            conn.close()
            self.log(f"✅ Đã lấy schema cho {len(tables)} tables")
            return schema
            
        except Exception as e:
            self.log(f"❌ Lỗi khi lấy schema: {e}", "ERROR")
            return {}
    
    def get_expected_schema(self) -> Dict[str, List[Dict]]:
        """Lấy schema mong đợi từ models."""
        self.log("📋 Lấy schema mong đợi từ models...")
        
        try:
            from check_cccd.models import CheckRequest, CheckMatch, ApiKey
            
            expected_schema = {
                'check_requests': [
                    {'name': 'id', 'type': 'TEXT', 'notnull': True, 'pk': True},
                    {'name': 'cccd', 'type': 'VARCHAR(20)', 'notnull': True, 'pk': False},
                    {'name': 'status', 'type': 'VARCHAR(20)', 'notnull': True, 'pk': False},
                    {'name': 'created_at', 'type': 'DATETIME', 'notnull': False, 'pk': False},
                    {'name': 'updated_at', 'type': 'DATETIME', 'notnull': False, 'pk': False},
                    {'name': 'error_message', 'type': 'TEXT', 'notnull': False, 'pk': False},
                ],
                'check_matches': [
                    {'name': 'id', 'type': 'TEXT', 'notnull': True, 'pk': True},
                    {'name': 'request_id', 'type': 'TEXT', 'notnull': True, 'pk': False},
                    {'name': 'type', 'type': 'VARCHAR(20)', 'notnull': True, 'pk': False},
                    {'name': 'name', 'type': 'VARCHAR(255)', 'notnull': False, 'pk': False},
                    {'name': 'tax_code', 'type': 'VARCHAR(20)', 'notnull': False, 'pk': False},
                    {'name': 'url', 'type': 'VARCHAR(500)', 'notnull': False, 'pk': False},
                    {'name': 'address', 'type': 'TEXT', 'notnull': False, 'pk': False},
                    {'name': 'role', 'type': 'VARCHAR(100)', 'notnull': False, 'pk': False},
                    {'name': 'raw_snippet', 'type': 'TEXT', 'notnull': False, 'pk': False},
                    {'name': 'created_at', 'type': 'DATETIME', 'notnull': False, 'pk': False},
                ],
                'api_keys': [
                    {'name': 'id', 'type': 'TEXT', 'notnull': True, 'pk': True},
                    {'name': 'key_hash', 'type': 'VARCHAR(255)', 'notnull': True, 'pk': False},
                    {'name': 'name', 'type': 'VARCHAR(100)', 'notnull': True, 'pk': False},
                    {'name': 'is_active', 'type': 'BOOLEAN', 'notnull': False, 'pk': False},
                    {'name': 'rate_limit_per_minute', 'type': 'INTEGER', 'notnull': False, 'pk': False},
                    {'name': 'created_at', 'type': 'DATETIME', 'notnull': False, 'pk': False},
                    {'name': 'last_used_at', 'type': 'DATETIME', 'notnull': False, 'pk': False},
                ]
            }
            
            self.log("✅ Đã lấy schema mong đợi")
            return expected_schema
            
        except Exception as e:
            self.log(f"❌ Lỗi khi lấy schema mong đợi: {e}", "ERROR")
            return {}
    
    def compare_schemas(self, current: Dict, expected: Dict) -> Dict[str, List[str]]:
        """So sánh schema hiện tại và mong đợi."""
        self.log("🔍 So sánh schemas...")
        
        differences = {
            'missing_tables': [],
            'missing_columns': {},
            'extra_columns': {},
            'type_mismatches': {}
        }
        
        # Kiểm tra tables thiếu
        for table_name in expected:
            if table_name not in current:
                differences['missing_tables'].append(table_name)
        
        # Kiểm tra columns cho từng table
        for table_name in expected:
            if table_name in current:
                expected_cols = {col['name']: col for col in expected[table_name]}
                current_cols = {col['name']: col for col in current[table_name]}
                
                # Columns thiếu
                missing_cols = []
                for col_name in expected_cols:
                    if col_name not in current_cols:
                        missing_cols.append(col_name)
                
                if missing_cols:
                    differences['missing_columns'][table_name] = missing_cols
                
                # Columns thừa
                extra_cols = []
                for col_name in current_cols:
                    if col_name not in expected_cols:
                        extra_cols.append(col_name)
                
                if extra_cols:
                    differences['extra_columns'][table_name] = extra_cols
                
                # Type mismatches
                type_mismatches = []
                for col_name in expected_cols:
                    if col_name in current_cols:
                        expected_type = expected_cols[col_name]['type']
                        current_type = current_cols[col_name]['type']
                        if expected_type != current_type:
                            type_mismatches.append({
                                'column': col_name,
                                'expected': expected_type,
                                'current': current_type
                            })
                
                if type_mismatches:
                    differences['type_mismatches'][table_name] = type_mismatches
        
        return differences
    
    def create_missing_tables(self, missing_tables: List[str]):
        """Tạo các tables thiếu."""
        self.log(f"📋 Tạo {len(missing_tables)} tables thiếu...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SQL để tạo tables
            create_statements = {
                'check_requests': '''
                    CREATE TABLE check_requests (
                        id TEXT PRIMARY KEY,
                        cccd VARCHAR(20) NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'queued',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        error_message TEXT
                    )
                ''',
                'check_matches': '''
                    CREATE TABLE check_matches (
                        id TEXT PRIMARY KEY,
                        request_id TEXT NOT NULL,
                        type VARCHAR(20) NOT NULL,
                        name VARCHAR(255),
                        tax_code VARCHAR(20),
                        url VARCHAR(500),
                        address TEXT,
                        role VARCHAR(100),
                        raw_snippet TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (request_id) REFERENCES check_requests (id)
                    )
                ''',
                'api_keys': '''
                    CREATE TABLE api_keys (
                        id TEXT PRIMARY KEY,
                        key_hash VARCHAR(255) NOT NULL UNIQUE,
                        name VARCHAR(100) NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        rate_limit_per_minute INTEGER DEFAULT 60,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_used_at DATETIME
                    )
                '''
            }
            
            for table in missing_tables:
                if table in create_statements:
                    cursor.execute(create_statements[table])
                    self.log(f"✅ Đã tạo table: {table}")
            
            conn.commit()
            conn.close()
            
            self.log("✅ Hoàn thành tạo tables")
            
        except Exception as e:
            self.log(f"❌ Lỗi khi tạo tables: {e}", "ERROR")
            raise
    
    def add_missing_columns(self, missing_columns: Dict[str, List[str]]):
        """Thêm các columns thiếu."""
        self.log("📝 Thêm columns thiếu...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Column definitions
            column_definitions = {
                'check_requests': {
                    'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'error_message': 'TEXT'
                },
                'check_matches': {
                    'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
                },
                'api_keys': {
                    'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'last_used_at': 'DATETIME'
                }
            }
            
            for table, columns in missing_columns.items():
                for column in columns:
                    if table in column_definitions and column in column_definitions[table]:
                        sql = f"ALTER TABLE {table} ADD COLUMN {column} {column_definitions[table][column]}"
                        cursor.execute(sql)
                        self.log(f"✅ Đã thêm column {table}.{column}")
                    else:
                        self.log(f"⚠️ Không tìm thấy definition cho {table}.{column}")
            
            conn.commit()
            conn.close()
            
            self.log("✅ Hoàn thành thêm columns")
            
        except Exception as e:
            self.log(f"❌ Lỗi khi thêm columns: {e}", "ERROR")
            raise
    
    def create_indexes(self):
        """Tạo indexes để tối ưu performance."""
        self.log("📊 Tạo database indexes...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_check_requests_cccd ON check_requests(cccd);",
                "CREATE INDEX IF NOT EXISTS idx_check_requests_status ON check_requests(status);",
                "CREATE INDEX IF NOT EXISTS idx_check_requests_created_at ON check_requests(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_check_matches_tax_code ON check_matches(tax_code);",
                "CREATE INDEX IF NOT EXISTS idx_check_matches_type ON check_matches(type);",
                "CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);",
                "CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            conn.close()
            
            self.log("✅ Hoàn thành tạo indexes")
            
        except Exception as e:
            self.log(f"❌ Lỗi khi tạo indexes: {e}", "ERROR")
            raise
    
    def backup_database(self):
        """Backup database trước khi migrate."""
        self.log("💾 Backup database...")
        
        try:
            backup_path = self.db_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
            
            # Copy database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            self.log(f"✅ Database đã được backup tại: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.log(f"❌ Lỗi khi backup database: {e}", "ERROR")
            return None
    
    def run_migration(self):
        """Chạy migration."""
        self.log("="*60)
        self.log("🔄 Database Migration - Check CCCD")
        self.log("="*60)
        
        # Backup database
        backup_path = self.backup_database()
        
        try:
            # Lấy schemas
            current_schema = self.get_current_schema()
            expected_schema = self.get_expected_schema()
            
            # So sánh schemas
            differences = self.compare_schemas(current_schema, expected_schema)
            
            # Hiển thị differences
            self.log("📊 Kết quả so sánh schema:")
            self.log(f"   - Tables thiếu: {len(differences['missing_tables'])}")
            self.log(f"   - Tables có columns thiếu: {len(differences['missing_columns'])}")
            self.log(f"   - Tables có columns thừa: {len(differences['extra_columns'])}")
            self.log(f"   - Tables có type mismatch: {len(differences['type_mismatches'])}")
            
            # Thực hiện migration
            if differences['missing_tables']:
                self.create_missing_tables(differences['missing_tables'])
            
            if differences['missing_columns']:
                self.add_missing_columns(differences['missing_columns'])
            
            # Tạo indexes
            self.create_indexes()
            
            # Kiểm tra lại schema
            final_schema = self.get_current_schema()
            self.log(f"✅ Migration hoàn tất. Database có {len(final_schema)} tables")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Migration thất bại: {e}", "ERROR")
            
            # Restore từ backup nếu có
            if backup_path and backup_path.exists():
                self.log("🔄 Đang restore từ backup...")
                import shutil
                shutil.copy2(backup_path, self.db_path)
                self.log("✅ Đã restore từ backup")
            
            return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration cho Check CCCD")
    parser.add_argument("--db-path", help="Đường dẫn database file")
    parser.add_argument("--backup-only", action="store_true", help="Chỉ backup database")
    
    args = parser.parse_args()
    
    migration = DatabaseMigration(args.db_path)
    
    if args.backup_only:
        backup_path = migration.backup_database()
        if backup_path:
            print(f"✅ Backup thành công tại: {backup_path}")
        else:
            print("❌ Backup thất bại")
            sys.exit(1)
    else:
        success = migration.run_migration()
        if success:
            print("\n✅ Migration hoàn tất thành công!")
        else:
            print("\n❌ Migration thất bại!")
            sys.exit(1)

if __name__ == "__main__":
    main()