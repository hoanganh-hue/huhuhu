#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Reorganization Script
Tổ chức lại cấu trúc dự án để giải quyết xung đột và tối ưu hóa logic flow
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ProjectReorganizer:
    """Class để tổ chức lại dự án"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reorganization_log = []
        
    def reorganize(self) -> Dict[str, Any]:
        """Thực hiện tổ chức lại dự án"""
        print("🔄 Bắt đầu tổ chức lại cấu trúc dự án...")
        
        # Tạo các thư mục cần thiết
        self._create_essential_directories()
        
        # Di chuyển các file duplicate
        self._resolve_duplicate_files()
        
        # Tổ chức lại các module
        self._reorganize_modules()
        
        # Tạo file cấu hình tổng hợp
        self._create_unified_config()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'actions_performed': self.reorganization_log,
            'status': 'completed'
        }
    
    def _create_essential_directories(self):
        """Tạo các thư mục cần thiết"""
        essential_dirs = [
            'src',
            'src/core',
            'src/modules',
            'src/utils',
            'src/config',
            'tests',
            'docs',
            'scripts',
            'data',
            'logs',
            'output',
            'archive'
        ]
        
        for dir_path in essential_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                self.reorganization_log.append(f"Created directory: {dir_path}")
    
    def _resolve_duplicate_files(self):
        """Giải quyết các file duplicate"""
        print("🔧 Giải quyết file duplicates...")
        
        # Di chuyển các file từ submodules vào archive
        submodules_to_archive = [
            'API-thongtindoanhnghiep',
            'bhxh-tool-enhanced-python',
            'check-cccd'
        ]
        
        for submodule in submodules_to_archive:
            submodule_path = self.project_root / submodule
            if submodule_path.exists():
                archive_path = self.project_root / 'archive' / f'{submodule}_backup'
                if not archive_path.exists():
                    shutil.move(str(submodule_path), str(archive_path))
                    self.reorganization_log.append(f"Moved {submodule} to archive")
    
    def _reorganize_modules(self):
        """Tổ chức lại các module"""
        print("📦 Tổ chức lại modules...")
        
        # Di chuyển các module chính vào src/modules
        modules_to_move = [
            ('cccd', 'src/modules/cccd'),
            ('modules', 'src/modules/core'),
            ('utils', 'src/utils'),
            ('config', 'src/config')
        ]
        
        for source, target in modules_to_move:
            source_path = self.project_root / source
            target_path = self.project_root / target
            
            if source_path.exists() and source_path != target_path:
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.move(str(source_path), str(target_path))
                self.reorganization_log.append(f"Moved {source} to {target}")
    
    def _create_unified_config(self):
        """Tạo file cấu hình tổng hợp"""
        print("⚙️ Tạo cấu hình tổng hợp...")
        
        # Tạo file cấu hình tổng hợp
        unified_config = {
            "project_info": {
                "name": "BHXH Data Tools",
                "version": "2.0.0",
                "description": "Hệ thống tự động hóa tra cứu và tổng hợp thông tin BHXH",
                "last_updated": datetime.now().isoformat()
            },
            "structure": {
                "src": "Source code",
                "src/core": "Core functionality",
                "src/modules": "Feature modules",
                "src/utils": "Utility functions",
                "src/config": "Configuration files",
                "tests": "Test files",
                "docs": "Documentation",
                "scripts": "Automation scripts",
                "data": "Data files",
                "logs": "Log files",
                "output": "Output files",
                "archive": "Archived files"
            },
            "main_entry_points": [
                "main.py",
                "batch_check_cccd.py",
                "run_batch_check_fixed.py"
            ],
            "dependencies": {
                "requirements_file": "requirements.txt",
                "python_version": "3.8+"
            }
        }
        
        config_file = self.project_root / 'project_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(unified_config, f, indent=2, ensure_ascii=False)
        
        self.reorganization_log.append("Created unified project configuration")
    
    def create_cleanup_script(self):
        """Tạo script cleanup tự động"""
        cleanup_script = '''#!/bin/bash
# Auto cleanup script for BHXH Data Tools

echo "🧹 Starting automatic cleanup..."

# Remove Python cache files
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove temporary files
find . -name "*.tmp" -delete
find . -name "*.log" -not -path "./logs/*" -delete

# Remove system files
find . -name ".DS_Store" -delete

# Clean up empty directories
find . -type d -empty -delete 2>/dev/null || true

echo "✅ Cleanup completed!"
'''
        
        script_file = self.project_root / 'cleanup.sh'
        with open(script_file, 'w') as f:
            f.write(cleanup_script)
        
        # Make executable
        os.chmod(script_file, 0o755)
        self.reorganization_log.append("Created cleanup script")

def main():
    """Main function"""
    print("🚀 Starting Project Reorganization...")
    
    reorganizer = ProjectReorganizer()
    results = reorganizer.reorganize()
    reorganizer.create_cleanup_script()
    
    # In kết quả
    print("\n📋 REORGANIZATION SUMMARY:")
    print("=" * 50)
    for action in results['actions_performed']:
        print(f"✅ {action}")
    
    print(f"\n🕐 Completed at: {results['timestamp']}")
    print("🎉 Project reorganization completed successfully!")
    
    # Lưu log
    log_file = Path("reorganization_log.json")
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Reorganization log saved to: {log_file}")
    
    return True

if __name__ == "__main__":
    main()