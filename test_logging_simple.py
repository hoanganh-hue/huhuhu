#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple AI-CODE LOGGING Test
"""

import sys
import json
import time
import logging.config
import yaml
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("🚀 Simple AI-CODE LOGGING Test")
    print("=" * 40)

    # Initialize logging
    LOG_ROOT = Path("/Users/nguyenduchung1993/Downloads/tools-data-bhxh/logs")
    LOG_CFG = LOG_ROOT / "logging.yaml"

    try:
        with open(LOG_CFG, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        logging.config.dictConfig(cfg)
        print("✅ Logging configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load logging: {e}")
        return 1

    # Test logging
    try:
        from utils.log_helper import get_logger, add_extra, set_correlation

        log = get_logger("test.simple", step="test_logging")
        set_correlation(log, "test-123")
        add_extra(log, test_value="hello", count=42)

        log.info("Test log message")
        log.warning("Test warning message")
        log.error("Test error message")

        print("✅ Test logs generated")

        # Check log file
        time.sleep(0.5)
        workflow_log = LOG_ROOT / "workflow.log"

        if workflow_log.exists():
            with open(workflow_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"✅ Found {len(lines)} log entries")
                    last_entry = json.loads(lines[-1].strip())
                    print(f"✅ Last log keys: {list(last_entry.keys())}")

                    # Check required fields
                    required = ["timestamp", "level", "module", "message", "request_id"]
                    missing = [f for f in required if f not in last_entry]
                    if not missing:
                        print("✅ All required fields present")
                        return 0
                    else:
                        print(f"❌ Missing fields: {missing}")
                        return 1
                else:
                    print("❌ No log entries found")
                    return 1
        else:
            print("❌ Log file not created")
            return 1

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())