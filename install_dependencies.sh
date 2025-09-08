#!/bin/bash

echo "🚀 Cài đặt dependencies cho Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH"
echo "================================================================================"

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy. Vui lòng cài đặt Python 3.8+ trước."
    exit 1
fi

echo "✅ Python3 đã được tìm thấy"
echo

# Cài đặt dependencies
echo "📦 Đang cài đặt dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Lỗi cài đặt dependencies"
    exit 1
fi

echo "✅ Cài đặt dependencies thành công!"
echo

# Kiểm tra cài đặt
echo "🔍 Kiểm tra cài đặt..."
python3 install_dependencies.py

if [ $? -ne 0 ]; then
    echo "❌ Có lỗi trong quá trình kiểm tra"
    exit 1
fi

echo
echo "🎉 Hoàn thành cài đặt!"
echo
echo "🚀 Sẵn sàng chạy hệ thống:"
echo "   python3 main.py         # Command line"
echo "   python3 gui_main.py     # GUI interface"
echo "   ./run_linux_mac.sh      # Linux/Mac script"
echo