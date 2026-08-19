import os
import sys
import random
from datetime import datetime, date, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, engine, Base
from app.models import Market, Commodity, CleanedMarketPrice, ModelRun
from app.ml.dataset_builder import build_dataset_from_db, chronological_split
from app.ml.train import train_catboost_models

# Pair definitions: (Commodity, Market, District, Group, BaseMinPrice, BaseMaxPrice)
PAIR_CONFIGS = [
    # Paddy
    ('Paddy', 'Banaganapalli APMC', 'Nandyal', 'Cereals', 2150, 2400),
    ('Paddy', 'Atmakur (Nandyal District) APMC', 'Nandyal', 'Cereals', 2100, 2350),
    ('Paddy', 'Rajahmundry APMC', 'East Godavari', 'Cereals', 2200, 2450),
    ('Paddy', 'Tiruvuru APMC', 'NTR', 'Cereals', 2120, 2380),
    ('Paddy', 'Tanuku APMC', 'West Godavari', 'Cereals', 2220, 2480),
    ('Paddy', 'Sampara (Kakinada Rural) APMC', 'Kakinada', 'Cereals', 2180, 2420),

    # Maize
    ('Maize', 'Kurnool APMC', 'Kurnool', 'Cereals', 1850, 2150),
    ('Maize', 'Atmakur (Nandyal District) APMC', 'Nandyal', 'Cereals', 1820, 2100),
    ('Maize', 'Tiruvuru APMC', 'NTR', 'Cereals', 1880, 2160),
    ('Maize', 'Nandyal APMC', 'Nandyal', 'Cereals', 1840, 2120),
    ('Maize', 'Chintalapudi APMC', 'Eluru', 'Cereals', 1900, 2200),

    # Jowar
    ('Jowar', 'Banaganapalli APMC', 'Nandyal', 'Cereals', 2400, 2800),
    ('Jowar', 'Alur APMC', 'Kurnool', 'Cereals', 2350, 2750),

    # Groundnut
    ('Groundnut', 'Kurnool APMC', 'Kurnool', 'Oilseeds', 5800, 6600),
    ('Groundnut', 'Adoni APMC', 'Kurnool', 'Oilseeds', 5750, 6550),
    ('Groundnut', 'Kadapa APMC', 'YSR Kadapa', 'Oilseeds', 5600, 6400),
    ('Groundnut', 'Yemmiganuru APMC', 'Kurnool', 'Oilseeds', 5700, 6500),

    # Castor Seed
    ('Castor Seed', 'Kurnool APMC', 'Kurnool', 'Oilseeds', 5200, 5900),
    ('Castor Seed', 'Adoni APMC', 'Kurnool', 'Oilseeds', 5150, 5850),
    ('Castor Seed', 'Yemmiganuru APMC', 'Kurnool', 'Oilseeds', 5100, 5800),

    # Sunflower
    ('Sunflower', 'Kurnool APMC', 'Kurnool', 'Oilseeds', 4300, 4900),
    ('Sunflower', 'Adoni APMC', 'Kurnool', 'Oilseeds', 4250, 4850),

    # Bengal Gram
    ('Bengal Gram', 'Banaganapalli APMC', 'Nandyal', 'Pulses', 4800, 5500),
    ('Bengal Gram', 'Kurnool APMC', 'Kurnool', 'Pulses', 4850, 5600),

    # Red Gram
    ('Red Gram', 'Kurnool APMC', 'Kurnool', 'Pulses', 6800, 7800),
    ('Red Gram', 'Dhone APMC', 'Nandyal', 'Pulses', 6750, 7750),

    # Black Gram
    ('Black Gram', 'Kurnool APMC', 'Kurnool', 'Pulses', 6200, 7200),

    # Dry Chillies
    ('Dry Chillies', 'Guntur APMC', 'Guntur', 'Spices', 15000, 18500),
    ('Dry Chillies', 'Kurnool APMC', 'Kurnool', 'Spices', 14500, 17800),
    ('Dry Chillies', 'Piduguralla (Palnadu) APMC', 'Palnadu', 'Spices', 14800, 18000),
    ('Dry Chillies', 'Tiruvuru APMC', 'NTR', 'Spices', 14200, 17500),

    # Turmeric
    ('Turmeric', 'Duggirala APMC', 'Guntur', 'Spices', 8500, 11500),
    ('Turmeric', 'Kadapa APMC', 'YSR Kadapa', 'Spices', 8200, 11000),

    # Ajwan
    ('Ajwan', 'Kurnool APMC', 'Kurnool', 'Spices', 11000, 14000),

    # Tomato
    ('Tomato', 'Madanapalli APMC', 'Annamayya', 'Vegetables', 1400, 2400),
    ('Tomato', 'Kalikiri APMC', 'Annamayya', 'Vegetables', 1350, 2300),
    ('Tomato', 'Palamaner APMC', 'Chittoor', 'Vegetables', 1350, 2300),
    ('Tomato', 'Punganur APMC', 'Chittoor', 'Vegetables', 1380, 2350),
    ('Tomato', 'Anantapur APMC', 'Anantapur', 'Vegetables', 1420, 2450),
    ('Tomato', 'Pattikonda APMC', 'Kurnool', 'Vegetables', 1450, 2500),
    ('Tomato', 'Mulakalacheruvu APMC', 'Annamayya', 'Vegetables', 1320, 2250),
    ('Tomato', 'Valmikipuram APMC', 'Annamayya', 'Vegetables', 1360, 2320),
    ('Tomato', 'Somala APMC', 'Chittoor', 'Vegetables', 1340, 2280),
    ('Tomato', 'Kuppam APMC', 'Chittoor', 'Vegetables', 1300, 2200),

    # Onion
    ('Onion', 'Kurnool APMC', 'Kurnool', 'Vegetables', 1800, 2800),
    ('Onion', 'Pattikonda APMC', 'Kurnool', 'Vegetables', 1750, 2700),
    ('Onion', 'Adoni APMC', 'Kurnool', 'Vegetables', 1780, 2750),
    ('Onion', 'Yerraguntla APMC', 'YSR Kadapa', 'Vegetables', 1820, 2850),
    ('Onion', 'Rajahmundry APMC', 'East Godavari', 'Vegetables', 1850, 2900),
    ('Onion', 'Tenali APMC', 'Guntur', 'Vegetables', 1830, 2880),

    # Potato
    ('Potato', 'Palamaner APMC', 'Chittoor', 'Vegetables', 2100, 2600),
    ('Potato', 'Kurnool APMC', 'Kurnool', 'Vegetables', 2150, 2650),
    ('Potato', 'Rajahmundry APMC', 'East Godavari', 'Vegetables', 2200, 2700),
    ('Potato', 'Tenali APMC', 'Guntur', 'Vegetables', 2180, 2680),

    # Lemon
    ('Lemon', 'Tenali APMC', 'Guntur', 'Vegetables', 2850, 4300),
    ('Lemon', 'Gopalapuram APMC', 'East Godavari', 'Vegetables', 2800, 4200),
    ('Lemon', 'Chintalapudi APMC', 'Eluru', 'Vegetables', 2800, 4200),
    ('Lemon', 'Eluru APMC', 'Eluru', 'Vegetables', 2900, 4400),
    ('Lemon', 'Denduluru APMC', 'Eluru', 'Vegetables', 2880, 4350),

    # Vegetables
    ('Brinjal', 'Palamaner APMC', 'Chittoor', 'Vegetables', 1500, 2200),
    ('Cabbage', 'Palamaner APMC', 'Chittoor', 'Vegetables', 1200, 1800),
    ('Cauliflower', 'Palamaner APMC', 'Chittoor', 'Vegetables', 1600, 2500),
    ('Green Chilli', 'Palamaner APMC', 'Chittoor', 'Vegetables', 3200, 4500),
    ('Green Chilli', 'Parchur APMC', 'Bapatla', 'Vegetables', 3150, 4400),
    ('Cluster Beans', 'Palamaner APMC', 'Chittoor', 'Vegetables', 2200, 3100),
    ('Ridge Gourd', 'Palamaner APMC', 'Chittoor', 'Vegetables', 1800, 2600),
]

def seed_and_train():
    print("Starting DB Seeding for requested crops & markets up to current date...")
    db = SessionLocal()
    
    # 1. Ensure commodities and markets exist
    market_map = {}
    commodity_map = {}

    for c_name, m_name, dist, group, min_p, max_p in PAIR_CONFIGS:
        # Market
        m = db.query(Market).filter(Market.canonical_name == m_name).first()
        if not m:
            m = Market(
                canonical_name=m_name,
                original_name=m_name,
                district=dist,
                state="Andhra Pradesh",
                is_active=True
            )
            db.add(m)
            db.commit()
            db.refresh(m)
        market_map[m_name] = m

        # Commodity
        c = db.query(Commodity).filter(Commodity.canonical_name == c_name).first()
        if not c:
            c = Commodity(
                canonical_name=c_name,
                original_name=c_name,
                commodity_group=group,
                unit="₹ per quintal"
            )
            db.add(c)
            db.commit()
            db.refresh(c)
        commodity_map[c_name] = c

    # 2. Populate daily records from 2026-05-01 to 2026-08-15
    start_dt = date(2026, 5, 1)
    end_dt = date(2026, 8, 15)
    days_count = (end_dt - start_dt).days + 1

    records_to_insert = []

    for c_name, m_name, dist, group, base_min, base_max in PAIR_CONFIGS:
        m = market_map[m_name]
        c = commodity_map[c_name]

        random.seed(hash(f"{c_name}_{m_name}") % 100000)
        curr_price = (base_min + base_max) / 2.0

        for i in range(days_count):
            obs_date = start_dt + timedelta(days=i)
            
            # Check if record already exists
            existing = db.query(CleanedMarketPrice).filter(
                CleanedMarketPrice.market_id == m.id,
                CleanedMarketPrice.commodity_id == c.id,
                CleanedMarketPrice.observation_date == obs_date
            ).first()

            if existing:
                continue

            # Random daily fluctuation
            drift = random.uniform(-0.02, 0.02) * curr_price
            curr_price = max(base_min * 0.8, min(base_max * 1.2, curr_price + drift))
            modal_p = round(curr_price, 2)
            min_p = round(modal_p * random.uniform(0.92, 0.96), 2)
            max_p = round(modal_p * random.uniform(1.04, 1.08), 2)
            arr_qty = round(random.uniform(5.0, 120.0), 2)

            records_to_insert.append(CleanedMarketPrice(
                market_id=m.id,
                commodity_id=c.id,
                observation_date=obs_date,
                modal_price=modal_p,
                min_price=min_p,
                max_price=max_p,
                arrival_quantity=arr_qty,
                quality_status="Standard Grade"
            ))

    if records_to_insert:
        db.bulk_save_objects(records_to_insert)
        db.commit()
        print(f"Inserted {len(records_to_insert)} daily price observations into CleanedMarketPrice!")

    db.close()

    db = SessionLocal()
    # 3. Trigger CatBoost ML Training
    print("Building dataset from DB...")
    df_all = build_dataset_from_db(db)
    if not df_all.empty:
        train_df, test_df = chronological_split(df_all, train_end="2026-08-10", test_start="2026-08-11")
        model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Training CatBoost ML Models ({model_version}) on {len(df_all)} records...")
        metadata = train_catboost_models(train_df, test_df, model_version=model_version)
        
        db.query(ModelRun).update({"is_active": False})
        model_run = ModelRun(
            model_name="CatBoostRegressor Direct 3-Horizon",
            model_version=model_version,
            training_start_date=date(2026, 5, 1),
            training_end_date=date(2026, 8, 10),
            test_start_date=date(2026, 8, 11),
            test_end_date=date(2026, 8, 15),
            training_rows=len(train_df),
            metrics_json=metadata.get("metrics"),
            artifact_path=f"ml/models/catboost_h1_{model_version}.cbm",
            status="completed",
            is_active=True
        )
        db.add(model_run)
        db.commit()
        print(f"Training complete! Active ModelRun: {model_version}")
    else:
        print("Warning: Dataset empty!")
    db.close()

if __name__ == "__main__":
    seed_and_train()
