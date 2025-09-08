#!/usr/bin/env python3
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
