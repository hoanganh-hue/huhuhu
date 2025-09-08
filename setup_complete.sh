#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    HỆ THỐNG TỰ ĐỘNG HÓA TRA CỨU THÔNG TIN BHXH              ║"
echo "║                              SETUP COMPLETE v2.0.0                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# Kiểm tra Python
echo -e "${BLUE}🔍 Kiểm tra Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 không được tìm thấy!${NC}"
    echo -e "${YELLOW}💡 Vui lòng cài đặt Python 3.8+ từ: https://python.org${NC}"
    echo
    exit 1
fi

echo -e "${GREEN}✅ Python3 đã được tìm thấy${NC}"
python3 --version
echo

# Kiểm tra pip
echo -e "${BLUE}🔍 Kiểm tra pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 không được tìm thấy!${NC}"
    echo -e "${YELLOW}💡 Vui lòng cài đặt pip3${NC}"
    echo
    exit 1
fi

echo -e "${GREEN}✅ pip3 đã được tìm thấy${NC}"
echo

# Cập nhật pip
echo -e "${BLUE}📦 Cập nhật pip...${NC}"
python3 -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Không thể cập nhật pip, tiếp tục với phiên bản hiện tại${NC}"
fi

echo

# Cài đặt dependencies
echo -e "${BLUE}📦 Cài đặt dependencies từ requirements.txt...${NC}"
echo -e "${YELLOW}⏳ Đang cài đặt, vui lòng chờ...${NC}"
echo

python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Lỗi cài đặt dependencies!${NC}"
    echo -e "${YELLOW}💡 Thử chạy: pip3 install -r requirements.txt${NC}"
    echo
    exit 1
fi

echo -e "${GREEN}✅ Cài đặt dependencies thành công!${NC}"
echo

# Kiểm tra cài đặt
echo -e "${BLUE}🔍 Kiểm tra cài đặt modules...${NC}"
python3 -c "import rich, click, requests, pandas, openpyxl, cachetools, fastapi, uvicorn, beautifulsoup4, lxml; print('✅ Tất cả modules chính đã được cài đặt!')"
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Một số modules có thể chưa được cài đặt đầy đủ${NC}"
    echo -e "${YELLOW}💡 Thử chạy lại: pip3 install -r requirements.txt${NC}"
fi

echo

# Tạo file .env nếu chưa có
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Tạo file .env...${NC}"
    cat > .env << EOF
# Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH
# Configuration File

# API Configuration
CAPTCHA_API_KEY=your_2captcha_api_key_here

# CCCD Generation
CCCD_COUNT=1000
CCCD_PROVINCE_CODE=001
CCCD_GENDER=Nam
CCCD_BIRTH_YEAR_FROM=1990
CCCD_BIRTH_YEAR_TO=2000

# System Configuration
LOG_LEVEL=INFO
DEBUG_MODE=false
EOF
    echo -e "${GREEN}✅ File .env đã được tạo${NC}"
else
    echo -e "${GREEN}✅ File .env đã tồn tại${NC}"
fi

echo

# Tạo thư mục cần thiết
mkdir -p logs
mkdir -p output
mkdir -p output/cccd

echo -e "${GREEN}✅ Thư mục cần thiết đã được tạo${NC}"
echo

# Kiểm tra cuối cùng
echo -e "${BLUE}🎯 Kiểm tra cuối cùng...${NC}"
python3 test_imports.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Có lỗi trong quá trình kiểm tra${NC}"
fi

echo
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                              🎉 SETUP HOÀN THÀNH! 🎉                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo
echo -e "${GREEN}🚀 SẴN SÀNG CHẠY HỆ THỐNG:${NC}"
echo
echo -e "${CYAN}   📱 GUI Interface (Khuyến nghị):${NC}"
echo -e "      python3 gui_main.py"
echo
echo -e "${CYAN}   💻 Command Line:${NC}"
echo -e "      python3 main.py"
echo
echo -e "${CYAN}   🖥️ Linux/Mac Scripts:${NC}"
echo -e "      ./run_linux_mac.sh"
echo
echo -e "${YELLOW}📋 CẤU HÌNH:${NC}"
echo -e "   - Chỉnh sửa file .env để cấu hình API keys và tham số"
echo -e "   - Đăng ký API key từ 2captcha.com cho module BHXH"
echo
echo -e "${YELLOW}📚 TÀI LIỆU:${NC}"
echo -e "   - README.md: Tài liệu chính"
echo -e "   - INSTALLATION_QUICK.md: Hướng dẫn cài đặt nhanh"
echo
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo