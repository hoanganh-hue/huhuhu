@echo off
echo 🚀 Cài đặt dependencies cho Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH
echo ================================================================================

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy. Vui lòng cài đặt Python 3.8+ trước.
    pause
    exit /b 1
)

echo ✅ Python đã được tìm thấy
echo.

REM Cài đặt dependencies
echo 📦 Đang cài đặt dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Lỗi cài đặt dependencies
    pause
    exit /b 1
)

echo ✅ Cài đặt dependencies thành công!
echo.

REM Kiểm tra cài đặt
echo 🔍 Kiểm tra cài đặt...
python install_dependencies.py

if errorlevel 1 (
    echo ❌ Có lỗi trong quá trình kiểm tra
    pause
    exit /b 1
)

echo.
echo 🎉 Hoàn thành cài đặt!
echo.
echo 🚀 Sẵn sàng chạy hệ thống:
echo    python main.py          # Command line
echo    python gui_main.py      # GUI interface
echo    run_windows.bat         # Windows script
echo.
pause