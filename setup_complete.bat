@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    HỆ THỐNG TỰ ĐỘNG HÓA TRA CỨU THÔNG TIN BHXH              ║
echo ║                              SETUP COMPLETE v2.0.0                          ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Kiểm tra Python
echo 🔍 Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy!
    echo 💡 Vui lòng cài đặt Python 3.8+ từ: https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python đã được tìm thấy
python --version
echo.

REM Kiểm tra pip
echo 🔍 Kiểm tra pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip không được tìm thấy!
    echo 💡 Vui lòng cài đặt pip
    echo.
    pause
    exit /b 1
)

echo ✅ pip đã được tìm thấy
echo.

REM Cập nhật pip
echo 📦 Cập nhật pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️ Không thể cập nhật pip, tiếp tục với phiên bản hiện tại
)

echo.

REM Cài đặt dependencies
echo 📦 Cài đặt dependencies từ requirements.txt...
echo ⏳ Đang cài đặt, vui lòng chờ...
echo.

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Lỗi cài đặt dependencies!
    echo 💡 Thử chạy: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Cài đặt dependencies thành công!
echo.

REM Kiểm tra cài đặt
echo 🔍 Kiểm tra cài đặt modules...
python -c "import rich, click, requests, pandas, openpyxl, cachetools, fastapi, uvicorn, beautifulsoup4, lxml; print('✅ Tất cả modules chính đã được cài đặt!')"
if errorlevel 1 (
    echo ⚠️ Một số modules có thể chưa được cài đặt đầy đủ
    echo 💡 Thử chạy lại: pip install -r requirements.txt
)

echo.

REM Tạo file .env nếu chưa có
if not exist .env (
    echo 📝 Tạo file .env...
    echo # Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH > .env
    echo # Configuration File >> .env
    echo. >> .env
    echo # API Configuration >> .env
    echo CAPTCHA_API_KEY=your_2captcha_api_key_here >> .env
    echo. >> .env
    echo # CCCD Generation >> .env
    echo CCCD_COUNT=1000 >> .env
    echo CCCD_PROVINCE_CODE=001 >> .env
    echo CCCD_GENDER=Nam >> .env
    echo CCCD_BIRTH_YEAR_FROM=1990 >> .env
    echo CCCD_BIRTH_YEAR_TO=2000 >> .env
    echo. >> .env
    echo # System Configuration >> .env
    echo LOG_LEVEL=INFO >> .env
    echo DEBUG_MODE=false >> .env
    echo ✅ File .env đã được tạo
) else (
    echo ✅ File .env đã tồn tại
)

echo.

REM Tạo thư mục cần thiết
if not exist logs mkdir logs
if not exist output mkdir output
if not exist output\cccd mkdir output\cccd

echo ✅ Thư mục cần thiết đã được tạo
echo.

REM Kiểm tra cuối cùng
echo 🎯 Kiểm tra cuối cùng...
python test_imports.py
if errorlevel 1 (
    echo ⚠️ Có lỗi trong quá trình kiểm tra
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              🎉 SETUP HOÀN THÀNH! 🎉                        ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🚀 SẴN SÀNG CHẠY HỆ THỐNG:
echo.
echo    📱 GUI Interface (Khuyến nghị):
echo       python gui_main.py
echo.
echo    💻 Command Line:
echo       python main.py
echo.
echo    🖥️ Windows Scripts:
echo       run_windows.bat
echo       run_windows_enhanced.bat
echo.
echo 📋 CẤU HÌNH:
echo    - Chỉnh sửa file .env để cấu hình API keys và tham số
echo    - Đăng ký API key từ 2captcha.com cho module BHXH
echo.
echo 📚 TÀI LIỆU:
echo    - README.md: Tài liệu chính
echo    - INSTALLATION_QUICK.md: Hướng dẫn cài đặt nhanh
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
pause