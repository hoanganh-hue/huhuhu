#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Output System - Cài đặt hệ thống output tự động
Cập nhật tất cả script để sử dụng OutputManager
"""

import os
import re
from pathlib import Path
from datetime import datetime

class OutputSystemSetup:
    """Class để cài đặt hệ thống output"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.output_manager_path = self.project_root / "src" / "utils" / "output_manager.py"
        self.updated_files = []
    
    def setup_output_system(self):
        """Cài đặt hệ thống output"""
        print("🔧 Setting up automatic output system...")
        
        # Tạo OutputManager nếu chưa có
        self._ensure_output_manager()
        
        # Cập nhật các script chính
        self._update_main_scripts()
        
        # Tạo script wrapper
        self._create_script_wrapper()
        
        # Test hệ thống
        self._test_output_system()
        
        print(f"✅ Output system setup completed! Updated {len(self.updated_files)} files.")
        return self.updated_files
    
    def _ensure_output_manager(self):
        """Đảm bảo OutputManager tồn tại"""
        if not self.output_manager_path.exists():
            print("❌ OutputManager not found! Please run the setup first.")
            return False
        
        print("✅ OutputManager found")
        return True
    
    def _update_main_scripts(self):
        """Cập nhật các script chính"""
        main_scripts = [
            "main.py",
            "batch_check_cccd.py", 
            "run_batch_check_fixed.py",
            "process_cccd_batch.py",
            "automated_cccd_workflow.py"
        ]
        
        for script_name in main_scripts:
            script_path = self.project_root / script_name
            if script_path.exists():
                self._update_script_file(script_path)
    
    def _update_script_file(self, script_path: Path):
        """Cập nhật một script file"""
        print(f"📝 Updating {script_path.name}...")
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Thêm import OutputManager
            if "from src.utils.output_manager import" not in content:
                import_line = "from src.utils.output_manager import get_output_manager, save_to_output, save_report, save_data\n"
                
                # Tìm vị trí thích hợp để thêm import
                lines = content.split('\n')
                import_end = 0
                
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_end = i + 1
                
                lines.insert(import_end, import_line)
                content = '\n'.join(lines)
            
            # Thay thế các pattern lưu file
            content = self._replace_file_save_patterns(content)
            
            # Ghi lại file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.updated_files.append(str(script_path))
            print(f"✅ Updated {script_path.name}")
            
        except Exception as e:
            print(f"❌ Error updating {script_path.name}: {e}")
    
    def _replace_file_save_patterns(self, content: str) -> str:
        """Thay thế các pattern lưu file"""
        patterns = [
            # Pattern: with open('filename', 'w') as f: f.write(content)
            (r"with open\(['\"]([^'\"]+)['\"], ['\"]w['\"]\) as f:\s*f\.write\(([^)]+)\)", 
             r"save_to_output(\2, '\1')"),
            
            # Pattern: json.dump(data, open('filename', 'w'))
            (r"json\.dump\(([^,]+),\s*open\(['\"]([^'\"]+)['\"], ['\"]w['\"]\)\)",
             r"save_data(\1, '\2')"),
            
            # Pattern: df.to_excel('filename')
            (r"df\.to_excel\(['\"]([^'\"]+)['\"]\)",
             r"copy_to_output(df.to_excel('\1'), '\1', 'data')"),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _create_script_wrapper(self):
        """Tạo script wrapper để tự động redirect output"""
        wrapper_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Wrapper - Tự động redirect tất cả output vào thư mục output/
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Thêm src vào Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from src.utils.output_manager import get_output_manager
    
    # Khởi tạo OutputManager
    output_manager = get_output_manager(project_root)
    
    print("🔧 Output system initialized!")
    print(f"📁 All outputs will be saved to: {output_manager.output_root}")
    
    # Redirect stdout để log vào file
    class OutputLogger:
        def __init__(self, original_stdout):
            self.original_stdout = original_stdout
            self.log_content = []
        
        def write(self, message):
            self.original_stdout.write(message)
            self.log_content.append(message)
        
        def flush(self):
            self.original_stdout.flush()
        
        def save_log(self):
            if self.log_content:
                log_content = ''.join(self.log_content)
                output_manager.save_log(log_content, "script_execution")
    
    # Wrap stdout
    logger = OutputLogger(sys.stdout)
    sys.stdout = logger
    
    # Import và chạy script gốc
    if len(sys.argv) > 1:
        script_name = sys.argv[1]
        script_args = sys.argv[2:]
        
        # Thay đổi sys.argv để script gốc nhận đúng arguments
        sys.argv = [script_name] + script_args
        
        # Import và chạy script
        if script_name == "main.py":
            from main import main
            main()
        elif script_name == "batch_check_cccd.py":
            from batch_check_cccd import main
            main()
        elif script_name == "run_batch_check_fixed.py":
            from run_batch_check_fixed import main
            main()
        else:
            print(f"❌ Unknown script: {script_name}")
    
    # Lưu log
    logger.save_log()
    
except ImportError as e:
    print(f"❌ Error importing OutputManager: {e}")
    print("💡 Please ensure src/utils/output_manager.py exists")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
'''
        
        wrapper_path = self.project_root / "run_with_output.py"
        with open(wrapper_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
        
        # Make executable
        os.chmod(wrapper_path, 0o755)
        
        print(f"✅ Created script wrapper: {wrapper_path}")
    
    def _test_output_system(self):
        """Test hệ thống output"""
        print("🧪 Testing output system...")
        
        try:
            import sys
            # Test OutputManager
            sys.path.insert(0, str(self.project_root / "src"))
            from src.utils.output_manager import get_output_manager
            
            om = get_output_manager(self.project_root)
            
            # Test save report
            test_report = f"""# Test Report
            
This is a test report generated at {datetime.now()}

## Test Results
- ✅ OutputManager working correctly
- ✅ File paths configured properly
- ✅ Directory structure created

## Next Steps
All future outputs will be automatically saved to the output/ directory.
"""
            
            report_path = om.save_report(test_report, "Output System Test")
            print(f"✅ Test report saved: {report_path}")
            
            # Test save data
            test_data = {
                "test": "output_system",
                "timestamp": datetime.now().isoformat(),
                "status": "working",
                "output_directory": str(om.output_root)
            }
            
            data_path = om.save_data(test_data, "test_output_system.json")
            print(f"✅ Test data saved: {data_path}")
            
            # Test summary
            summary = om.get_output_summary()
            print(f"✅ Output summary: {summary['total_files']} files in output directory")
            
            print("🎉 Output system test completed successfully!")
            
        except Exception as e:
            print(f"❌ Output system test failed: {e}")
    
    def create_usage_guide(self):
        """Tạo hướng dẫn sử dụng"""
        guide_content = f"""# Hướng Dẫn Sử Dụng Hệ Thống Output Tự Động

## Tổng Quan
Tất cả file kết quả của dự án sẽ được tự động lưu vào thư mục `output/` với cấu trúc có tổ chức.

## Cấu Trúc Thư Mục Output
```
output/
├── reports/     # Báo cáo (.md, .txt, .html, .pdf)
├── data/        # Dữ liệu (.xlsx, .csv, .json, .xml)
├── logs/        # Log files (.log, .out, .err)
├── exports/     # File export (.zip, .tar, .gz)
├── backups/     # Backup files (.bak, .backup, .old)
└── temp/        # File tạm thời
```

## Cách Sử Dụng

### 1. Import OutputManager
```python
from src.utils.output_manager import get_output_manager, save_to_output, save_report, save_data

# Khởi tạo
om = get_output_manager()
```

### 2. Lưu Báo Cáo
```python
report_content = "# My Report\\n\\nContent here..."
report_path = om.save_report(report_content, "My Report")
```

### 3. Lưu Dữ Liệu
```python
data = {{"key": "value", "timestamp": "2025-09-08"}}
data_path = om.save_data(data, "my_data.json")
```

### 4. Copy File Vào Output
```python
source_file = "input.xlsx"
output_path = om.copy_file(source_file, "processed_data.xlsx", "data")
```

### 5. Tạo Backup
```python
backup_path = om.create_backup("important_file.py", "important_file")
```

## Chạy Script Với Output Tự Động
```bash
# Sử dụng wrapper script
python3 run_with_output.py main.py
python3 run_with_output.py batch_check_cccd.py
```

## Tính Năng Tự Động
- ✅ Tự động tạo timestamp cho file names
- ✅ Tự động xác định loại file dựa trên extension
- ✅ Tự động tạo thư mục nếu chưa tồn tại
- ✅ Tự động cleanup file cũ (có thể cấu hình)
- ✅ Tự động log tất cả hoạt động

## Cấu Hình
Tất cả cấu hình được quản lý trong `src/config/settings.py`:
- `output_path`: Đường dẫn thư mục output
- `logs_path`: Đường dẫn thư mục logs
- Các cấu hình khác...

## Monitoring
```python
# Xem tóm tắt output
summary = om.get_output_summary()
print(f"Total files: {{summary['total_files']}}")
print(f"Total size: {{summary['total_size']}} bytes")

# Cleanup file cũ (giữ lại 30 ngày)
om.cleanup_old_files(days=30)
```

---
*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        guide_path = self.project_root / "OUTPUT_SYSTEM_GUIDE.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"✅ Created usage guide: {guide_path}")

def main():
    """Main function"""
    print("🚀 Setting up automatic output system...")
    
    setup = OutputSystemSetup()
    updated_files = setup.setup_output_system()
    setup.create_usage_guide()
    
    print("\n📋 SETUP SUMMARY:")
    print("=" * 50)
    print(f"✅ Updated {len(updated_files)} files")
    print("✅ Created script wrapper: run_with_output.py")
    print("✅ Created usage guide: OUTPUT_SYSTEM_GUIDE.md")
    print("✅ Output directory structure created")
    print("✅ All outputs will be saved to output/ directory")
    
    print("\n🎉 Setup completed successfully!")
    print("💡 Use 'python3 run_with_output.py <script_name>' to run scripts with automatic output")

if __name__ == "__main__":
    main()