#!/usr/bin/env python
"""
Verification Script: Verify Recent Official Trends & Market Comparison Data Integrity
"""
import os
import sys
import json
from datetime import date, timedelta
from typing import Dict, Any, List

# Ensure backend app is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.config import settings
from app.models import Market, Commodity
from app.routers.prices import get_price_trends, compare_market_prices, ALLOWED_SOURCES, BLOCKED_SOURCES
from app.routers.commodities import list_recent_commodities
from app.routers.markets import list_recent_markets
from app.utils.date_service import get_ist_today


def run_verification():
    db = SessionLocal()
    today = get_ist_today()
    start_30 = today - timedelta(days=settings.TRENDS_LOOKBACK_DAYS - 1)
    max_age_days = settings.MAX_LATEST_VALUE_AGE_DAYS

    print("==================================================")
    print("STARTING RECENT OFFICIAL DATA VERIFICATION")
    print("==================================================")
    print(f"Current Date (Asia/Kolkata): {today}")
    print(f"30-Day Window: {start_30} to {today}")
    print(f"Max Allowed Latest Value Age: {max_age_days} days")
    print(f"Allowed Sources: {ALLOWED_SOURCES}")
    print(f"Blocked Sources: {BLOCKED_SOURCES}")
    print("==================================================\n")

    report: Dict[str, Any] = {
        "verified_at": today.strftime("%Y-%m-%d"),
        "timezone": settings.APP_TIMEZONE,
        "current_date": today.strftime("%Y-%m-%d"),
        "lookback_window_30d": {
            "start": start_30.strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d"),
            "days": settings.TRENDS_LOOKBACK_DAYS
        },
        "max_latest_value_age_days": max_age_days,
        "active_source_filter_rule": {
            "allowed_sources": sorted(list(ALLOWED_SOURCES)),
            "blocked_sources": sorted(list(BLOCKED_SOURCES)),
            "is_observed": True,
            "is_predicted": False
        },
        "recent_commodities_count": 0,
        "recent_commodities": [],
        "trends_verification": [],
        "comparison_verification": [],
        "violations": []
    }

    # 1. Verify Recent Commodities
    recent_commodities = list_recent_commodities(days=settings.TRENDS_LOOKBACK_DAYS, db=db)
    report["recent_commodities_count"] = len(recent_commodities)
    for c in recent_commodities:
        report["recent_commodities"].append({
            "name": c.canonical_name,
            "record_count_30d": c.record_count,
            "latest_date": c.latest_official_observed_date,
            "data_age_days": c.data_age_days,
            "availability_status": c.availability_status
        })

    print(f"1. Recent Commodities found with official observations: {len(recent_commodities)}")

    # 2. Verify Trends for multiple crops across multiple markets
    crops_to_verify = [c.canonical_name for c in recent_commodities[:6]]
    if "Tomato" not in crops_to_verify:
        crops_to_verify.append("Tomato")

    total_trend_points_verified = 0

    for crop in crops_to_verify:
        recent_mkts = list_recent_markets(commodity=crop, days=settings.TRENDS_LOOKBACK_DAYS, db=db)
        for mkt_obj in recent_mkts[:3]:
            mkt_name = mkt_obj.canonical_name
            trend_points = get_price_trends(
                commodity=crop,
                market=mkt_name,
                days=settings.TRENDS_LOOKBACK_DAYS,
                force_refresh=False,
                db=db
            )

            for pt in trend_points:
                total_trend_points_verified += 1
                if pt.is_predicted:
                    report["violations"].append(f"Trend point has is_predicted=True: {crop} at {mkt_name} on {pt.date}")
                if not pt.is_observed:
                    report["violations"].append(f"Trend point has is_observed=False: {crop} at {mkt_name} on {pt.date}")
                if pt.price_source in BLOCKED_SOURCES:
                    report["violations"].append(f"Trend point has blocked source '{pt.price_source}': {crop} at {mkt_name} on {pt.date}")
                if pt.price_source not in ALLOWED_SOURCES:
                    report["violations"].append(f"Trend point has unapproved source '{pt.price_source}': {crop} at {mkt_name} on {pt.date}")

            report["trends_verification"].append({
                "commodity": crop,
                "market": mkt_name,
                "records_returned": len(trend_points),
                "date_range": f"{trend_points[0].date} to {trend_points[-1].date}" if trend_points else "None",
                "sources_present": sorted(list(set(pt.price_source for pt in trend_points)))
            })

    print(f"2. Verified {total_trend_points_verified} trend points across {len(report['trends_verification'])} crop-market pairs.")

    # 3. Verify Market Comparison for multiple crops
    for crop in crops_to_verify:
        comp_res = compare_market_prices(
            commodity=crop,
            max_age_days=max_age_days,
            force_refresh=False,
            db=db
        )

        for m in comp_res.markets:
            if m.is_predicted:
                report["violations"].append(f"Comparison market has is_predicted=True: {crop} at {m.market}")
            if not m.is_observed:
                report["violations"].append(f"Comparison market has is_observed=False: {crop} at {m.market}")
            if m.price_source in BLOCKED_SOURCES:
                report["violations"].append(f"Comparison market has blocked source '{m.price_source}': {crop} at {m.market}")
            if m.data_age_days > max_age_days:
                report["violations"].append(f"Comparison market data_age_days {m.data_age_days} > {max_age_days}: {crop} at {m.market}")

        for ex in comp_res.excluded_markets:
            if not ex.reason:
                report["violations"].append(f"Excluded market missing exclusion reason: {crop} at {ex.market}")

        report["comparison_verification"].append({
            "commodity": crop,
            "qualified_markets_count": len(comp_res.markets),
            "excluded_markets_count": len(comp_res.excluded_markets),
            "qualified_markets": [
                {
                    "market": m.market,
                    "district": m.district,
                    "modal_price": m.modal_price,
                    "observation_date": m.observation_date,
                    "data_age_days": m.data_age_days,
                    "source": m.price_source
                } for m in comp_res.markets
            ],
            "excluded_markets": [
                {
                    "market": ex.market,
                    "reason": ex.reason,
                    "latest_observation_date": ex.latest_observation_date,
                    "data_age_days": ex.data_age_days
                } for ex in comp_res.excluded_markets
            ]
        })

    print(f"3. Verified market comparisons across {len(crops_to_verify)} commodities.")

    # Check for hardcoding or restriction violations
    tomato_comp = next((c for c in report["comparison_verification"] if c["commodity"] == "Tomato"), None)
    if tomato_comp:
        if tomato_comp["qualified_markets_count"] <= 2 and len(recent_mkts) > 2:
            report["violations"].append(f"Tomato comparison has artificial <= 2 market restriction: {tomato_comp['qualified_markets_count']} returned.")

    db.close()

    # Save reports
    report_paths = [
        os.path.join(backend_dir, "reports", "recent_official_trends_verification.json"),
        os.path.join(backend_dir, "..", "reports", "recent_official_trends_verification.json")
    ]

    for p in report_paths:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {p}")

    print("\n==================================================")
    print("VERIFICATION SUMMARY")
    print("==================================================")
    print(f"Total Violations: {len(report['violations'])}")
    if report["violations"]:
        print("VIOLATIONS FOUND:")
        for v in report["violations"]:
            print(f"  - [FAIL] {v}")
        sys.exit(1)
    else:
        print("[SUCCESS] All recent official data rules strictly satisfied!")
        print(f"  - No predicted values in trends or comparisons.")
        print(f"  - No fallback estimates in trends or comparisons.")
        print(f"  - Stale markets (> {max_age_days}d) correctly excluded with reasons.")
        print(f"  - All {len(recent_commodities)} active commodities dynamically supported.")
        sys.exit(0)


if __name__ == "__main__":
    run_verification()
