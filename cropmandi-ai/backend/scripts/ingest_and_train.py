import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add app to python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine, Base
from app.models.entities import Market, Commodity, CleanedMarketPrice, WeatherObservation
from app.ml.dataset_builder import build_dataset_from_db, chronological_split
from app.ml.train import train_catboost_models

def ingest_csv_data(csv_path: str):
    print(f"Reading CSV dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    if 'Market' not in df.columns:
        print("Header row offset detected, reading with header=1...")
        df = pd.read_csv(csv_path, header=1)
    
    # Normalize dynamic column names like 'Modal Price 01-01-2021 to 11-08-2026'
    col_rename = {}
    for col in df.columns:
        if 'Arrival Quantity' in col:
            col_rename[col] = 'Arrival Quantity'
        elif 'Min Price' in col:
            col_rename[col] = 'Min Price'
        elif 'Modal Price' in col:
            col_rename[col] = 'Modal Price'
        elif 'Max Price' in col:
            col_rename[col] = 'Max Price'
    if col_rename:
        df = df.rename(columns=col_rename)

    print(f"Total raw rows: {len(df)}")

    # Drop missing essential rows
    df = df.dropna(subset=['Market', 'Commodity', 'Date', 'Modal Price'])
    print(f"Rows after dropping missing essential columns: {len(df)}")

    db = SessionLocal()

    try:
        # 1. Ingest Markets
        state_col = 'State/UT' if 'State/UT' in df.columns else 'State'
        market_district_map = df[['Market', 'District', state_col]].drop_duplicates()
        market_lookup = {}
        for _, row in market_district_map.iterrows():
            mkt_name = str(row['Market']).strip()
            dist_name = str(row['District']).strip() if pd.notna(row['District']) else "Andhra Pradesh"
            state_name = str(row[state_col]).strip() if pd.notna(row[state_col]) else "Andhra Pradesh"

            mkt = db.query(Market).filter(Market.canonical_name == mkt_name).first()
            if not mkt:
                mkt = Market(
                    canonical_name=mkt_name,
                    original_name=mkt_name,
                    district=dist_name,
                    state=state_name,
                    is_active=True
                )
                db.add(mkt)
                db.commit()
                db.refresh(mkt)
                print(f"Added Market: {mkt_name} ({dist_name})")
            market_lookup[mkt_name] = mkt.id

        # 2. Ingest Commodities
        commodity_map = df[['Commodity', 'Commodity Group']].drop_duplicates()
        commodity_lookup = {}
        for _, row in commodity_map.iterrows():
            comm_name = str(row['Commodity']).strip()
            comm_group = str(row['Commodity Group']).strip() if pd.notna(row['Commodity Group']) else "Vegetables"

            comm = db.query(Commodity).filter(Commodity.canonical_name == comm_name).first()
            if not comm:
                comm = Commodity(
                    canonical_name=comm_name,
                    original_name=comm_name,
                    commodity_group=comm_group,
                    unit="₹ per quintal",
                    is_active=True
                )
                db.add(comm)
                db.commit()
                db.refresh(comm)
                print(f"Added Commodity: {comm_name}")
            commodity_lookup[comm_name] = comm.id

        # 3. Parse Dates & Numerical fields
        df['observation_date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce').dt.date
        df = df.dropna(subset=['observation_date'])

        # Prepare records for insertion
        cleaned_records = []
        existing_keys = set(
            db.query(CleanedMarketPrice.market_id, CleanedMarketPrice.commodity_id, CleanedMarketPrice.observation_date).all()
        )
        print(f"Existing records in DB: {len(existing_keys)}")

        new_count = 0
        for _, row in df.iterrows():
            m_id = market_lookup.get(str(row['Market']).strip())
            c_id = commodity_lookup.get(str(row['Commodity']).strip())
            o_date = row['observation_date']

            if not m_id or not c_id:
                continue

            key = (m_id, c_id, o_date)
            if key in existing_keys:
                continue

            arr_qty = float(row['Arrival Quantity']) if pd.notna(row['Arrival Quantity']) else 0.0
            min_p = float(row['Min Price']) if pd.notna(row['Min Price']) else float(row['Modal Price'])
            mod_p = float(row['Modal Price'])
            max_p = float(row['Max Price']) if pd.notna(row['Max Price']) else float(row['Modal Price'])

            cleaned_records.append({
                "market_id": m_id,
                "commodity_id": c_id,
                "observation_date": o_date,
                "arrival_quantity": arr_qty,
                "min_price": min_p,
                "modal_price": mod_p,
                "max_price": max_p,
                "unit": "₹ per quintal",
                "quality_status": "valid"
            })
            existing_keys.add(key)
            new_count += 1

        print(f"New unique price records to insert: {new_count}")

        if cleaned_records:
            # Batch insert
            batch_size = 2000
            for i in range(0, len(cleaned_records), batch_size):
                batch = cleaned_records[i:i + batch_size]
                db.bulk_insert_mappings(CleanedMarketPrice, batch)
                db.commit()
                print(f"Inserted batch {i // batch_size + 1}/{(len(cleaned_records) + batch_size - 1) // batch_size}")

        print("Database Ingestion Complete.")

        # 4. Rebuild Dataset & Train CatBoost Models
        print("\n--- Rebuilding Feature Dataset & Training CatBoost Models ---")
        df_all = build_dataset_from_db(db)
        print(f"Full Feature Dataset Shape: {df_all.shape}")

        if df_all.empty:
            print("Dataset empty after feature building!")
            return

        train_df, test_df = chronological_split(df_all, train_end="2025-06-30", test_start="2025-07-01")
        print(f"Train set shape: {train_df.shape}, Test set shape: {test_df.shape}")

        metadata = train_catboost_models(
            train_df=train_df,
            test_df=test_df,
            model_version="1.1.0",
            iterations=600,
            learning_rate=0.04
        )

        print("\nCatBoost Models Successfully Trained and Saved!")
        print(f"Metrics: {metadata.get('metrics')}")

    except Exception as e:
        db.rollback()
        print(f"Error during ingestion/training: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    csv_file = r"c:\Users\sivas\OneDrive\Desktop\ghfh\All_Type_of_Report_(All_Grades)_14-08-2026_11-51-59_AM.csv"
    ingest_csv_data(csv_file)
