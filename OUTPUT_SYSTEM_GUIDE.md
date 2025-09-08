# Hướng Dẫn Sử Dụng Hệ Thống Output Tự Động

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
report_content = "# My Report\n\nContent here..."
report_path = om.save_report(report_content, "My Report")
```

### 3. Lưu Dữ Liệu
```python
data = {"key": "value", "timestamp": "2025-09-08"}
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
print(f"Total files: {summary['total_files']}")
print(f"Total size: {summary['total_size']} bytes")

# Cleanup file cũ (giữ lại 30 ngày)
om.cleanup_old_files(days=30)
```

---
*Generated: 2025-09-08 10:44:57*
