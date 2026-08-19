import sqlite3
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATHS = [
    ROOT_DIR / "cropmandi.db",
    ROOT_DIR / "backend" / "cropmandi.db"
]

def migrate_db(db_path):
    if not os.path.exists(db_path):
        return

    print(f"Migrating schema for: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(predictions)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Existing columns: {columns}")

    needed_columns = [
        ("forecast_origin_date", "DATE"),
        ("price_source", "VARCHAR(50) DEFAULT 'predicted'"),
        ("model_version", "VARCHAR(50) DEFAULT 'catboost-v2'"),
        ("feature_snapshot_id", "VARCHAR(100)"),
        ("superseded_by_official", "BOOLEAN DEFAULT 0"),
        ("superseded_by_prediction_id", "INTEGER"),
        ("input_data_timestamp", "DATETIME"),
        ("weather_data_timestamp", "DATETIME"),
        ("arrival_data_timestamp", "DATETIME"),
        ("generated_at", "DATETIME"),
        ("updated_at", "DATETIME"),
    ]

    for col_name, col_type in needed_columns:
        if col_name not in columns:
            print(f"Adding column '{col_name}' ({col_type})...")
            try:
                cursor.execute(f"ALTER TABLE predictions ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Notice: {e}")

    if "prediction_date" in columns and "forecast_origin_date" in columns:
        cursor.execute("UPDATE predictions SET forecast_origin_date = prediction_date WHERE forecast_origin_date IS NULL")

    conn.commit()
    conn.close()

def main():
    for p in DB_PATHS:
        migrate_db(p)
    print("Migration finished.")

if __name__ == "__main__":
    main()
