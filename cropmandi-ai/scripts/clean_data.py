import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.services.cleaning_service import run_cleaning_pipeline

def main():
    print("Running CropMandi AI data cleaning & normalization pipeline...")
    db = SessionLocal()
    try:
        report = run_cleaning_pipeline(db)
        print("\n--- DATA QUALITY REPORT ---")
        print(f"Total Input Rows: {report['total_input_rows']}")
        print(f"Valid Cleaned Rows: {report['valid_rows']}")
        print(f"Invalid / Rejected Rows: {report['invalid_rows']}")
        print(f"Duplicates Removed: {report['duplicate_counts']}")
        print(f"Suspicious Price Records: {report['suspicious_price_counts']}")
        print(f"Future Date Records Ignored: {report['future_date_counts']}")
        print(f"Date Range: {report['date_range']['start']} to {report['date_range']['end']}")
        print("----------------------------\n")
    except Exception as e:
        print(f"Cleaning pipeline failed: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
