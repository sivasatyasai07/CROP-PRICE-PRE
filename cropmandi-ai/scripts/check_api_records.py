import sys
import os
import argparse
import requests
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import DATA_GOV_API_KEY, DATA_GOV_BASE_URL, DATA_GOV_RESOURCE_ID

def main():
    parser = argparse.ArgumentParser(description="Check raw records directly from data.gov.in AGMARKNET API")
    parser.add_argument("--commodity", type=str, default="Tomato")
    parser.add_argument("--market", type=str, default="Madanapalli APMC")
    args = parser.parse_args()

    res_id = DATA_GOV_RESOURCE_ID.lstrip('/')
    if res_id.startswith("resource/"):
        res_id = res_id[len("resource/"):]
    safe_url = f"{DATA_GOV_BASE_URL.rstrip('/')}/resource/{res_id}"
    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "limit": 50,
        "filters[commodity]": args.commodity
    }

    print(f"Querying data.gov.in API for commodity '{args.commodity}'...")
    resp = requests.get(safe_url, params=params, timeout=10)
    print(f"HTTP Status: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        records = data.get("records", [])
        print(f"Total records received: {len(records)}")
        for idx, r in enumerate(records[:10]):
            mkt = r.get("market") or r.get("Market")
            comm = r.get("commodity") or r.get("Commodity")
            dt = r.get("arrival_date") or r.get("Arrival_Date") or r.get("date")
            modal = r.get("modal_price") or r.get("Modal_Price") or r.get("Modal Price")
            print(f"[{idx+1}] Market: {mkt} | Commodity: {comm} | Date: {dt} | Modal Price: Rs. {modal}")

if __name__ == "__main__":
    main()
