import os
import csv
import logging
import threading
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel

from app.config import settings
from app.utils.market_normalization import normalize_commodity_name, normalize_market_name

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_master_index: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
_is_loaded = False
_stats = {
    "total_rows_loaded": 0,
    "unique_keys": 0,
    "duplicates_found": 0,
    "date_range": ("", ""),
    "loaded_at": ""
}


class MasterRecordResult:
    def __init__(self, record: Optional[Dict[str, Any]] = None, status: str = "not_found", is_valid: bool = False):
        self.record = record
        self.status = status
        self.is_valid = is_valid


def get_master_data_path() -> str:
    path = getattr(settings, "MASTER_DATA_PATH", "data/master-data.csv")
    if not os.path.isabs(path):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base_dir, path)
    return path


def parse_csv_date(date_str: str) -> Optional[str]:
    """Parses various CSV date formats (DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY) into ISO YYYY-MM-DD."""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def normalize_master_columns(headers: List[str]) -> Dict[str, str]:
    """Maps CSV column headers to standardized internal field names."""
    mapping = {}
    for h in headers:
        clean = h.strip().lower()
        if "state" in clean:
            mapping[h] = "state"
        elif "district" in clean:
            mapping[h] = "district"
        elif "market" in clean:
            mapping[h] = "market"
        elif "commodity group" in clean:
            mapping[h] = "commodity_group"
        elif "commodity" in clean:
            mapping[h] = "commodity"
        elif "date" in clean:
            mapping[h] = "date"
        elif "arrival quantity" in clean:
            mapping[h] = "arrival_quantity"
        elif "arrival unit" in clean:
            mapping[h] = "arrival_unit"
        elif "modal price" in clean:
            mapping[h] = "modal_price"
        elif "price unit" in clean:
            mapping[h] = "price_unit"
    return mapping


def validate_master_record(record: Dict[str, Any]) -> bool:
    """Validates that a master CSV record has required non-negative modal price and valid date."""
    if not record:
        return False
    modal_p = record.get("modal_price")
    if modal_p is None:
        return False
    try:
        f_price = float(modal_p)
        if f_price <= 0:
            return False
    except (ValueError, TypeError):
        return False
    
    if not record.get("date") or not record.get("commodity") or not record.get("market"):
        return False
    return True


def normalize_master_record(raw_dict: Dict[str, Any], col_map: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Standardizes a single raw CSV row into normalized dictionary."""
    normalized: Dict[str, Any] = {
        "state": "",
        "district": "",
        "market": "",
        "commodity_group": "",
        "commodity": "",
        "date": "",
        "arrival_quantity": None,
        "arrival_unit": "Metric Tonnes",
        "modal_price": None,
        "price_unit": "Rs./Quintal"
    }

    for raw_k, val in raw_dict.items():
        std_k = col_map.get(raw_k)
        if not std_k:
            continue
        v_str = str(val).strip() if val is not None else ""
        if std_k == "date":
            parsed_d = parse_csv_date(v_str)
            normalized["date"] = parsed_d if parsed_d else v_str
        elif std_k in ("modal_price", "arrival_quantity"):
            try:
                # remove currency symbols or commas
                clean_num = v_str.replace(",", "").replace("Rs.", "").replace("₹", "").strip()
                normalized[std_k] = float(clean_num) if clean_num else None
            except (ValueError, TypeError):
                normalized[std_k] = None
        else:
            normalized[std_k] = v_str

    if not validate_master_record(normalized):
        return None
    return normalized


def load_master_data(force_reload: bool = False) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
    """
    Loads `master-data.csv` once into an in-memory index `(canonical_commodity, canonical_market, YYYY-MM-DD)`.
    Thread-safe and optimized for O(1) exact lookups.
    """
    global _master_index, _is_loaded, _stats
    with _lock:
        if _is_loaded and not force_reload:
            return _master_index

        path = get_master_data_path()
        if not os.path.exists(path):
            logger.warning("master-data.csv not found at: %s", path)
            _master_index = {}
            _is_loaded = True
            return _master_index

        index: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        total_rows = 0
        duplicates = 0
        min_date = ""
        max_date = ""

        try:
            with open(path, mode="r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    logger.error("Empty or invalid master-data.csv header.")
                    _master_index = {}
                    _is_loaded = True
                    return _master_index

                col_map = normalize_master_columns(reader.fieldnames)

                for row in reader:
                    total_rows += 1
                    rec = normalize_master_record(row, col_map)
                    if not rec:
                        continue

                    comm_norm = normalize_commodity_name(rec["commodity"])
                    mkt_norm = normalize_market_name(rec["market"])
                    rec_date = rec["date"]

                    key = (comm_norm.lower(), mkt_norm.lower(), rec_date)

                    if key in index:
                        duplicates += 1
                        # Documented duplicate resolution: keep row with latest price / higher arrival quantity
                        existing = index[key]
                        if (rec["arrival_quantity"] or 0) >= (existing["arrival_quantity"] or 0):
                            index[key] = rec
                    else:
                        index[key] = rec

                    # Track date range
                    if not min_date or rec_date < min_date:
                        min_date = rec_date
                    if not max_date or rec_date > max_date:
                        max_date = rec_date

            _master_index = index
            _is_loaded = True
            _stats = {
                "total_rows_loaded": total_rows,
                "unique_keys": len(index),
                "duplicates_found": duplicates,
                "date_range": (min_date, max_date),
                "loaded_at": datetime.now().isoformat()
            }
            logger.info("Successfully loaded master-data.csv: %d records, %d unique keys, range [%s to %s]",
                        total_rows, len(index), min_date, max_date)
        except Exception as exc:
            logger.exception("Failed to load master-data.csv: %s", exc)
            _master_index = {}
            _is_loaded = True

        return _master_index


def reload_master_data() -> Dict[str, Any]:
    """Forces reloading of the master data CSV."""
    load_master_data(force_reload=True)
    return get_master_data_stats()


def get_master_data_stats() -> Dict[str, Any]:
    """Returns runtime statistics of the loaded master dataset."""
    if not _is_loaded:
        load_master_data()
    return _stats


def find_exact_master_record(
    commodity: Optional[str] = None,
    market: Optional[str] = None,
    target_date: Optional[Any] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    *args,
    **kwargs
) -> MasterRecordResult:
    """
    Finds exact matching record in master-data.csv for commodity, market, and date.
    Supports both:
      find_exact_master_record(commodity="Tomato", market="Madanapalli APMC", target_date=..., state=..., district=...)
      find_exact_master_record(state, district, commodity, market, target_date)
    """
    if not _is_loaded:
        load_master_data()

    # Check positional args: if 5 positional args passed: state, district, commodity, market, target_date
    if len(args) == 2 and commodity and market and target_date:
        req_state = commodity
        req_district = market
        req_commodity = str(target_date)
        req_market = args[0]
        req_target_date = args[1]
    else:
        req_commodity = commodity or kwargs.get("commodity", "")
        req_market = market or kwargs.get("market", "")
        req_target_date = target_date or kwargs.get("target_date")
        req_state = state or kwargs.get("state")
        req_district = district or kwargs.get("district")

    # Normalize date
    if isinstance(req_target_date, date):
        date_str = req_target_date.strftime("%Y-%m-%d")
    elif isinstance(req_target_date, str):
        parsed = parse_csv_date(req_target_date)
        date_str = parsed if parsed else req_target_date.strip()
    else:
        date_str = str(req_target_date)

    comm_canonical = normalize_commodity_name(req_commodity).lower()
    mkt_canonical = normalize_market_name(req_market).lower()

    key = (comm_canonical, mkt_canonical, date_str)
    record = _master_index.get(key)

    if record:
        return MasterRecordResult(
            record=record,
            status="found_in_master_csv",
            is_valid=validate_master_record(record)
        )
    return MasterRecordResult(
        record=None,
        status="not_found_in_master_csv",
        is_valid=False
    )


def find_latest_master_record(
    commodity: str,
    market: str,
    max_date: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Finds the latest available recorded row in master-data.csv on or before max_date.
    """
    if not _is_loaded:
        load_master_data()

    comm_canonical = normalize_commodity_name(commodity).lower()
    mkt_canonical = normalize_market_name(market).lower()

    max_d_str = None
    if max_date:
        if isinstance(max_date, date):
            max_d_str = max_date.strftime("%Y-%m-%d")
        elif isinstance(max_date, str):
            parsed = parse_csv_date(max_date)
            max_d_str = parsed if parsed else max_date.strip()

    matching_dates = []
    for (c, m, d_str) in _master_index.keys():
        if c == comm_canonical and m == mkt_canonical:
            if max_d_str is None or d_str <= max_d_str:
                matching_dates.append(d_str)

    if not matching_dates:
        return None

    matching_dates.sort(reverse=True)
    best_date = matching_dates[0]
    return _master_index.get((comm_canonical, mkt_canonical, best_date))


# Alias
find_exact_record = find_exact_master_record

