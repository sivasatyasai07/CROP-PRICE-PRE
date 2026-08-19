import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("cropmandi-ai/backend"))
sys.path.insert(0, os.path.abspath("."))

from app.services.official_market_service import build_data_gov_url, fetch_with_pagination, parse_api_date
from app.config import settings


def main():
    parser = argparse.ArgumentParser(description="Safely inspect data.gov.in resource response without exposing keys")
    parser.add_argument("--state", default="Andhra Pradesh", help="State name")
    parser.add_argument("--district", default="Annamayya", help="District name")
    parser.add_argument("--market", default="Madanapalli", help="Market name")
    parser.add_argument("--commodity", default="Tomato", help="Commodity name")
    parser.add_argument("--date", default="2026-08-19", help="Arrival date (YYYY-MM-DD or DD/MM/YYYY)")
    args = parser.parse_args()

    date_parsed = parse_api_date(args.date)
    formatted_date_filter = date_parsed.strftime("%d/%m/%Y") if date_parsed else args.date

    endpoint_url, params, safe_log_url = build_data_gov_url(
        state=args.state,
        district=args.district,
        market=args.market,
        commodity=args.commodity,
        arrival_date=formatted_date_filter,
        limit=100
    )

    print("=" * 60)
    print("DATA.GOV.IN RESOURCE INSPECTION REPORT")
    print("=" * 60)
    print(f"Resource ID: {settings.DATA_GOV_RESOURCE_ID}")
    print(f"Sanitized Query Endpoint: {safe_log_url}")
    print(f"Requested State: {args.state}")
    print(f"Requested District: {args.district}")
    print(f"Requested Market: {args.market}")
    print(f"Requested Commodity: {args.commodity}")
    print(f"Requested Arrival Date Filter: {formatted_date_filter}")
    print("-" * 60)

    http_status, records, error = fetch_with_pagination(endpoint_url, params, safe_log_url, max_pages=1)

    print(f"HTTP Status: {http_status}")
    print(f"Response Format: {settings.DATA_GOV_FORMAT or 'json'}")
    print(f"Record Count Returned: {len(records)}")

    actual_fields = []
    latest_date = None
    exact_matches = []

    if records:
        sample = records[0]
        actual_fields = list(sample.keys())
        print(f"Actual API Field Names: {actual_fields}")

        all_dates = []
        for r in records:
            raw_d = r.get("Arrival_Date") or r.get("arrival_date") or r.get("Date") or r.get("date")
            d_obj = parse_api_date(raw_d)
            if d_obj:
                all_dates.append(d_obj)
                if date_parsed and d_obj == date_parsed:
                    exact_matches.append(r)

        if all_dates:
            latest_date = max(all_dates)
            print(f"Latest Returned Date in Sample: {latest_date}")

        print(f"Exact Matching Records for {args.date}: {len(exact_matches)}")
        if exact_matches:
            print("Matching Record Excerpt:")
            print(json.dumps(exact_matches[0], indent=2))
    else:
        print("Result: No records returned for exact filter criteria.")

    if error:
        print(f"API Warning/Error Message: {error}")

    print("=" * 60)


if __name__ == "__main__":
    main()
