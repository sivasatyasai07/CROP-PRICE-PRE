import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Market, Commodity

logger = logging.getLogger(__name__)

APMC_MARKETS_SEED = [
    # Annamayya / Chittoor
    {"canonical_name": "Madanapalle APMC", "original_name": "Madanapalle", "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.5500, "longitude": 78.5000},
    {"canonical_name": "Kalikiri APMC", "original_name": "Kalikiri", "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.6833, "longitude": 78.7833},
    {"canonical_name": "Mulakalacheruvu APMC", "original_name": "Mulakalacheruvu", "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.9167, "longitude": 78.3333},
    {"canonical_name": "Valmikipuram APMC", "original_name": "Valmikipuram", "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.6667, "longitude": 78.6167},
    {"canonical_name": "Palamaner APMC", "original_name": "Palamaner", "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 13.2000, "longitude": 78.7500},
    {"canonical_name": "Punganur APMC", "original_name": "Punganur", "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 13.3667, "longitude": 78.5833},
    {"canonical_name": "Somala APMC", "original_name": "Somala", "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 13.4333, "longitude": 78.8500},
    {"canonical_name": "Kuppam APMC", "original_name": "Kuppam", "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 12.7500, "longitude": 78.3667},
    # Kurnool / Nandyal
    {"canonical_name": "Kurnool APMC", "original_name": "Kurnool", "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.8281, "longitude": 78.0373},
    {"canonical_name": "Pattikonda APMC", "original_name": "Pattikonda", "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.4000, "longitude": 77.5167},
    {"canonical_name": "Adoni APMC", "original_name": "Adoni", "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.6322, "longitude": 77.2728},
    {"canonical_name": "Alur APMC", "original_name": "Alur", "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.3000, "longitude": 77.2500},
    {"canonical_name": "Yemmiganuru APMC", "original_name": "Yemmiganuru", "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.7333, "longitude": 77.4833},
    {"canonical_name": "Banaganapalli APMC", "original_name": "Banaganapalli", "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.3167, "longitude": 78.2333},
    {"canonical_name": "Atmakur (Nandyal District) APMC", "original_name": "Atmakur (Nandyal District)", "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.8833, "longitude": 78.6000},
    {"canonical_name": "Nandyal APMC", "original_name": "Nandyal", "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.4833, "longitude": 78.4833},
    {"canonical_name": "Dhone APMC", "original_name": "Dhone", "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.4167, "longitude": 77.8667},
    # Anantapur / YSR Kadapa
    {"canonical_name": "Ananthapur APMC", "original_name": "Ananthapur", "district": "Anantapur", "state": "Andhra Pradesh", "latitude": 14.6819, "longitude": 77.6006},
    {"canonical_name": "Kadapa APMC", "original_name": "Kadapa", "district": "YSR Kadapa", "state": "Andhra Pradesh", "latitude": 14.4673, "longitude": 78.8242},
    {"canonical_name": "Yerraguntla APMC", "original_name": "Yerraguntla", "district": "YSR Kadapa", "state": "Andhra Pradesh", "latitude": 14.6333, "longitude": 78.5333},
    # Coastal Andhra / Godavari / Guntur / Krishna / Palnadu / Bapatla / Eluru
    {"canonical_name": "Rajahmundry APMC", "original_name": "Rajahmundry", "district": "East Godavari", "state": "Andhra Pradesh", "latitude": 17.0005, "longitude": 81.8040},
    {"canonical_name": "Gopalapuram APMC", "original_name": "Gopalapuram", "district": "East Godavari", "state": "Andhra Pradesh", "latitude": 17.1000, "longitude": 81.5333},
    {"canonical_name": "Tenali APMC", "original_name": "Tenali", "district": "Guntur", "state": "Andhra Pradesh", "latitude": 16.2430, "longitude": 80.6400},
    {"canonical_name": "Guntur APMC", "original_name": "Guntur", "district": "Guntur", "state": "Andhra Pradesh", "latitude": 16.3067, "longitude": 80.4365},
    {"canonical_name": "Eluru APMC", "original_name": "Eluru", "district": "Eluru", "state": "Andhra Pradesh", "latitude": 16.7107, "longitude": 81.0952},
    {"canonical_name": "Chintalapudi APMC", "original_name": "Chintalapudi", "district": "Eluru", "state": "Andhra Pradesh", "latitude": 17.0667, "longitude": 80.9833},
    {"canonical_name": "Denduluru APMC", "original_name": "Denduluru", "district": "Eluru", "state": "Andhra Pradesh", "latitude": 16.7833, "longitude": 81.1500},
    {"canonical_name": "Parchur APMC", "original_name": "Parchur", "district": "Bapatla", "state": "Andhra Pradesh", "latitude": 15.9667, "longitude": 80.2667},
    {"canonical_name": "Tiruvuru APMC", "original_name": "Tiruvuru", "district": "NTR", "state": "Andhra Pradesh", "latitude": 17.1167, "longitude": 80.6167},
    {"canonical_name": "Tanuku APMC", "original_name": "Tanuku", "district": "West Godavari", "state": "Andhra Pradesh", "latitude": 16.7565, "longitude": 81.6811},
    {"canonical_name": "Sampara (Kakinada Rural) APMC", "original_name": "Sampara (Kakinada Rural)", "district": "Kakinada", "state": "Andhra Pradesh", "latitude": 16.9500, "longitude": 82.2000},
    {"canonical_name": "Pidugurala (Palnadu) APMC", "original_name": "Pidugurala (Palnadu)", "district": "Palnadu", "state": "Andhra Pradesh", "latitude": 16.4833, "longitude": 79.8833},
]

COMMODITIES_SEED = [
    {"canonical_name": "Tomato", "original_name": "Tomato", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 1400.0},
    {"canonical_name": "Onion", "original_name": "Onion", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 2200.0},
    {"canonical_name": "Potato", "original_name": "Potato", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 1850.0},
    {"canonical_name": "Lemon", "original_name": "Lemon", "commodity_group": "Fruits", "unit": "Rs./Quintal", "base_price": 3200.0},
    {"canonical_name": "Brinjal", "original_name": "Brinjal", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 1600.0},
    {"canonical_name": "Cabbage", "original_name": "Cabbage", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 1200.0},
    {"canonical_name": "Cauliflower", "original_name": "Cauliflower", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 1900.0},
    {"canonical_name": "Green Chilli", "original_name": "Green Chilli", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 3500.0},
    {"canonical_name": "Cluster Beans", "original_name": "Cluster Beans", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 2400.0},
    {"canonical_name": "Ridgeguard", "original_name": "Ridgeguard", "commodity_group": "Vegetables", "unit": "Rs./Quintal", "base_price": 2100.0},
    {"canonical_name": "Paddy", "original_name": "Paddy(Dhan)(Common)", "commodity_group": "Cereals", "unit": "Rs./Quintal", "base_price": 2300.0},
    {"canonical_name": "Maize", "original_name": "Maize", "commodity_group": "Cereals", "unit": "Rs./Quintal", "base_price": 2150.0},
    {"canonical_name": "Jowar", "original_name": "Jowar(Sorghum)", "commodity_group": "Cereals", "unit": "Rs./Quintal", "base_price": 2800.0},
    {"canonical_name": "Groundnut", "original_name": "Groundnut", "commodity_group": "Oilseeds", "unit": "Rs./Quintal", "base_price": 6500.0},
    {"canonical_name": "Castor Seed", "original_name": "Castor Seed", "commodity_group": "Oilseeds", "unit": "Rs./Quintal", "base_price": 5800.0},
    {"canonical_name": "Sunflower", "original_name": "Sunflower", "commodity_group": "Oilseeds", "unit": "Rs./Quintal", "base_price": 4900.0},
    {"canonical_name": "Bengal Gram", "original_name": "Bengal Gram(Gram)(Whole)", "commodity_group": "Pulses", "unit": "Rs./Quintal", "base_price": 5400.0},
    {"canonical_name": "Red Gram", "original_name": "Arhar (Tur/Red Gram)(Whole)", "commodity_group": "Pulses", "unit": "Rs./Quintal", "base_price": 7200.0},
    {"canonical_name": "Black Gram", "original_name": "Black Gram (Urd Beans)(Whole)", "commodity_group": "Pulses", "unit": "Rs./Quintal", "base_price": 6800.0},
    {"canonical_name": "Dry Chillies", "original_name": "Dry Chillies", "commodity_group": "Spices", "unit": "Rs./Quintal", "base_price": 18500.0},
    {"canonical_name": "Ajwan", "original_name": "Ajwan", "commodity_group": "Spices", "unit": "Rs./Quintal", "base_price": 14200.0},
]


def seed_markets_and_commodities(db: Session = None):
    """
    Seeds all verified APMC markets and agricultural commodities with coordinates and defaults.
    """
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        # 1. Seed Markets
        for m_data in APMC_MARKETS_SEED:
            existing = db.query(Market).filter(
                (Market.canonical_name == m_data["canonical_name"]) |
                (Market.original_name == m_data["original_name"])
            ).first()

            if existing:
                if existing.latitude is None or existing.longitude is None or not existing.district:
                    existing.latitude = m_data["latitude"]
                    existing.longitude = m_data["longitude"]
                    existing.district = m_data["district"]
                    existing.state = m_data["state"]
                    existing.is_active = True
            else:
                new_m = Market(
                    canonical_name=m_data["canonical_name"],
                    original_name=m_data["original_name"],
                    district=m_data["district"],
                    state=m_data["state"],
                    latitude=m_data["latitude"],
                    longitude=m_data["longitude"],
                    is_active=True
                )
                db.add(new_m)

        # 2. Seed Commodities
        for c_data in COMMODITIES_SEED:
            existing_c = db.query(Commodity).filter(
                (Commodity.canonical_name == c_data["canonical_name"]) |
                (Commodity.original_name == c_data["original_name"])
            ).first()

            if not existing_c:
                new_c = Commodity(
                    canonical_name=c_data["canonical_name"],
                    original_name=c_data["original_name"],
                    commodity_group=c_data["commodity_group"],
                    unit=c_data["unit"],
                    is_active=True
                )
                db.add(new_c)

        db.commit()
        logger.info("[SEED] Successfully seeded APMC markets and commodities.")
    except Exception as exc:
        db.rollback()
        logger.error("[SEED] Error seeding markets and commodities: %s", exc)
    finally:
        if close_after:
            db.close()
