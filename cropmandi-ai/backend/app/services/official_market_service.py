import os
import hashlib
import json
import logging
import time
import urllib.parse
import requests
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Market, Commodity, OfficialMarketPrice, CleanedMarketPrice, Prediction
from app.utils.date_service import (
    get_ist_now,
    get_ist_today,
    parse_internal_date,
    format_api_date,
    normalize_api_date
)

logger = logging.getLogger(__name__)


def _clean_str(val: Optional[str]) -> str:
    if not val:
        return ""
    return "".join(str(val).split()).strip().lower()


def build_api_params(
    state: Optional[str] = None,
    district: Optional[str] = None,
    market: Optional[str] = None,
    commodity: Optional[str] = None,
    target_date: Optional[Any] = None,
    limit: int = 1000,
    offset: int = 0
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Constructs the query parameters dictionary for data.gov.in API.
    Returns (params_with_api_key, sanitized_params_for_logging).
    """
    date_filter_str = None
    if target_date:
        d_obj = parse_internal_date(target_date) or normalize_api_date(target_date)
        if d_obj:
            date_filter_str = format_api_date(d_obj)
        elif isinstance(target_date, str):
            date_filter_str = target_date.strip()

    params: Dict[str, Any] = {
        "api-key": settings.DATA_GOV_API_KEY,
        "format": settings.DATA_GOV_FORMAT or "json",
        "limit": limit,
        "offset": offset
    }

    safe_params: Dict[str, Any] = {
        "format": settings.DATA_GOV_FORMAT or "json",
        "limit": limit,
        "offset": offset
    }

    if state:
        params["filters[state]"] = state
        safe_params["filters[state]"] = state
    if district:
        params["filters[district]"] = district
        safe_params["filters[district]"] = district
    if market:
        clean_mkt = market.replace(" APMC", "").split("(")[0].strip()
        # Canonical mappings for data.gov.in Elasticsearch index
        mkt_lower = clean_mkt.lower()
        if mkt_lower in ["madanapalle", "madanapalli"]:
            clean_mkt = "Madanapalli"
        elif mkt_lower in ["ananthapur", "anantapur"]:
            clean_mkt = "Anantapur"
        elif mkt_lower in ["pidugurala", "piduguralla"]:
            clean_mkt = "Piduguralla"
        elif "atmakur" in mkt_lower:
            clean_mkt = "Atmakur"
        elif "sampara" in mkt_lower:
            clean_mkt = "Sampara"
        elif "banaganapall" in mkt_lower:
            clean_mkt = "Banaganapalli"
        params["filters[market]"] = clean_mkt
        safe_params["filters[market]"] = clean_mkt
    if commodity:
        clean_comm = commodity.replace("Ridge Gourd", "Ridgeguard").strip()
        params["filters[commodity]"] = clean_comm
        safe_params["filters[commodity]"] = clean_comm
    if date_filter_str:
        params["filters[arrival_date]"] = date_filter_str
        safe_params["filters[arrival_date]"] = date_filter_str

    return params, safe_params


def build_api_url(
    state: Optional[str] = None,
    district: Optional[str] = None,
    market: Optional[str] = None,
    commodity: Optional[str] = None,
    target_date: Optional[Any] = None,
    limit: int = 1000,
    offset: int = 0
) -> Tuple[str, Dict[str, Any], str]:
    """
    Constructs the data.gov.in endpoint URL and parameters dictionary.
    Returns (endpoint_url, params_dict_with_key, safe_url_for_logging).
    """
    res_id = settings.DATA_GOV_RESOURCE_ID.strip("/")
    if res_id.startswith("resource/"):
        res_id = res_id[len("resource/"):]

    base_url = settings.DATA_GOV_BASE_URL.rstrip("/")
    if not base_url.endswith("resource"):
        endpoint_url = f"{base_url}/resource/{res_id}"
    else:
        endpoint_url = f"{base_url}/{res_id}"

    params, safe_params = build_api_params(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        target_date=target_date,
        limit=limit,
        offset=offset
    )

    safe_query = urllib.parse.urlencode(safe_params)
    safe_log_url = f"{endpoint_url}?{safe_query}"

    return endpoint_url, params, safe_log_url


# Alias
build_data_gov_url = build_api_url


def map_api_fields(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts raw field aliases into standardized dictionary.
    Supports comprehensive field name variations from data.gov.in.
    """
    if not isinstance(raw, dict):
        return {}

    state_raw = (
        raw.get("State") or raw.get("state") or raw.get("State/UT") or
        raw.get("state_name") or raw.get("State_Name")
    )
    district_raw = (
        raw.get("District") or raw.get("district") or raw.get("district_name") or
        raw.get("District_Name")
    )
    market_raw = (
        raw.get("Market") or raw.get("market") or raw.get("market_name") or
        raw.get("Market_Name") or raw.get("Market Name") or raw.get("center") or
        raw.get("mandi") or raw.get("APMC")
    )
    commodity_raw = (
        raw.get("Commodity") or raw.get("commodity") or raw.get("commodity_name") or
        raw.get("Commodity_Name") or raw.get("Commodity Name") or raw.get("crop")
    )
    date_raw = (
        raw.get("Arrival_Date") or raw.get("arrival_date") or raw.get("Arrival Date") or
        raw.get("Date") or raw.get("date") or raw.get("reported_date") or raw.get("price_date") or
        raw.get("Price_Date")
    )
    modal_raw = (
        raw.get("Modal_Price") or raw.get("modal_price") or raw.get("Modal Price") or
        raw.get("modal_price_rs") or raw.get("Modal_Price_Rs") or raw.get("price") or
        raw.get("Modal_Price_Rs_Quintal")
    )
    min_raw = (
        raw.get("Min_Price") or raw.get("min_price") or raw.get("Min Price") or
        raw.get("min_price_rs") or raw.get("Min_Price_Rs") or raw.get("Minimum Price")
    )
    max_raw = (
        raw.get("Max_Price") or raw.get("max_price") or raw.get("Max Price") or
        raw.get("max_price_rs") or raw.get("Max_Price_Rs") or raw.get("Maximum Price")
    )
    arrival_raw = (
        raw.get("Arrival_Quantity") or raw.get("arrival_quantity") or raw.get("Arrival Quantity") or
        raw.get("arrivals") or raw.get("Arrivals") or raw.get("arrival") or raw.get("Arrival")
    )
    variety_raw = raw.get("Variety") or raw.get("variety")
    grade_raw = raw.get("Grade") or raw.get("grade")

    return {
        "state": state_raw,
        "district": district_raw,
        "market": market_raw,
        "commodity": commodity_raw,
        "arrival_date": date_raw,
        "modal_price": modal_raw,
        "min_price": min_raw,
        "max_price": max_raw,
        "arrival_quantity": arrival_raw,
        "variety": variety_raw,
        "grade": grade_raw
    }


def normalize_api_record(raw: Dict[str, Any], db: Session) -> Optional[Dict[str, Any]]:
    """
    Normalizes raw API JSON record into internal data representation with database entities.
    """
    mapped = map_api_fields(raw)
    if not mapped.get("market") or not mapped.get("commodity") or not mapped.get("arrival_date") or mapped.get("modal_price") is None:
        return None

    obs_date = normalize_api_date(mapped["arrival_date"])
    if not obs_date:
        return None

    try:
        modal_p = float(str(mapped["modal_price"]).replace(",", "").replace("Rs.", "").strip())
        min_p = float(str(mapped["min_price"]).replace(",", "").replace("Rs.", "").strip()) if mapped["min_price"] is not None else None
        max_p = float(str(mapped["max_price"]).replace(",", "").replace("Rs.", "").strip()) if mapped["max_price"] is not None else None
        arr_q = float(str(mapped["arrival_quantity"]).replace(",", "").strip()) if mapped["arrival_quantity"] is not None else None
    except (ValueError, TypeError):
        return None

    # Load canonical entities
    all_commodities = {c.canonical_name: c for c in db.query(Commodity).all()}
    all_markets = {m.canonical_name: m for m in db.query(Market).all()}

    # Match commodity
    comm_raw = str(mapped["commodity"]).strip()
    norm_comm_str = _clean_str(comm_raw)
    comm_obj = None
    for name, obj in all_commodities.items():
        if _clean_str(name) in norm_comm_str or norm_comm_str in _clean_str(name):
            comm_obj = obj
            break
    if not comm_obj:
        comm_obj = db.query(Commodity).filter(Commodity.canonical_name == comm_raw).first()
        if not comm_obj:
            comm_obj = Commodity(canonical_name=comm_raw, original_name=comm_raw)
            db.add(comm_obj)
            db.commit()
            db.refresh(comm_obj)

    # Match market
    mkt_raw = str(mapped["market"]).strip()
    norm_mkt_str = _clean_str(mkt_raw)
    mkt_obj = None
    for name, obj in all_markets.items():
        clean_name = _clean_str(name).replace("apmc", "").replace("mc", "").strip()
        if clean_name in norm_mkt_str or norm_mkt_str in clean_name or (len(clean_name) >= 6 and norm_mkt_str.startswith(clean_name[:6])):
            mkt_obj = obj
            break
    if not mkt_obj:
        mkt_name = f"{mkt_raw} APMC" if "apmc" not in mkt_raw.lower() else mkt_raw
        mkt_obj = db.query(Market).filter(Market.canonical_name == mkt_name).first()
        if not mkt_obj:
            mkt_obj = Market(
                canonical_name=mkt_name,
                original_name=mkt_raw,
                district=mapped.get("district") or "Andhra Pradesh",
                state=mapped.get("state") or "Andhra Pradesh"
            )
            db.add(mkt_obj)
            db.commit()
            db.refresh(mkt_obj)

    raw_str = json.dumps(raw, sort_keys=True)
    payload_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
    record_id = f"APMC_{mkt_obj.id}_{comm_obj.id}_{obs_date.isoformat()}"

    return {
        "source": "official_api",
        "source_record_id": record_id,
        "market": mkt_obj,
        "commodity": comm_obj,
        "state": mapped.get("state"),
        "district": mapped.get("district"),
        "canonical_market": mkt_obj.canonical_name,
        "canonical_commodity": comm_obj.canonical_name,
        "observation_date": obs_date,
        "modal_price": modal_p,
        "min_price": min_p,
        "max_price": max_p,
        "arrival_quantity": arr_q,
        "variety": mapped.get("variety"),
        "grade": mapped.get("grade"),
        "original_market_name": mkt_raw,
        "original_commodity_name": comm_raw,
        "raw_payload_hash": payload_hash,
        "raw_payload": raw_str
    }


def validate_api_record(
    norm: Dict[str, Any],
    commodity: str,
    market: str,
    district: Optional[str] = None,
    state: Optional[str] = None,
    target_date: Optional[date] = None
) -> Tuple[bool, str]:
    """
    Strict validation rule enforcement:
    1. modal_price >= 0
    2. min_price <= modal_price <= max_price (if present)
    3. exact canonical commodity match
    4. exact canonical market match
    5. exact date match (if specified)
    """
    if norm["modal_price"] < 0:
        return False, "Negative modal price"

    if norm["min_price"] is not None and norm["min_price"] > norm["modal_price"]:
        return False, f"min_price ({norm['min_price']}) > modal_price ({norm['modal_price']})"

    if norm["max_price"] is not None and norm["max_price"] < norm["modal_price"]:
        return False, f"max_price ({norm['max_price']}) < modal_price ({norm['modal_price']})"

    from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
    norm_req_comm = normalize_commodity_name(commodity)
    norm_req_mkt = normalize_market_name(market)

    if norm["canonical_commodity"] != commodity and norm["canonical_commodity"] != norm_req_comm:
        return False, f"Commodity mismatch: got '{norm['canonical_commodity']}', expected '{commodity}'"

    if norm["canonical_market"] != market and norm["canonical_market"] != norm_req_mkt:
        return False, f"Market mismatch: got '{norm['canonical_market']}', expected '{market}'"

    if target_date and norm["observation_date"] != target_date:
        return False, f"Date mismatch: got '{norm['observation_date']}', expected '{target_date}'"

    if district and norm.get("district"):
        if _clean_str(district) not in _clean_str(norm["district"]) and _clean_str(norm["district"]) not in _clean_str(district):
            logger.debug("District mismatch: got %s, expected %s", norm["district"], district)

    return True, "valid"


def find_exact_record(
    records: List[Dict[str, Any]],
    commodity: str,
    market: str,
    target_date: date,
    district: Optional[str] = None,
    state: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Finds the exact matching normalized record and returns (matched_record, rejected_records_with_reasons).
    """
    matched = None
    rejected = []
    for rec in records:
        valid, reason = validate_api_record(rec, commodity, market, district, state, target_date)
        if valid and not matched:
            matched = rec
        elif not valid:
            rejected.append({"record": rec, "reason": reason})
    return matched, rejected


# Alias
filter_exact_record = lambda records, commodity, market, target_date, district=None, state=None: find_exact_record(records, commodity, market, target_date, district, state)[0]


def fetch_paginated_records(
    endpoint_url: str,
    params: Dict[str, Any],
    safe_log_url: str,
    max_pages: int = 5
) -> Tuple[int, List[Dict[str, Any]], Optional[str]]:
    """
    Safe HTTP execution with pagination, timeout, retries, 429 rate limit backoff, and sanitized error handling.
    """
    if not settings.DATA_GOV_API_KEY:
        return 401, [], "Official data service is not configured."

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CropMandiAI/2.0'}
    all_records: List[Dict[str, Any]] = []
    current_params = dict(params)
    page_limit = int(current_params.get("limit", settings.DATA_GOV_PAGE_LIMIT or 1000))
    offset = int(current_params.get("offset", 0))
    last_status_code = 200
    error_msg = None

    timeout_sec = getattr(settings, "DATA_GOV_TIMEOUT_SECONDS", getattr(settings, "DATA_GOV_API_TIMEOUT_SECONDS", 30))
    max_retries = getattr(settings, "DATA_GOV_MAX_RETRIES", getattr(settings, "DATA_GOV_API_MAX_RETRIES", 3))

    for page in range(max_pages):
        current_params["offset"] = offset
        raw_json = None

        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.get(
                    endpoint_url,
                    params=current_params,
                    headers=headers,
                    timeout=timeout_sec
                )
                last_status_code = resp.status_code

                if resp.status_code == 401 or resp.status_code == 403:
                    logger.warning("data.gov.in authentication failed (HTTP %d)", resp.status_code)
                    return resp.status_code, [], "Official data API authentication failed."

                if resp.status_code == 429:
                    logger.warning("data.gov.in rate limit (429), backoff attempt %d", attempt)
                    time.sleep(1.5 * attempt)
                    continue

                if resp.status_code == 404:
                    return 404, [], "The configured data.gov.in resource does not currently provide a usable API."

                if resp.status_code != 200:
                    logger.warning("data.gov.in returned HTTP %d for endpoint %s", resp.status_code, safe_log_url)
                    error_msg = f"HTTP {resp.status_code}"
                    continue

                raw_json = resp.json()
                break
            except requests.Timeout:
                logger.warning("data.gov.in timeout on attempt %d for %s", attempt, safe_log_url)
                error_msg = "Live official data could not be fetched. Stored official data or fallback sources may be used."
                time.sleep(1.0)
            except requests.RequestException as exc:
                logger.warning("data.gov.in request exception attempt %d: %s", attempt, exc)
                error_msg = "Live official data could not be fetched. Stored official data or fallback sources may be used."
                time.sleep(1.0)

        if not raw_json or not isinstance(raw_json, dict) or "records" not in raw_json:
            break

        page_records = raw_json.get("records", [])
        if not page_records:
            break

        all_records.extend(page_records)
        if len(page_records) < page_limit:
            break
        offset += page_limit

    return last_status_code, all_records, error_msg


# Alias
fetch_with_pagination = fetch_paginated_records


def fetch_exact_record(
    db: Session,
    commodity: str,
    market: str,
    target_date: date,
    district: Optional[str] = None,
    state: Optional[str] = None,
    force_refresh: bool = True
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes single-date official API lookup with exact filter parameters (DD/MM/YYYY)
    and returns (matched_record, diagnostic_metadata).
    """
    date_api_str = format_api_date(target_date)
    endpoint_url, params, safe_log_url = build_api_url(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        target_date=target_date,
        limit=1000
    )

    logger.info("Executing exact official API lookup: state=%s district=%s commodity=%s market=%s date=%s URL=%s",
                state, district, commodity, market, date_api_str, safe_log_url)
    http_status, raw_records, error = fetch_paginated_records(endpoint_url, params, safe_log_url, max_pages=3)

    norm_records: List[Dict[str, Any]] = []
    for raw in raw_records:
        norm = normalize_api_record(raw, db)
        if norm:
            norm_records.append(norm)

    matched, rejected = find_exact_record(norm_records, commodity, market, target_date, district, state)

    api_status = "available" if matched else ("no_records" if http_status == 200 else "error")
    if error and not matched:
        api_status = "error"

    diag_info = {
        "requested": {
            "state": state,
            "district": district,
            "market": market,
            "commodity": commodity,
            "date": target_date.isoformat(),
            "api_filter_date": date_api_str
        },
        "api_checked": True,
        "api_status": api_status,
        "record_found": matched is not None,
        "record": matched,
        "rejected_records": rejected,
        "raw_records_count": len(raw_records),
        "http_status": http_status,
        "error": error,
        "checked_at": get_ist_now().isoformat()
    }

    if matched:
        from app.services.official_market_sync_service import upsert_official_record, replace_stale_prediction
        off_rec, _ = upsert_official_record(db, matched)
        replace_stale_prediction(db, matched["market"].id, matched["commodity"].id, target_date, off_rec.id)

    return matched, diag_info


# Alias
fetch_exact_official_record = fetch_exact_record


def fetch_date_range_records(
    db: Session,
    commodity: str,
    market: str,
    start_date: date,
    end_date: date,
    district: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 1000
) -> Dict[date, Dict[str, Any]]:
    """
    Fetches all official records for commodity and market across a date range.
    """
    endpoint_url, params, safe_log_url = build_api_url(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        limit=limit
    )

    logger.info("Fetching official API records across range [%s to %s]: URL=%s", start_date, end_date, safe_log_url)
    http_status, raw_records, error = fetch_paginated_records(endpoint_url, params, safe_log_url, max_pages=5)

    records_by_date: Dict[date, Dict[str, Any]] = {}
    from app.services.official_market_sync_service import upsert_official_record, replace_stale_prediction

    for raw in raw_records:
        norm = normalize_api_record(raw, db)
        if not norm:
            continue
        valid, _ = validate_api_record(norm, commodity, market, district, state)
        if not valid:
            continue
        rec_dt = norm["observation_date"]
        if start_date <= rec_dt <= end_date:
            off_rec, _ = upsert_official_record(db, norm)
            replace_stale_prediction(db, norm["market"].id, norm["commodity"].id, rec_dt, off_rec.id)
            records_by_date[rec_dt] = norm

    return records_by_date


def get_api_health(
    state: Optional[str] = "Andhra Pradesh",
    district: Optional[str] = "Annamayya",
    market: Optional[str] = "Madanapalli",
    commodity: Optional[str] = "Tomato"
) -> Dict[str, Any]:
    """
    Health check diagnostic reporting status, record count, actual fields, and latest date without exposing secrets.
    """
    endpoint_url, params, safe_log_url = build_api_url(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        limit=10
    )

    now_ist = get_ist_now()
    http_status, raw_records, error = fetch_paginated_records(endpoint_url, params, safe_log_url, max_pages=1)

    actual_fields: List[str] = []
    latest_date_str = None

    if raw_records:
        actual_fields = list(raw_records[0].keys())
        dates = []
        for r in raw_records:
            d = normalize_api_date(r.get("Arrival_Date") or r.get("arrival_date") or r.get("date") or r.get("Date"))
            if d:
                dates.append(d)
        if dates:
            latest_date_str = max(dates).isoformat()

    api_status = "available"
    if http_status == 401 or http_status == 403:
        api_status = "authentication_failed"
    elif http_status == 408 or http_status == 504:
        api_status = "timeout"
    elif http_status != 200:
        api_status = "unavailable"
    elif len(raw_records) == 0:
        api_status = "no_records"

    return {
        "resource_id": settings.DATA_GOV_RESOURCE_ID,
        "api_status": api_status,
        "http_status": http_status,
        "record_count": len(raw_records),
        "latest_available_date": latest_date_str,
        "actual_fields": actual_fields,
        "checked_at": now_ist.isoformat(),
        "message": f"Endpoint returned HTTP {http_status} with {len(raw_records)} sample records" if not error else error
    }


_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIVE_JSON_PATHS = [
    os.path.join(_BASE_DIR, "data", "live_fetched_mandi_data.json"),
    os.path.abspath("data/live_fetched_mandi_data.json"),
    os.path.abspath("backend/data/live_fetched_mandi_data.json")
]


def clear_live_fetched_json() -> None:
    """Clears the live fetched mandi JSON file before each new generate request."""
    for path_str in LIVE_JSON_PATHS:
        try:
            if os.path.exists(path_str):
                with open(path_str, "w", encoding="utf-8") as f:
                    json.dump({}, f)
        except Exception as e:
            logger.debug("Failed clearing %s: %s", path_str, e)


def save_live_fetched_json(payload: Dict[str, Any]) -> None:
    """Saves the latest live API response payload in JSON format for transparency and frontend display."""
    for path_str in LIVE_JSON_PATHS:
        try:
            os.makedirs(os.path.dirname(path_str), exist_ok=True)
            with open(path_str, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
        except Exception as e:
            logger.debug("Failed saving %s: %s", path_str, e)
        except Exception as e:
            logger.debug("Failed saving %s: %s", path_str, e)


def get_live_fetched_json() -> Optional[Dict[str, Any]]:
    """Returns the latest live fetched JSON payload."""
    for path_str in LIVE_JSON_PATHS:
        try:
            if os.path.exists(path_str):
                with open(path_str, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if content:
                        return content
        except Exception:
            continue
    return None

