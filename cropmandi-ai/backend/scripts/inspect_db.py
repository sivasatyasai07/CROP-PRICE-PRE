import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "cropmandi.db"
conn = sqlite3.connect(str(DB_PATH))
c = conn.cursor()

c.execute("SELECT id, canonical_name FROM commodities")
commodities = c.fetchall()
print("COMMODITIES:", commodities)

c.execute("SELECT id, canonical_name, district, state, latitude, longitude FROM markets WHERE state LIKE '%Andhra%'")
markets = c.fetchall()
print(f"AP MARKETS ({len(markets)} total):")
for m in markets[:20]:
    print(m)

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("TABLES:", tables)

for t in tables:
    tname = t[0]
    c.execute(f"SELECT COUNT(*) FROM {tname}")
    cnt = c.fetchone()[0]
    print(f"Table {tname}: {cnt} rows")

c.execute("""
    SELECT c.canonical_name, m.canonical_name, COUNT(*) 
    FROM cleaned_market_prices p
    JOIN commodities c ON p.commodity_id = c.id
    JOIN markets m ON p.market_id = m.id
    GROUP BY c.canonical_name, m.canonical_name
    ORDER BY c.canonical_name, COUNT(*) DESC
""")
records = c.fetchall()
print(f"\nTOP COMMODITY-MARKET PAIRS IN cleaned_market_prices ({len(records)} total pairs):")
for r in records[:60]:
    print(r)

conn.close()
