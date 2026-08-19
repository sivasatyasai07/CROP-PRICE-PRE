import sys
import os
from pathlib import Path

# Add backend root to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal
from app.models import Market
from app.utils.geolocation import validate_coordinates

def validate_all_market_coordinates():
    db = SessionLocal()
    try:
        markets = db.query(Market).filter(Market.is_active == True).all()
        total_markets = len(markets)

        valid_markets = []
        missing_coordinates = []
        invalid_coordinates = []
        suspicious_coordinates = []
        seen_coordinates = {}
        duplicate_coordinates = []

        # India bounding box roughly: Lat 6.5 to 37.5, Lon 68.0 to 97.5
        # Andhra Pradesh bounding box roughly: Lat 12.5 to 19.5, Lon 76.5 to 84.8
        for m in markets:
            lat = m.latitude
            lon = m.longitude

            if lat is None or lon is None:
                missing_coordinates.append(m)
                continue

            if not validate_coordinates(lat, lon):
                invalid_coordinates.append((m, f"Invalid format/values: lat={lat}, lon={lon}"))
                continue

            # Suspicious check (outside India bounds or 0.0)
            if not (6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0):
                suspicious_coordinates.append((m, f"Outside India geographical bounds: lat={lat}, lon={lon}"))

            # Duplicate check
            coord_key = (round(lat, 4), round(lon, 4))
            if coord_key in seen_coordinates:
                duplicate_coordinates.append((m, seen_coordinates[coord_key], coord_key))
            else:
                seen_coordinates[coord_key] = m

            valid_markets.append(m)

        print("=" * 60)
        print(" APMC MANDI MARKET COORDINATE AUDIT REPORT")
        print("=" * 60)
        print(f"Total Active Configured Markets : {total_markets}")
        print(f"Markets with Valid Coordinates  : {len(valid_markets)}")
        print(f"Markets with Missing Coordinates: {len(missing_coordinates)}")
        print(f"Markets with Invalid Coordinates: {len(invalid_coordinates)}")
        print(f"Duplicate Coordinate Sets       : {len(duplicate_coordinates)}")
        print(f"Suspicious Out-of-Bound Coords  : {len(suspicious_coordinates)}")
        print("-" * 60)

        if valid_markets:
            print("\nSample Valid Configured Markets with Distance Readiness:")
            for m in valid_markets[:15]:
                print(f"  * [{m.id}] {m.canonical_name:<40} ({m.district}, {m.state}) -> Lat: {m.latitude:.4f}, Lon: {m.longitude:.4f}")

        if missing_coordinates:
            print(f"\nMissing Coordinates Sample ({len(missing_coordinates)} total):")
            for m in missing_coordinates[:10]:
                print(f"  [MISSING] [{m.id}] {m.canonical_name} ({m.district}, {m.state})")

        if invalid_coordinates:
            print("\nInvalid Coordinates:")
            for m, reason in invalid_coordinates:
                print(f"  [INVALID] [{m.id}] {m.canonical_name}: {reason}")

        if duplicate_coordinates:
            print("\nDuplicate Coordinates:")
            for m1, m2, coord in duplicate_coordinates[:5]:
                print(f"  [DUPLICATE] Coords {coord} shared by '{m1.canonical_name}' and '{m2.canonical_name}'")

        print("=" * 60)
        return {
            "total": total_markets,
            "valid": len(valid_markets),
            "missing": len(missing_coordinates),
            "invalid": len(invalid_coordinates),
            "duplicates": len(duplicate_coordinates),
            "suspicious": len(suspicious_coordinates)
        }

    finally:
        db.close()

if __name__ == "__main__":
    validate_all_market_coordinates()
