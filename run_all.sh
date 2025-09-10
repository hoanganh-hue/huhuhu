#!/bin/bash

# Script chạy toàn bộ pipeline
echo "🚀 BẮT ĐẦU PIPELINE"
echo "=================="

# Tạo thư mục logs nếu chưa có
mkdir -p logs

# Chạy kiểm tra dữ liệu thực
echo "🔍 Kiểm tra dữ liệu thực..."
python3 scripts/check_real_data.py

# Chạy Feature-1: Tạo CCCD
echo "🔢 Feature-1: Tạo CCCD..."
python3 main.py

# Chạy Feature-6: Export Excel
echo "📊 Feature-6: Export Excel..."
python3 scripts/export_excel.py output.xlsx

echo "✅ PIPELINE HOÀN THÀNH"
echo "======================"
