#!/usr/bin/env python
"""
Root Wrapper for verify_recent_official_trends.py
"""
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cropmandi-ai", "backend"))
if not os.path.exists(backend_dir):
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.verify_recent_official_trends import run_verification

if __name__ == "__main__":
    run_verification()
