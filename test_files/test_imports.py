#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra import modules
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🔍 Kiểm tra import modules...")
print("=" * 50)

# Test imports
modules_to_test = [
    ('rich', 'rich'),
    ('click', 'click'),
    ('requests', 'requests'),
    ('pandas', 'pandas'),
    ('openpyxl', 'openpyxl'),
    ('cachetools', 'cachetools'),
    ('tkinter', 'tkinter'),
    ('json', 'json'),
    ('pathlib', 'pathlib'),
    ('datetime', 'datetime'),
    ('threading', 'threading'),
    ('queue', 'queue'),
]

success_count = 0
total_count = len(modules_to_test)

for module_name, import_name in modules_to_test:
    try:
        __import__(import_name)
        print(f"✅ {module_name}")
        success_count += 1
    except ImportError as e:
        print(f"❌ {module_name}: {e}")

print("=" * 50)
print(f"📊 Kết quả: {success_count}/{total_count} modules thành công")

if success_count == total_count:
    print("🎉 Tất cả modules đã được cài đặt thành công!")
    print("\n🚀 Sẵn sàng chạy hệ thống:")
    print("   python main.py          # Command line")
    print("   python gui_main.py      # GUI interface")
else:
    print(f"⚠️ Còn thiếu {total_count - success_count} modules")
    print("\n💡 Chạy lệnh sau để cài đặt:")
    print("   pip install -r requirements.txt")