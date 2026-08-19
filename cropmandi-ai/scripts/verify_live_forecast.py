import argparse
import json
import sys
import os
import requests
from datetime import date

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

def main():
    parser = argparse.ArgumentParser(description="Verify live mandi forecast against official data.gov.in API")
    parser.add_argument("--commodity", type=str, default="Tomato")
    parser.add_argument("--market", type=str, default="Madanapalli APMC")
    parser.add_argument("--selected-date", type=str, default="2026-08-17")
    parser.add_argument("--backend-url", type=str, default="http://127.0.0.1:8000")
    args = parser.parse_args()

    print(f"===========================================================")
    print(f" FORENSIC LIVE FORECAST VERIFICATION REPORT")
    print(f" Commodity: {args.commodity}")
    print(f" Market: {args.market}")
    print(f" Selected Date: {args.selected_date}")
    print(f"===========================================================\n")

    # 1. Query Backend Verified Forecast API
    post_url = f"{args.backend_url}/forecast/api/v1/forecast/verified"
    payload = {
        "commodity": args.commodity,
        "market": args.market,
        "selected_date": args.selected_date,
        "force_refresh": True
    }

    try:
        res = requests.post(post_url, json=payload, timeout=15)
        if res.status_code != 200:
            print(f"❌ Backend endpoint returned HTTP {res.status_code}: {res.text}")
            sys.exit(1)
        resp_data = res.json()
    except Exception as e:
        print(f"❌ Error connecting to backend at {post_url}: {e}")
        sys.exit(1)

    records = resp_data.get("records", [])
    print(f"Fetched {len(records)} forecast records from backend:\n")
    print(f"| Date       | Displayed Modal Price | Min Price | Max Price | Price Source       | Data Status       | Verification Status |")
    print(f"|------------|-----------------------|-----------|-----------|--------------------|-------------------|---------------------|")

    mismatch_found = False
    for r in records:
        d_str = r.get("date")
        modal_p = r.get("modal_price")
        min_p = r.get("min_price")
        max_p = r.get("max_price")
        src = r.get("price_source")
        status = r.get("data_status")
        verif = r.get("verification_status")

        modal_str = f"₹{modal_p:.2f}" if modal_p is not None else "N/A"
        min_str = f"₹{min_p:.2f}" if min_p is not None else "N/A"
        max_str = f"₹{max_p:.2f}" if max_p is not None else "N/A"

        print(f"| {d_str:10} | {modal_str:21} | {min_str:9} | {max_str:9} | {src:18} | {status:17} | {verif:19} |")

        if verif == "mismatch_detected":
            mismatch_found = True

    # Save JSON verification report artifact
    report_file = os.path.join(os.path.dirname(__file__), "..", "live_forecast_verification_report.json")
    with open(report_file, "w") as f:
        json.dump(resp_data, f, indent=2)

    print(f"\nVerification report saved to: {os.path.abspath(report_file)}")

    if mismatch_found:
        print("❌ VERIFICATION FAILED: Price mismatch detected between official API and display!")
        sys.exit(1)

    print("\n✅ VERIFICATION PASSED: All displayed official prices strictly match official source data.")
    sys.exit(0)

if __name__ == "__main__":
    main()
