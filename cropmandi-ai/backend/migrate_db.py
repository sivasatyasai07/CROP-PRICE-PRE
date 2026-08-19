import sqlite3
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "cropmandi.db"

def migrate():
    print(f"Migrating database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns = [
        ("official_market_prices", "last_verified_at", "DATETIME"),
        ("official_market_prices", "data_status", "VARCHAR(50) DEFAULT 'fresh_official'"),
        ("official_market_prices", "verification_status", "VARCHAR(50) DEFAULT 'verified'"),
        ("predictions", "superseded_by_official", "BOOLEAN DEFAULT 0"),
        ("predictions", "official_record_id", "INTEGER"),
        ("markets", "coordinate_source", "VARCHAR(100) DEFAULT 'official_registry'")
    ]

    for tbl, col, typ in columns:
        try:
            cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {typ};")
            print(f"Added {col} to {tbl}")
        except Exception as e:
            print(f"{tbl}.{col}: {e}")

    conn.commit()
    conn.close()
    print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate()
