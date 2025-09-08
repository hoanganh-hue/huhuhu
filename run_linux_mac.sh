#!/bin/bash
# ================================================================================================
#  Hệ Thống Tự Động Hóa Tra Cứu và Tổng Hợp Thông Tin Tích Hợp
#  Linux/Mac Launcher Script
#  
#  Tác giả: MiniMax Agent
#  Ngày tạo: 06/09/2025
# ================================================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                HỆ THỐNG TỰ ĐỘNG HÓA TRA CỨU THÔNG TIN TÍCH HỢP               ║"
    echo "║                                v1.0.0                                       ║"
    echo "║                        Linux/Mac Launcher                                   ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check Python installation
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 không được tìm thấy!${NC}"
        echo -e "${YELLOW}💡 Cài đặt Python3:${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "   brew install python3"
        else
            echo "   sudo apt-get update && sudo apt-get install python3 python3-pip"
            echo "   hoặc: sudo yum install python3 python3-pip"
        fi
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python3 đã được cài đặt${NC}"
}

# Check tkinter (required for GUI)
check_tkinter() {
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  tkinter không có sẵn${NC}"
        echo -e "${YELLOW}💡 Cài đặt tkinter:${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "   tkinter thường có sẵn với Python trên macOS"
        else
            echo "   sudo apt-get install python3-tkinter"
            echo "   hoặc: sudo yum install tkinter"
        fi
        return 1
    fi
    return 0
}

# Setup configuration
setup_config() {
    if [[ ! -f ".env" ]]; then
        echo -e "${YELLOW}🔧 Lần đầu chạy - thiết lập cấu hình...${NC}"
        if [[ -f ".env.sample" ]]; then
            cp ".env.sample" ".env"
            echo -e "${GREEN}✅ Đã tạo file cấu hình mặc định${NC}"
        fi
    fi
}

# Install dependencies
install_deps() {
    echo -e "${BLUE}📦 Đang cài đặt dependencies...${NC}"
    echo ""
    
    echo -e "${CYAN}🔄 Đang chạy setup.py...${NC}"
    python3 setup.py
    
    echo ""
    echo -e "${CYAN}🔄 Đang cài đặt requirements...${NC}"
    python3 -m pip install -r requirements.txt
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Cài đặt hoàn tất!${NC}"
    else
        echo -e "${RED}❌ Có lỗi xảy ra trong quá trình cài đặt!${NC}"
        return 1
    fi
}

# Show menu
show_menu() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                           🚀 MENU LAUNCHER                                   ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}   1. 🎨 Chạy GUI (Giao diện đồ họa) - KHUYẾN NGHỊ${NC}"
    echo -e "${BLUE}   2. ⌨️  Chạy CLI (Giao diện dòng lệnh)${NC}"
    echo -e "${YELLOW}   3. 🔧 Kiểm tra hệ thống${NC}"
    echo -e "${PURPLE}   4. 📦 Cài đặt/Cập nhật dependencies${NC}"
    echo -e "${CYAN}   5. 📋 Xem hướng dẫn${NC}"
    echo -e "${RED}   6. 🚪 Thoát${NC}"
    echo ""
}

# Show help
show_help() {
    echo ""
    echo -e "${CYAN}📋 HƯỚNG DẪN SỬ DỤNG:${NC}"
    echo ""
    echo -e "${GREEN}🎯 KHUYẾN NGHỊ: Sử dụng GUI (lựa chọn 1) cho trải nghiệm tốt nhất${NC}"
    echo ""
    echo -e "${BLUE}📚 Chi tiết:${NC}"
    echo "   • GUI: Giao diện trực quan, dễ sử dụng, hiển thị progress real-time"
    echo "   • CLI: Giao diện dòng lệnh, phù hợp cho automation scripts"
    echo "   • Test: Kiểm tra tất cả modules có hoạt động đúng không"
    echo ""
    echo -e "${YELLOW}📋 Cấu hình:${NC}"
    echo "   • Chỉnh sửa file .env để thay đổi cấu hình"
    echo "   • CAPTCHA_API_KEY: Bắt buộc phải có (lấy từ 2captcha.com)"
    echo "   • CCCD_COUNT: Số lượng CCCD cần tạo (1-1000)"
    echo "   • CCCD_PROVINCE_CODE: Mã tỉnh/thành (001=HN, 079=HCM)"
    echo ""
    echo -e "${PURPLE}📁 Kết quả:${NC}"
    echo "   • File Excel: output/output.xlsx"
    echo "   • Log files: output/module_*.txt"
    echo "   • System logs: logs/system.log"
    echo ""
}

# Launch GUI
launch_gui() {
    echo ""
    echo -e "${GREEN}🎨 Đang khởi chạy GUI...${NC}"
    
    if ! check_tkinter; then
        echo -e "${RED}❌ Không thể chạy GUI do thiếu tkinter${NC}"
        echo -e "${YELLOW}💡 Hãy cài đặt tkinter hoặc sử dụng CLI${NC}"
        return 1
    fi
    
    python3 launcher.py gui
}

# Launch CLI
launch_cli() {
    echo ""
    echo -e "${BLUE}⌨️  Đang khởi chạy CLI...${NC}"
    python3 launcher.py cli
}

# Test system
test_system() {
    echo ""
    echo -e "${YELLOW}🔧 Đang kiểm tra hệ thống...${NC}"
    python3 launcher.py test
}

# Main menu loop
main_menu() {
    while true; do
        show_menu
        read -p "👉 Nhập lựa chọn của bạn (1-6): " choice
        
        case $choice in
            1)
                launch_gui
                if [[ $? -ne 0 ]]; then
                    echo ""
                    echo -e "${RED}❌ Lỗi khởi chạy GUI!${NC}"
                    read -p "Nhấn Enter để tiếp tục..."
                fi
                ;;
            2)
                launch_cli
                if [[ $? -ne 0 ]]; then
                    echo ""
                    echo -e "${RED}❌ Lỗi khởi chạy CLI!${NC}"
                    read -p "Nhấn Enter để tiếp tục..."
                fi
                ;;
            3)
                test_system
                read -p "Nhấn Enter để tiếp tục..."
                ;;
            4)
                install_deps
                read -p "Nhấn Enter để tiếp tục..."
                ;;
            5)
                show_help
                read -p "Nhấn Enter để tiếp tục..."
                ;;
            6)
                echo ""
                echo -e "${GREEN}👋 Cảm ơn bạn đã sử dụng hệ thống!${NC}"
                echo -e "${CYAN}📧 Liên hệ hỗ trợ: MiniMax Agent${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Lựa chọn không hợp lệ!${NC}"
                sleep 1
                ;;
        esac
        
        clear
    done
}

# Main execution
main() {
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Show banner
    clear
    show_banner
    
    # Check Python
    check_python
    
    # Setup configuration
    setup_config
    
    # Start main menu
    main_menu
}

# Trap Ctrl+C
trap 'echo -e "\n\n${YELLOW}⏹️  Đã dừng theo yêu cầu người dùng.${NC}"; exit 0' INT

# Error handling
error_exit() {
    echo -e "\n${RED}❌ Đã xảy ra lỗi!${NC}"
    echo -e "${YELLOW}💡 Hãy thử:${NC}"
    echo "   1. Kiểm tra quyền truy cập file"
    echo "   2. Kiểm tra kết nối internet"  
    echo "   3. Chạy 'python3 setup.py' để cài đặt lại"
    echo ""
    exit 1
}

# Set error trap
trap error_exit ERR

# Run main function
main "$@"
