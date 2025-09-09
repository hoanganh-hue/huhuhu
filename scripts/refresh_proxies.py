#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script refresh proxy pool
Tự động tìm và cập nhật danh sách proxy miễn phí
"""

import asyncio
import sys
import os
from pathlib import Path

# Thêm path để import module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from modules.core.module_7_advanced_api_client import ProxyManager

async def main():
    """Main function"""
    print("🔄 REFRESH PROXY POOL")
    print("=" * 50)
    
    # Tạo proxy manager
    proxy_manager = ProxyManager("config/proxies.txt")
    
    # Refresh proxy pool
    await proxy_manager.refresh_proxies(limit=100)
    
    print("✅ Hoàn thành refresh proxy pool!")

if __name__ == "__main__":
    asyncio.run(main())