import os
import re
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
API_BASE_URL = "http://127.0.0.1:8000"

SUSPICIOUS_PATTERNS = [
    r'const\s+modalPrice\s*=\s*\d+',
    r'const\s+predictedPrice\s*=\s*\d+',
    r'const\s+demoForecast\s*=',
    r'const\s+samplePrice\s*=',
    r'fallbackPrice\s*=\s*\d+',
    r'All_Type_of_Report'
]


def scan_source_files() -> List[Dict[str, Any]]:
    findings = []
    scan_dirs = [
        os.path.join(PROJECT_ROOT, "frontend", "src"),
        os.path.join(BASE_DIR, "app"),
    ]

    for s_dir in scan_dirs:
        if not os.path.exists(s_dir):
            continue
        for root, _, files in os.walk(s_dir):
            for file in files:
                if file.endswith((".ts", ".tsx", ".py", ".js")):
                    fpath = os.path.join(root, file)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            for pat in SUSPICIOUS_PATTERNS:
                                matches = re.finditer(pat, content)
                                for m in matches:
                                    findings.append({
                                        "file": os.path.relpath(fpath, PROJECT_ROOT),
                                        "pattern": pat,
                                        "match": m.group(0)
                                    })
                    except Exception:
                        pass
    return findings


def verify_runtime_endpoint():
    url = f"{API_BASE_URL}/forecast/verified"
    req_body = {
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": "2026-08-14",
        "force_refresh": True,
        "request_id": f"scan_{datetime.now().timestamp()}"
    }

    res = requests.post(url, json=req_body, timeout=20)
    if res.status_code != 200:
        return False, f"HTTP {res.status_code}: {res.text}"

    data = res.json()
    records = data.get("records", [])
    if not records:
        return False, "No records returned from verified forecast"

    for r in records:
        src = r.get("price_source")
        if src not in ("official_api", "official_csv", "predicted", "unavailable"):
            return False, f"Unknown price_source: {src}"
        if r.get("is_observed") and r.get("is_predicted"):
            return False, "Conflict: record is both observed and predicted"
        if not r.get("lookup_trace"):
            return False, "Missing lookup_trace in record"

    return True, "Verified forecast endpoint returned valid runtime data"


def main():
    print("==================================================")
    print("  CROPMANDI AI — NO-HARDCODED-PRICES AUDIT")
    print("==================================================")

    findings = scan_source_files()
    if findings:
        print(f"FAILED: Found {len(findings)} suspicious hardcoded price patterns or old CSV references:")
        for f in findings:
            print(f"  - {f['file']}: {f['match']}")
        sys.exit(1)
    else:
        print("Source code scan for hardcoded prices: PASSED (0 suspicious patterns found)")

    # Test runtime endpoint
    passed, msg = verify_runtime_endpoint()
    print(f"Runtime Forecast Endpoint Check: {'PASSED' if passed else 'FAILED'} — {msg}")

    if not passed:
        sys.exit(1)

    print("\n==================================================")
    print("  NO-HARDCODING AUDIT: ALL CHECKS PASSED")
    print("==================================================")


if __name__ == "__main__":
    main()
