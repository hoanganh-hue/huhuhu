@echo off
REM ================================================================================================
REM  Hệ Thống Tự Động Hóa Tra Cứu và Tổng Hợp Thông Tin Tích Hợp
REM  Enhanced Windows Auto-Install & Run Script
REM  
REM  Tác giả: MiniMax Agent
REM  Ngày tạo: 07/09/2025
REM  Phiên bản: 2.0.0 - PRODUCTION READY
REM ================================================================================================

setlocal enabledelayedexpansion

REM Project Configuration
set PROJECT_NAME=Anh Em New World - Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH
set PROJECT_VERSION=2.0.0
set PROJECT_DIR=%~dp0
set LOG_FILE=%PROJECT_DIR%install.log
set VENV_DIR=%PROJECT_DIR%venv
set PYTHON_MIN_VERSION=3.8

REM Colors and Status
set INFO_PREFIX=[INFO]
set ERROR_PREFIX=[ERROR]
set WARNING_PREFIX=[WARNING]
set SUCCESS_PREFIX=[SUCCESS]

REM Logging Functions
:log
echo %INFO_PREFIX% [%date% %time%] %~1
echo %INFO_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:error
echo %ERROR_PREFIX% [%date% %time%] %~1
echo %ERROR_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:warning
echo %WARNING_PREFIX% [%date% %time%] %~1
echo %WARNING_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:success
echo %SUCCESS_PREFIX% [%date% %time%] %~1
echo %SUCCESS_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

REM Print Banner
:print_banner
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    ANH EM NEW WORLD - HỆ THỐNG TỰ ĐỘNG HÓA                  ║
echo ║                        TRA CỨU THÔNG TIN TÍCH HỢP                           ║
echo ║                                v%PROJECT_VERSION%                                       ║
echo ║                        Enhanced Windows Auto-Install ^& Run                     ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
goto :eof

REM Check System Requirements
:check_requirements
call :log "🔍 Kiểm tra system requirements..."

REM Check Windows Version
ver | find "Windows" >nul
if %errorlevel% neq 0 (
    call :error "❌ Script này chỉ hỗ trợ Windows"
    exit /b 1
)

REM Check Administrator Rights
net session >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Đang chạy với quyền Administrator"
) else (
    call :warning "⚠️ Không có quyền Administrator - một số tính năng có thể bị hạn chế"
)

REM Check Internet Connection
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Kết nối internet OK"
) else (
    call :warning "⚠️ Không có kết nối internet - một số tính năng có thể không hoạt động"
)

call :success "✅ System requirements check completed"
goto :eof

REM Check and Install Python
:check_python
call :log "🐍 Kiểm tra và cài đặt Python..."

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    REM Get Python version
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    call :log "✅ Python đã được cài đặt: %PYTHON_VERSION%"
    
    REM Check version compatibility
    echo %PYTHON_VERSION% | findstr /r "^3\.[8-9]\|^3\.1[0-9]" >nul
    if %errorlevel% equ 0 (
        call :success "✅ Python version tương thích"
    ) else (
        call :warning "⚠️ Python version có thể không tương thích (yêu cầu 3.8+)"
    )
) else (
    call :warning "❌ Python không được tìm thấy"
    call :log "💡 Hướng dẫn cài đặt Python:"
    call :log "   1. Truy cập: https://www.python.org/downloads/"
    call :log "   2. Tải Python 3.8+ cho Windows"
    call :log "   3. Chạy installer với 'Add to PATH' được chọn"
    call :log "   4. Restart Command Prompt và chạy lại script"
    
    REM Try to open Python download page
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check pip
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ pip đã được cài đặt"
) else (
    call :error "❌ pip không được tìm thấy"
    call :log "💡 Cài đặt pip: python -m ensurepip --upgrade"
    python -m ensurepip --upgrade
    if %errorlevel% equ 0 (
        call :success "✅ pip đã được cài đặt"
    ) else (
        call :error "❌ Không thể cài đặt pip"
        exit /b 1
    )
)

goto :eof

REM Create Virtual Environment
:create_venv
call :log "🐍 Tạo virtual environment..."

if exist "%VENV_DIR%" (
    call :log "✅ Virtual environment đã tồn tại"
) else (
    call :log "🔄 Đang tạo virtual environment..."
    python -m venv "%VENV_DIR%"
    if %errorlevel% equ 0 (
        call :success "✅ Virtual environment đã được tạo"
    ) else (
        call :error "❌ Không thể tạo virtual environment"
        exit /b 1
    )
)

REM Activate virtual environment
call :log "🔄 Kích hoạt virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% equ 0 (
    call :success "✅ Virtual environment đã được kích hoạt"
) else (
    call :error "❌ Không thể kích hoạt virtual environment"
    exit /b 1
)

goto :eof

REM Install Dependencies
:install_dependencies
call :log "📦 Cài đặt dependencies..."

REM Upgrade pip
call :log "🔄 Cập nhật pip..."
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    call :warning "⚠️ Không thể cập nhật pip"
)

REM Check requirements.txt
if not exist "requirements.txt" (
    call :error "❌ Không tìm thấy requirements.txt"
    exit /b 1
)

REM Install requirements with error handling
call :log "🔄 Cài đặt requirements từ requirements.txt..."
pip install -r requirements.txt
if %errorlevel% equ 0 (
    call :success "✅ Dependencies đã được cài đặt"
) else (
    call :error "❌ Lỗi khi cài đặt dependencies"
    call :log "💡 Thử cài đặt từng package riêng lẻ..."
    
    REM Try installing critical packages individually
    pip install openpyxl pandas requests python-dotenv
    pip install fastapi uvicorn httpx beautifulsoup4
    pip install tenacity psutil tqdm
    pip install numpy pillow opencv-python
    
    if %errorlevel% equ 0 (
        call :success "✅ Critical dependencies đã được cài đặt"
    ) else (
        call :error "❌ Không thể cài đặt dependencies"
        exit /b 1
    )
)

goto :eof

REM Setup Environment
:setup_environment
call :log "🔧 Thiết lập environment..."

REM Create .env file if not exists
if not exist ".env" (
    call :log "🔄 Tạo file .env..."
    (
        echo # Anh Em New World - Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH
        echo # Configuration File
        echo.
        echo # CAPTCHA Configuration
        echo CAPTCHA_API_KEY=your_2captcha_api_key_here
        echo CAPTCHA_WEBSITE_KEY=6Lcey5QUAAAAADcB0m7xYLj8W8HHi8ur4JQrTCUY
        echo CAPTCHA_WEBSITE_URL=https://baohiemxahoi.gov.vn
        echo.
        echo # CCCD Configuration
        echo CCCD_COUNT=100
        echo CCCD_PROVINCE_CODE=001
        echo CCCD_GENDER=
        echo CCCD_BIRTH_YEAR_FROM=1990
        echo CCCD_BIRTH_YEAR_TO=2000
        echo.
        echo # API Configuration
        echo CHECK_CCCD_API_URL=http://localhost:8000
        echo CHECK_CCCD_API_KEY=dev-api-key-123
        echo BHXH_API_URL=https://baohiemxahoi.gov.vn/UserControls/BHXH/BaoHiemYTe/HienThiHoGiaDinh/pListKoOTP.aspx
        echo.
        echo # System Configuration
        echo LOG_LEVEL=INFO
        echo DEBUG_MODE=false
        echo OUTPUT_PATH=output
        echo EXCEL_OUTPUT_FILE=output.xlsx
        echo.
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///./tools_data_bhxh.db
        echo REDIS_URL=redis://localhost:6379/0
        echo.
        echo # Security
        echo SECRET_KEY=your_secret_key_here
        echo API_KEY=your_api_key_here
    ) > .env
    call :success "✅ File .env đã được tạo"
) else (
    call :log "✅ File .env đã tồn tại"
)

REM Create necessary directories
if not exist "output" mkdir output
if not exist "logs" mkdir logs
if not exist "data" mkdir data

call :success "✅ Environment setup completed"
goto :eof

REM Run Tests
:run_tests
call :log "🧪 Chạy tests để kiểm tra tính toàn vẹn..."

REM Test CCCD Generator
if exist "cccd\test_cccd_generator.py" (
    call :log "🔄 Testing CCCD Generator..."
    python cccd\test_cccd_generator.py
    if %errorlevel% equ 0 (
        call :success "✅ CCCD Generator test passed"
    ) else (
        call :warning "⚠️ CCCD Generator test failed"
    )
)

REM Test main imports
call :log "🔄 Testing main imports..."
python -c "from main import IntegratedLookupSystem; print('✅ Main imports successful')"
if %errorlevel% equ 0 (
    call :success "✅ Main imports test passed"
) else (
    call :warning "⚠️ Main imports test failed"
)

REM Test GUI imports
call :log "🔄 Testing GUI imports..."
python -c "import tkinter; print('✅ GUI imports successful')"
if %errorlevel% equ 0 (
    call :success "✅ GUI imports test passed"
) else (
    call :warning "⚠️ GUI imports test failed"
)

call :success "✅ Tests completed"
goto :eof

REM Start Application
:start_application
call :log "🚀 Khởi động ứng dụng..."

REM Check if GUI is available
python -c "import tkinter" >nul 2>&1
if %errorlevel% equ 0 (
    call :log "🎨 Khởi động GUI application..."
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                           🎨 GUI APPLICATION                                  ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo 📖 Hướng dẫn sử dụng GUI:
    echo    • Cấu hình CAPTCHA API Key trong tab Configuration
    echo    • Chọn số lượng CCCD và tỉnh/thành phố
    echo    • Nhấn "BẮT ĐẦU WORKFLOW" để chạy tự động
    echo    • Theo dõi progress trong tab Progress
    echo    • Xem kết quả trong tab Results
    echo.
    echo 🛑 Để dừng ứng dụng, đóng cửa sổ GUI hoặc nhấn Ctrl+C
    echo.
    
    python gui_main.py
    if %errorlevel% equ 0 (
        call :success "✅ GUI application completed successfully"
    ) else (
        call :error "❌ GUI application failed"
    )
) else (
    call :log "⌨️ Khởi động CLI application..."
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                           ⌨️ CLI APPLICATION                                   ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo 📖 Hướng dẫn sử dụng CLI:
    echo    • Cấu hình trong file .env trước khi chạy
    echo    • Đảm bảo CAPTCHA_API_KEY đã được thiết lập
    echo    • Workflow sẽ chạy tự động 6 bước
    echo    • Kết quả sẽ được lưu trong thư mục output/
    echo.
    echo 🛑 Để dừng ứng dụng, nhấn Ctrl+C
    echo.
    
    python main.py
    if %errorlevel% equ 0 (
        call :success "✅ CLI application completed successfully"
    ) else (
        call :error "❌ CLI application failed"
    )
)

goto :eof

REM Docker Integration
:check_docker
call :log "🐳 Kiểm tra Docker..."

docker --version >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Docker đã được cài đặt"
    
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        call :log "✅ Docker Compose đã được cài đặt"
        
        if exist "docker-compose.yml" (
            call :log "🔄 Docker Compose configuration found"
            set /p docker_choice="🐳 Bạn có muốn sử dụng Docker? (y/N): "
            if /i "%docker_choice%"=="y" (
                call :log "🚀 Khởi động với Docker Compose..."
                docker-compose up -d
                if %errorlevel% equ 0 (
                    call :success "✅ Docker services started successfully"
                    call :log "📖 Services available at:"
                    call :log "   • Main App: http://localhost:8080"
                    call :log "   • Check CCCD API: http://localhost:8000"
                    call :log "   • API Docs: http://localhost:8000/docs"
                ) else (
                    call :error "❌ Docker services failed to start"
                )
            )
        )
    ) else (
        call :warning "⚠️ Docker Compose không được tìm thấy"
    )
) else (
    call :log "ℹ️ Docker không được cài đặt - sử dụng Python native"
)

goto :eof

REM Main Installation Function
:main
call :print_banner

REM Run installation steps
call :check_requirements
if %errorlevel% neq 0 exit /b 1

call :check_python
if %errorlevel% neq 0 exit /b 1

call :create_venv
if %errorlevel% neq 0 exit /b 1

call :install_dependencies
if %errorlevel% neq 0 exit /b 1

call :setup_environment
if %errorlevel% neq 0 exit /b 1

call :run_tests
if %errorlevel% neq 0 exit /b 1

call :check_docker

call :success "🎉 Installation hoàn tất thành công!"
call :log "🚀 Đang khởi động hệ thống..."

call :start_application
goto :eof

REM Command Line Arguments Handling
if "%1"=="install" (
    call :print_banner
    call :check_requirements
    call :check_python
    call :create_venv
    call :install_dependencies
    call :setup_environment
    call :run_tests
    call :success "🎉 Installation hoàn tất! Chạy 'run_windows.bat run' để khởi động"
    goto :eof
)

if "%1"=="run" (
    call :log "🚀 Khởi động hệ thống..."
    call "%VENV_DIR%\Scripts\activate.bat"
    call :start_application
    goto :eof
)

if "%1"=="test" (
    call :log "🧪 Chạy tests..."
    call "%VENV_DIR%\Scripts\activate.bat"
    call :run_tests
    goto :eof
)

if "%1"=="gui" (
    call :log "🎨 Khởi động GUI..."
    call "%VENV_DIR%\Scripts\activate.bat"
    python gui_main.py
    goto :eof
)

if "%1"=="cli" (
    call :log "⌨️ Khởi động CLI..."
    call "%VENV_DIR%\Scripts\activate.bat"
    python main.py
    goto :eof
)

if "%1"=="docker" (
    call :log "🐳 Khởi động Docker services..."
    docker-compose up -d
    goto :eof
)

if "%1"=="clean" (
    call :log "🧹 Cleaning up..."
    if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
    if exist "*.db" del "*.db"
    if exist "*.log" del "*.log"
    if exist "__pycache__" rmdir /s /q "__pycache__"
    call :success "✅ Cleanup hoàn tất"
    goto :eof
)

if "%1"=="help" (
    call :print_banner
    echo.
    echo 📋 HƯỚNG DẪN SỬ DỤNG:
    echo.
    echo 🎯 CÁCH SỬ DỤNG:
    echo    • Chạy không tham số: Tự động cài đặt và khởi động
    echo    • run_windows.bat install: Chỉ cài đặt dependencies
    echo    • run_windows.bat run: Khởi động ứng dụng
    echo    • run_windows.bat gui: Khởi động GUI
    echo    • run_windows.bat cli: Khởi động CLI
    echo    • run_windows.bat docker: Khởi động Docker services
    echo    • run_windows.bat test: Chạy tests
    echo    • run_windows.bat clean: Dọn dẹp files
    echo.
    echo 📚 CẤU HÌNH:
    echo    • Chỉnh sửa file .env để thay đổi cấu hình
    echo    • CAPTCHA_API_KEY: Bắt buộc (lấy từ 2captcha.com)
    echo    • CCCD_COUNT: Số lượng CCCD (1-1000)
    echo    • CCCD_PROVINCE_CODE: Mã tỉnh/thành (001=HN, 079=HCM)
    echo.
    echo 📁 KẾT QUẢ:
    echo    • File Excel: output/output.xlsx
    echo    • Log files: output/module_*.txt
    echo    • System logs: logs/system.log
    echo    • Install logs: install.log
    echo.
    pause
    goto :eof
)

REM Default: run main installation
call :main