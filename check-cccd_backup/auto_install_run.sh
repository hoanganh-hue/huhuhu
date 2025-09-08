#!/bin/bash

# Auto Install & Run Script cho Check CCCD
# Script tự động cài đặt dependencies, setup database và chạy hệ thống

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project info
PROJECT_NAME="Check CCCD API"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/install.log"

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "🔍 $PROJECT_NAME - Auto Install & Run"
    echo "============================================================"
    echo -e "${NC}"
}

# Check system requirements
check_requirements() {
    log "🔍 Kiểm tra system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log "✅ Python3 found: $PYTHON_VERSION"
    else
        error "❌ Python3 không được tìm thấy. Vui lòng cài đặt Python 3.8+"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        log "✅ pip3 found"
    else
        error "❌ pip3 không được tìm thấy. Vui lòng cài đặt pip"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ]; then
        error "❌ Không tìm thấy requirements.txt. Vui lòng chạy script từ thư mục project"
        exit 1
    fi
    
    log "✅ System requirements OK"
}

# Create virtual environment
create_venv() {
    log "🐍 Tạo virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log "✅ Virtual environment đã được tạo"
    else
        log "✅ Virtual environment đã tồn tại"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    log "✅ Virtual environment đã được kích hoạt"
}

# Install dependencies
install_dependencies() {
    log "📦 Cài đặt dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    log "✅ Dependencies đã được cài đặt"
}

# Setup environment
setup_environment() {
    log "🔧 Thiết lập environment..."
    
    # Create .env file if not exists
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./check_cccd.db

# Redis Configuration (optional for development)
REDIS_URL=redis://localhost:6379/0

# API Security
API_KEY=dev-api-key-123
SECRET_KEY=dev-secret-key-123

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Scraping Configuration
REQUEST_TIMEOUT=15.0
MAX_RETRIES=3
RETRY_DELAY=1.0

# Cache Configuration
CACHE_TTL_SECONDS=3600

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=text

# Monitoring Configuration
ENABLE_METRICS=true

# Development/Production Mode
ENVIRONMENT=development
EOF
        log "✅ File .env đã được tạo"
    else
        log "✅ File .env đã tồn tại"
    fi
}

# Setup database
setup_database() {
    log "🗄️ Thiết lập database..."
    
    # Run database migration
    python database_migration.py
    
    if [ $? -eq 0 ]; then
        log "✅ Database đã được thiết lập"
    else
        error "❌ Lỗi khi thiết lập database"
        exit 1
    fi
}

# Test installation
test_installation() {
    log "🧪 Kiểm tra installation..."
    
    # Test imports
    python -c "
import sys
sys.path.insert(0, 'src')
try:
    from check_cccd.app import app
    from check_cccd.scraper import scrape_cccd_sync
    from check_cccd.database import create_tables
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log "✅ Installation test passed"
    else
        error "❌ Installation test failed"
        exit 1
    fi
}

# Start services
start_services() {
    log "🚀 Khởi động services..."
    
    info "📖 API Documentation sẽ có tại: http://localhost:8000/docs"
    info "🔍 Health Check sẽ có tại: http://localhost:8000/health"
    info "📊 Metrics sẽ có tại: http://localhost:8000/metrics"
    info ""
    info "🎯 Để test API, chạy: python test_api.py"
    info "🛑 Để dừng server, nhấn Ctrl+C"
    info ""
    
    # Start the application
    python setup_and_run.py
}

# Cleanup function
cleanup() {
    log "🧹 Cleaning up..."
    # Add any cleanup tasks here
}

# Main installation function
main() {
    print_banner
    
    # Trap to ensure cleanup on exit
    trap cleanup EXIT
    
    # Run installation steps
    check_requirements
    create_venv
    install_dependencies
    setup_environment
    setup_database
    test_installation
    
    log "🎉 Installation hoàn tất thành công!"
    log "🚀 Đang khởi động hệ thống..."
    
    start_services
}

# Handle command line arguments
case "${1:-}" in
    "install")
        print_banner
        check_requirements
        create_venv
        install_dependencies
        setup_environment
        setup_database
        test_installation
        log "🎉 Installation hoàn tất! Chạy './auto_install_run.sh run' để khởi động"
        ;;
    "run")
        log "🚀 Khởi động hệ thống..."
        source venv/bin/activate
        start_services
        ;;
    "test")
        log "🧪 Chạy tests..."
        source venv/bin/activate
        python test_api.py
        ;;
    "migrate")
        log "🔄 Chạy database migration..."
        source venv/bin/activate
        python database_migration.py
        ;;
    "clean")
        log "🧹 Cleaning up..."
        rm -rf venv
        rm -f *.db
        rm -f *.log
        log "✅ Cleanup hoàn tất"
        ;;
    *)
        main
        ;;
esac