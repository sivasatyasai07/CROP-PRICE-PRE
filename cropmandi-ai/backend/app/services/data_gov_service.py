import httpx
import json
from sqlalchemy.orm import Session
from app.config import settings
from app.models import RawMarketPrice
from typing import List, Dict, Any, Optional

def fetch_data_gov_prices(
    db: Session,
    state: str = "Andhra Pradesh",
    limit: int = 1000,
    offset: int = 0
) -> List[RawMarketPrice]:
    api_key = settings.DATA_GOV_API_KEY
    resource_id = settings.DATA_GOV_RESOURCE_ID
    
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("DATA_GOV_API_KEY is missing or invalid.")

    # Remove leading slash if needed
    res_path = resource_id.lstrip("/")
    url = f"{settings.DATA_GOV_BASE_URL}/{res_path}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CropMandi/1.0 (Agricultural Intelligence)"
    }

    params = {
        "api-key": api_key,
        "format": "json",
        "limit": limit,
        "offset": offset,
    }
    if state:
        params["filters[state]"] = state

    try:
        response = httpx.get(url, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise RuntimeError(f"Error fetching data from data.gov.in: {str(e)}")

    records = data.get("records", [])
    raw_records = []
    
    for idx, rec in enumerate(records):
        st = rec.get("state") or rec.get("State") or state
        dist = rec.get("district") or rec.get("District") or ""
        mkt = rec.get("market") or rec.get("Market") or ""
        comm = rec.get("commodity") or rec.get("Commodity") or ""
        c_group = rec.get("commodity_group") or rec.get("Commodity_Group") or "Vegetables"
        obs_date = rec.get("arrival_date") or rec.get("Arrival_Date") or rec.get("date") or rec.get("Date") or ""
        arr_qty = rec.get("arrival_quantity") or rec.get("Arrival_Quantity") or ""
        min_p = rec.get("min_price") or rec.get("Min_Price") or ""
        mod_p = rec.get("modal_price") or rec.get("Modal_Price") or ""
        max_p = rec.get("max_price") or rec.get("Max_Price") or ""

        raw_obj = RawMarketPrice(
            source="data_gov_api",
            source_record_id=str(rec.get("id") or rec.get("Id") or f"api_{offset+idx+1}"),
            state=str(st),
            district=str(dist),
            original_market=str(mkt),
            original_commodity=str(comm),
            commodity_group=str(c_group),
            observation_date=str(obs_date),
            arrival_quantity_raw=str(arr_qty),
            min_price_raw=str(min_p),
            modal_price_raw=str(mod_p),
            max_price_raw=str(max_p),
            raw_payload=json.dumps(rec)
        )
        raw_records.append(raw_obj)

    if raw_records:
        db.bulk_save_objects(raw_records)
        db.commit()

    return raw_records
