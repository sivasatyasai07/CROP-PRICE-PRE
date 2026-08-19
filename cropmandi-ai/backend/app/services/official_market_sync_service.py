import hashlib
import json
import logging
import time
import requests
import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Market, Commodity, OfficialMarketPrice, CleanedMarketPrice, Prediction
from app.services.date_service import get_ist_now, get_ist_today, parse_date_safely
from app.services.cache_service import global_cache

logger = logging.getLogger(__name__)

# Valid crop-market constraints in CropMandi AI
VALID_CROP_MARKET_MAP = {
    "Ajwan": ["Kurnool APMC"],
    "Tomato": [
        "Madanapalli APMC", "Kalikiri APMC", "Palamaner APMC", "Punganur APMC",
        "Anantapur APMC", "Pattikonda APMC", "Mulakalacheruvu APMC", "Valmikipuram APMC",
        "Somala APMC", "Kuppam APMC"
    ],
    "Onion": [
        "Kurnool APMC", "Pattikonda APMC", "Adoni APMC", "Yerraguntla APMC",
        "Rajahmundry APMC", "Tenali APMC"
    ],
    "Potato": [
        "Palamaner APMC", "Kurnool APMC", "Rajahmundry APMC", "Tenali APMC"
    ],
    "Lemon": [
        "Tenali APMC", "Gopalapuram APMC", "Chintalapudi APMC", "Eluru APMC", "Denduluru APMC"
    ],
    "Brinjal": ["Palamaner APMC"],
    "Cabbage": ["Palamaner APMC"],
    "Cauliflower": ["Palamaner APMC"],
    "Green Chilli": ["Palamaner APMC", "Parchur APMC"],
    "Cluster Beans": ["Palamaner APMC"],
    "Ridge Gourd": ["Palamaner APMC"],
    "Paddy": [
        "Banaganapalli APMC", "Atmakur (Nandyal District) APMC", "Rajahmundry APMC",
        "Tiruvuru APMC", "Tanuku APMC", "Sampara (Kakinada Rural) APMC"
    ],
    "Maize": [
        "Kurnool APMC", "Atmakur (Nandyal District) APMC", "Tiruvuru APMC",
        "Nandyal APMC", "Chintalapudi APMC"
    ],
    "Jowar": ["Banaganapalli APMC", "Alur APMC"],
    "Groundnut": ["Kurnool APMC", "Adoni APMC", "Kadapa APMC", "Yemmiganuru APMC"],
    "Castor Seed": ["Kurnool APMC", "Adoni APMC", "Yemmiganuru APMC"],
    "Sunflower": ["Kurnool APMC", "Adoni APMC"],
    "Bengal Gram": ["Banaganapalli APMC", "Kurnool APMC"],
    "Red Gram": ["Kurnool APMC", "Dhone APMC"],
    "Black Gram": ["Kurnool APMC"],
    "Dry Chillies": [
        "Guntur APMC", "Kurnool APMC", "Piduguralla (Palnadu) APMC", "Tiruvuru APMC"
    ],
    "Beetroot": ["Palamaner APMC", "Madanapalli APMC"],
    "Carrot": ["Palamaner APMC", "Madanapalli APMC"]
}


def _clean_str(val: Optional[str]) -> str:
    if not val:
        return ""
    return "".join(val.split()).strip().lower()


def _match_canonical_commodity(raw_comm: str, commodities_by_name: Dict[str, Commodity]) -> Optional[Commodity]:
    norm_raw = _clean_str(raw_comm)
    for name, obj in commodities_by_name.items():
        if _clean_str(name) in norm_raw or norm_raw in _clean_str(name):
            return obj
    return None


def _match_canonical_market(raw_mkt: str, markets_by_name: Dict[str, Market]) -> Optional[Market]:
    norm_raw = _clean_str(raw_mkt)
    for name, obj in markets_by_name.items():
        clean_name = _clean_str(name).replace("apmc", "").replace("mc", "").strip()
        if clean_name in norm_raw or norm_raw in clean_name or (len(clean_name) >= 6 and norm_raw.startswith(clean_name[:6])):
            return obj
    return None


def normalize_api_record(raw: Dict[str, Any], db: Session) -> Optional[Dict[str, Any]]:
    """
    Normalizes raw JSON record from data.gov.in into standard internal structure.
    Handles multiple field variations (Market, Commodity, Arrival_Date, Min_Price, Modal_Price, etc.)
    """
    if not isinstance(raw, dict):
        return None

    # Field name fallbacks
    market_raw = (
        raw.get("market") or raw.get("Market") or raw.get("market_name") or
        raw.get("Market_Name") or raw.get("Market Name") or raw.get("center")
    )
    commodity_raw = (
        raw.get("commodity") or raw.get("Commodity") or raw.get("commodity_name") or
        raw.get("Commodity_Name") or raw.get("Commodity Name") or raw.get("crop")
    )
    date_raw = (
        raw.get("arrival_date") or raw.get("Arrival_Date") or raw.get("Arrival Date") or
        raw.get("date") or raw.get("Date") or raw.get("reported_date") or raw.get("price_date")
    )
    
    modal_raw = (
        raw.get("modal_price") or raw.get("Modal_Price") or raw.get("Modal Price") or
        raw.get("modal_price_rs") or raw.get("Modal_Price_Rs") or raw.get("price")
    )
    min_raw = (
        raw.get("min_price") or raw.get("Min_Price") or raw.get("Min Price") or
        raw.get("min_price_rs") or raw.get("Min_Price_Rs")
    )
    max_raw = (
        raw.get("max_price") or raw.get("Max_Price") or raw.get("Max Price") or
        raw.get("max_price_rs") or raw.get("Max_Price_Rs")
    )
    arrival_raw = (
        raw.get("arrival_quantity") or raw.get("Arrival_Quantity") or raw.get("Arrival Quantity") or
        raw.get("arrivals") or raw.get("Arrivals") or raw.get("arrival") or raw.get("Arrival")
    )

    if not market_raw or not commodity_raw or not date_raw or modal_raw is None:
        return None

    obs_date = parse_date_safely(date_raw)
    if not obs_date:
        return None

    try:
        modal_p = float(modal_raw)
        min_p = float(min_raw) if min_raw is not None else None
        max_p = float(max_raw) if max_raw is not None else None
        arr_q = float(arrival_raw) if arrival_raw is not None else None
    except (ValueError, TypeError):
        return None

    # Load lookup dictionaries
    all_commodities = {c.canonical_name: c for c in db.query(Commodity).all()}
    all_markets = {m.canonical_name: m for m in db.query(Market).all()}

    comm_obj = _match_canonical_commodity(str(commodity_raw), all_commodities)
    if not comm_obj:
        comm_obj = db.query(Commodity).filter(Commodity.canonical_name == str(commodity_raw)).first()
        if not comm_obj:
            comm_obj = Commodity(canonical_name=str(commodity_raw), original_name=str(commodity_raw))
            db.add(comm_obj)
            db.commit()
            db.refresh(comm_obj)

    mkt_obj = _match_canonical_market(str(market_raw), all_markets)
    if not mkt_obj:
        mkt_name = f"{market_raw} APMC" if "apmc" not in str(market_raw).lower() else str(market_raw)
        mkt_obj = db.query(Market).filter(Market.canonical_name == mkt_name).first()
        if not mkt_obj:
            mkt_obj = Market(canonical_name=mkt_name, original_name=str(market_raw), district="Andhra Pradesh")
            db.add(mkt_obj)
            db.commit()
            db.refresh(mkt_obj)

    if not comm_obj or not mkt_obj:
        return None

    # Payload hash for verification
    raw_str = json.dumps(raw, sort_keys=True)
    payload_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
    record_id = f"APMC_{mkt_obj.id}_{comm_obj.id}_{obs_date.isoformat()}"

    return {
        "source": "official_api",
        "source_record_id": record_id,
        "market": mkt_obj,
        "commodity": comm_obj,
        "canonical_market": mkt_obj.canonical_name,
        "canonical_commodity": comm_obj.canonical_name,
        "observation_date": obs_date,
        "modal_price": modal_p,
        "min_price": min_p,
        "max_price": max_p,
        "arrival_quantity": arr_q,
        "original_market_name": str(market_raw),
        "original_commodity_name": str(commodity_raw),
        "raw_payload_hash": payload_hash,
        "raw_payload": raw_str
    }


def validate_api_record(norm: Dict[str, Any], requested_comm: str, requested_mkt: str, requested_date: Optional[datetime.date] = None) -> Tuple[bool, str]:
    """
    Strict validation rule enforcement:
    1. modal_price >= 0
    2. min_price <= modal_price <= max_price (if min/max present)
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
    norm_req_comm = normalize_commodity_name(requested_comm)
    norm_req_mkt = normalize_market_name(requested_mkt)

    if norm["canonical_commodity"] != requested_comm and norm["canonical_commodity"] != norm_req_comm:
        return False, f"Commodity mismatch: got {norm['canonical_commodity']}, expected {requested_comm}"

    if norm["canonical_market"] != requested_mkt and norm["canonical_market"] != norm_req_mkt:
        return False, f"Market mismatch: got {norm['canonical_market']}, expected {requested_mkt}"

    if requested_date and norm["observation_date"] != requested_date:
        return False, f"Date mismatch: got {norm['observation_date']}, expected {requested_date}"

    return True, "valid"


def upsert_official_record(db: Session, norm: Dict[str, Any]) -> Tuple[OfficialMarketPrice, bool]:
    """
    Idempotent upsert of official record into OfficialMarketPrice & CleanedMarketPrice tables.
    Returns (OfficialMarketPrice, is_new).
    """
    now = get_ist_now()
    existing_off = db.query(OfficialMarketPrice).filter(
        OfficialMarketPrice.market_id == norm["market"].id,
        OfficialMarketPrice.commodity_id == norm["commodity"].id,
        OfficialMarketPrice.observation_date == norm["observation_date"]
    ).first()

    is_new = False
    if existing_off:
        existing_off.modal_price = norm["modal_price"]
        existing_off.min_price = norm["min_price"]
        existing_off.max_price = norm["max_price"]
        existing_off.arrival_quantity = norm["arrival_quantity"]
        existing_off.raw_payload_hash = norm["raw_payload_hash"]
        existing_off.raw_payload = norm["raw_payload"]
        existing_off.last_verified_at = now
        existing_off.data_status = "fresh_official"
        existing_off.verification_status = "api_verified"
        off_rec = existing_off
    else:
        is_new = True
        off_rec = OfficialMarketPrice(
            source="official_api",
            source_record_id=norm["source_record_id"],
            market_id=norm["market"].id,
            commodity_id=norm["commodity"].id,
            observation_date=norm["observation_date"],
            min_price=norm["min_price"],
            modal_price=norm["modal_price"],
            max_price=norm["max_price"],
            arrival_quantity=norm["arrival_quantity"],
            original_market_name=norm["original_market_name"],
            original_commodity_name=norm["original_commodity_name"],
            fetched_at=now,
            last_verified_at=now,
            data_status="fresh_official",
            verification_status="api_verified",
            raw_payload_hash=norm["raw_payload_hash"],
            raw_payload=norm["raw_payload"]
        )
        db.add(off_rec)

    # Mirror into CleanedMarketPrice table for ML feature generation
    existing_cleaned = db.query(CleanedMarketPrice).filter(
        CleanedMarketPrice.market_id == norm["market"].id,
        CleanedMarketPrice.commodity_id == norm["commodity"].id,
        CleanedMarketPrice.observation_date == norm["observation_date"]
    ).first()

    if existing_cleaned:
        existing_cleaned.modal_price = norm["modal_price"]
        existing_cleaned.min_price = norm["min_price"]
        existing_cleaned.max_price = norm["max_price"]
        existing_cleaned.arrival_quantity = norm["arrival_quantity"]
    else:
        db.add(CleanedMarketPrice(
            market_id=norm["market"].id,
            commodity_id=norm["commodity"].id,
            observation_date=norm["observation_date"],
            min_price=norm["min_price"],
            modal_price=norm["modal_price"],
            max_price=norm["max_price"],
            arrival_quantity=norm["arrival_quantity"],
            unit=norm["commodity"].unit or "₹ per quintal"
        ))

    db.commit()
    db.refresh(off_rec)
    return off_rec, is_new


def replace_stale_prediction(db: Session, market_id: int, commodity_id: int, obs_date: datetime.date, official_rec_id: int) -> int:
    """
    Marks any prediction records matching market + commodity + target_date as superseded.
    """
    preds = db.query(Prediction).filter(
        Prediction.market_id == market_id,
        Prediction.commodity_id == commodity_id,
        Prediction.target_date == obs_date
    ).all()

    replaced_count = 0
    for p in preds:
        p.prediction_status = "superseded_by_official"
        p.superseded_by_official = True
        p.official_record_id = official_rec_id
        replaced_count += 1

    if replaced_count > 0:
        db.commit()
    return replaced_count


def get_latest_official_date(db: Session, commodity: str, market: str) -> Optional[datetime.date]:
    """
    Returns the latest official observation date in the database for a commodity and market.
    """
    from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
    norm_m = normalize_market_name(market)
    norm_c = normalize_commodity_name(commodity)

    mkt = db.query(Market).filter((Market.canonical_name == market) | (Market.canonical_name == norm_m)).first()
    comm = db.query(Commodity).filter((Commodity.canonical_name == commodity) | (Commodity.canonical_name == norm_c)).first()

    if not mkt or not comm:
        return None

    rec = db.query(CleanedMarketPrice).filter(
        CleanedMarketPrice.market_id == mkt.id,
        CleanedMarketPrice.commodity_id == comm.id
    ).order_by(CleanedMarketPrice.observation_date.desc()).first()

    return rec.observation_date if rec else None


def fetch_date_range_records(
    db: Session,
    commodity: str,
    market: str,
    start_date: datetime.date,
    end_date: datetime.date,
    limit: int = 1000
) -> Dict[datetime.date, Dict[str, Any]]:
    """
    Fetches official records directly from data.gov.in API for a date range.
    Handles pagination, retries, 429 rate limits, timeout, and field variations without exposing API keys.
    """
    api_key = settings.DATA_GOV_API_KEY
    if not api_key:
        logger.warning("DATA_GOV_API_KEY is not configured in backend environment.")
        return {}

    res_id = settings.DATA_GOV_RESOURCE_ID.lstrip('/')
    if res_id.startswith("resource/"):
        res_id = res_id[len("resource/"):]
    safe_url = f"{settings.DATA_GOV_BASE_URL.rstrip('/')}/resource/{res_id}"
    logger.info("Querying data.gov.in API: commodity=%s market=%s window=[%s to %s] endpoint=%s", commodity, market, start_date, end_date, safe_url)

    clean_market = market.replace(" APMC", "").strip()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CropMandiAI/2.0'}

    records_by_date: Dict[datetime.date, Dict[str, Any]] = {}
    page_size = min(limit, 1000)
    offset = 0
    max_pages = 5

    for page in range(max_pages):
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": page_size,
            "offset": offset,
            "filters[commodity]": commodity,
            "filters[market]": clean_market
        }

        raw_data = None
        for attempt in range(1, settings.DATA_GOV_API_MAX_RETRIES + 1):
            try:
                resp = requests.get(safe_url, params=params, headers=headers, timeout=settings.DATA_GOV_API_TIMEOUT_SECONDS)
                if resp.status_code == 429:
                    logger.warning("data.gov.in API rate limited (429) on attempt %s, backoff 1.5s", attempt)
                    time.sleep(1.5)
                    continue
                if resp.status_code != 200:
                    logger.warning("data.gov.in API returned HTTP %s on attempt %s", resp.status_code, attempt)
                    continue
                raw_data = resp.json()
                break
            except requests.RequestException as exc:
                logger.warning("data.gov.in API connection error on attempt %s: %s", attempt, exc)
                time.sleep(1)

        if not raw_data or not isinstance(raw_data, dict) or 'records' not in raw_data:
            break

        records = raw_data.get('records', [])
        if not records:
            break

        for rec in records:
            norm = normalize_api_record(rec, db)
            if not norm:
                continue

            valid, reason = validate_api_record(norm, commodity, market)
            if not valid:
                logger.debug("Rejected API record: %s", reason)
                continue

            rec_date = norm["observation_date"]
            if start_date <= rec_date <= end_date:
                # Upsert into DB and replace stale predictions
                off_rec, _ = upsert_official_record(db, norm)
                replace_stale_prediction(db, norm["market"].id, norm["commodity"].id, rec_date, off_rec.id)
                records_by_date[rec_date] = norm

        # Stop paging if we received fewer records than page_size
        if len(records) < page_size:
            break
        offset += page_size

    logger.info("data.gov.in API query completed: %d valid records accepted in window [%s to %s]", len(records_by_date), start_date, end_date)
    return records_by_date


def fetch_latest_official_data(db: Session, commodity: str, market: str, lookback_days: int = 14) -> Dict[datetime.date, Dict[str, Any]]:
    """Fetches latest official data up to server today."""
    today = get_ist_today()
    start_date = today - datetime.timedelta(days=lookback_days)
    return fetch_date_range_records(db, commodity, market, start_date, today)


def fetch_recent_official_records(db: Session, commodity: str, market: str, lookback_days: int = 14) -> List[Dict[str, Any]]:
    """Returns list of normalized records from the rolling lookback window."""
    res_map = fetch_latest_official_data(db, commodity, market, lookback_days)
    return list(res_map.values())


def refresh_before_forecast(
    db: Session,
    commodity: str,
    market: str,
    lookback_days: int = 14,
    force_refresh: bool = True
) -> Dict[str, Any]:
    """
    Mandatory pre-forecast synchronization:
    1. Determines current date in Asia/Kolkata.
    2. Queries data.gov.in across [server_today - lookback_days, server_today].
    3. Normalizes and validates records.
    4. Upserts records into OfficialMarketPrice and CleanedMarketPrice.
    5. Returns sync metadata for forecast pipeline and diagnostics.
    """
    started_at = get_ist_now()
    today_ist = get_ist_today()
    start_date = today_ist - datetime.timedelta(days=lookback_days)
    end_date = today_ist

    summary: Dict[str, Any] = {
        "api_called": True,
        "api_status": "in_progress",
        "started_at": started_at,
        "completed_at": None,
        "refresh_start_date": start_date,
        "refresh_end_date": end_date,
        "records_received": 0,
        "records_accepted": 0,
        "records_rejected": 0,
        "records_upserted": 0,
        "latest_api_date": None,
        "latest_db_date": None,
        "records_by_date": {},
        "error": None
    }

    try:
        records_map = fetch_date_range_records(
            db=db,
            commodity=commodity,
            market=market,
            start_date=start_date,
            end_date=end_date
        )
        summary["records_by_date"] = records_map
        summary["records_accepted"] = len(records_map)
        summary["records_upserted"] = len(records_map)

        if records_map:
            latest_api_dt = max(records_map.keys())
            summary["latest_api_date"] = latest_api_dt
            summary["api_status"] = "success"
        else:
            summary["api_status"] = "checked_no_records"

        summary["latest_db_date"] = get_latest_official_date(db, commodity, market)
        summary["completed_at"] = get_ist_now()

    except Exception as exc:
        logger.exception("Error in refresh_before_forecast for %s @ %s: %s", commodity, market, exc)
        summary["api_status"] = "failed"
        summary["error"] = str(exc)
        summary["latest_db_date"] = get_latest_official_date(db, commodity, market)
        summary["completed_at"] = get_ist_now()

    return summary


def sync_latest_market_data(db: Session = None, lookback_days: int = 14) -> Dict[str, Any]:
    """
    Synchronizes all valid crop-market pairs for the latest rolling lookback window.
    Generates a full synchronization report.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    started_at = get_ist_now()
    today = get_ist_today()
    start_date = today - datetime.timedelta(days=lookback_days)

    report = {
        "status": "in_progress",
        "started_at": started_at,
        "completed_at": None,
        "latest_api_date": None,
        "latest_database_date": None,
        "records_received": 0,
        "records_accepted": 0,
        "records_rejected": 0,
        "predictions_replaced": 0,
        "rejection_reasons": {},
        "error": None
    }

    try:
        all_markets = {m.canonical_name: m for m in db.query(Market).all()}
        all_commodities = {c.canonical_name: c for c in db.query(Commodity).all()}
        max_api_date = None

        for comm_name, market_names in VALID_CROP_MARKET_MAP.items():
            if comm_name not in all_commodities:
                continue
            for mkt_name in market_names:
                if mkt_name not in all_markets:
                    continue

                res_map = fetch_date_range_records(
                    db=db,
                    commodity=comm_name,
                    market=mkt_name,
                    start_date=start_date,
                    end_date=today
                )
                report["records_accepted"] += len(res_map)
                if res_map:
                    latest_d = max(res_map.keys())
                    if max_api_date is None or latest_d > max_api_date:
                        max_api_date = latest_d

        report["status"] = "success"
        report["latest_api_date"] = max_api_date or today
        report["completed_at"] = get_ist_now()

    except Exception as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        logger.exception("Error during sync_latest_market_data: %s", exc)
    finally:
        if close_db:
            db.close()

    return report

