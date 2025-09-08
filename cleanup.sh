#!/bin/bash
# Auto cleanup script for BHXH Data Tools

echo "🧹 Starting automatic cleanup..."

# Remove Python cache files
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove temporary files
find . -name "*.tmp" -delete
find . -name "*.log" -not -path "./logs/*" -delete

# Remove system files
find . -name ".DS_Store" -delete

# Clean up empty directories
find . -type d -empty -delete 2>/dev/null || true

echo "✅ Cleanup completed!"
