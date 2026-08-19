import random
import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Market, Commodity, CleanedMarketPrice, OfficialMarketPrice
from app.services.official_market_service import fetch_date_range_prices
from app.utils.holidays import check_market_holiday

# Full List of Valid Crop-Market Mapping Constraints
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
    ]
}


def sync_all_crop_prices_on_startup(db: Session = None):
    """
    Automatic startup routine executed every time the backend server runs.
    Ensures official price observations are fetched from the API and stored up-to-date
    (up to current date) for every valid crop and related market in the system.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        today = datetime.date.today()
        start_fetch_date = today - datetime.timedelta(days=7)
        print(f"\n========================================================")
        print(f"[*] STARTUP AUTOMATED PRICE SYNC: Syncing up to {today}...")
        print(f"========================================================")

        total_synced = 0
        total_api_records = 0
        total_created = 0

        # Retrieve all markets and commodities
        all_markets = {m.canonical_name: m for m in db.query(Market).all()}
        all_commodities = {c.canonical_name: c for c in db.query(Commodity).all()}

        for comm_name, market_names in VALID_CROP_MARKET_MAP.items():
            comm_obj = all_commodities.get(comm_name)
            if not comm_obj:
                continue

            for mkt_name in market_names:
                mkt_obj = all_markets.get(mkt_name)
                if not mkt_obj:
                    continue

                # 1. Fetch live official API data from start_fetch_date up to today
                api_results = fetch_date_range_prices(
                    db=db,
                    commodity=comm_name,
                    market=mkt_name,
                    start_date=start_fetch_date,
                    end_date=today
                )
                total_api_records += len(api_results)

                # 2. Check latest CleanedMarketPrice in local DB
                latest_rec = db.query(CleanedMarketPrice).filter(
                    CleanedMarketPrice.market_id == mkt_obj.id,
                    CleanedMarketPrice.commodity_id == comm_obj.id
                ).order_by(CleanedMarketPrice.observation_date.desc()).first()

                last_date = latest_rec.observation_date if latest_rec else (today - datetime.timedelta(days=7))
                last_price = float(latest_rec.modal_price) if latest_rec else 2000.0

                # 3. Store verified API observations into CleanedMarketPrice
                for curr_date, norm in api_results.items():
                    existing_cleaned = db.query(CleanedMarketPrice).filter(
                        CleanedMarketPrice.market_id == mkt_obj.id,
                        CleanedMarketPrice.commodity_id == comm_obj.id,
                        CleanedMarketPrice.observation_date == curr_date
                    ).first()

                    if not existing_cleaned:
                        new_rec = CleanedMarketPrice(
                            market_id=mkt_obj.id,
                            commodity_id=comm_obj.id,
                            observation_date=curr_date,
                            min_price=norm['min_price'],
                            modal_price=norm['modal_price'],
                            max_price=norm['max_price'],
                            arrival_quantity=norm['arrival_quantity'],
                            unit=comm_obj.unit or "₹ per quintal"
                        )
                        db.add(new_rec)
                        total_created += 1

                total_synced += 1

        db.commit()
        print(f"[OK] STARTUP PRICE SYNC COMPLETE: Processed {total_synced} crop-market pairs up to {today}.")
        print(f"     Official API Records Fetched: {total_api_records} | Local Records Updated/Created: {total_created}")
        print(f"========================================================\n")

    except Exception as e:
        db.rollback()
        print(f"[!] Warning during startup price sync: {e}")
    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    sync_all_crop_prices_on_startup()
