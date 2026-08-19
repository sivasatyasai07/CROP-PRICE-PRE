import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.ml.dataset_builder import build_dataset_from_db

def main():
    print("Building ML feature matrix from cleaned market prices & weather observations...")
    db = SessionLocal()
    try:
        df_feat = build_dataset_from_db(db)
        if df_feat.empty:
            print("Warning: Feature dataset is empty. Have you run `import_csv.py` and `clean_data.py`?")
            sys.exit(1)

        print(f"Successfully constructed feature dataset with {len(df_feat)} rows and {len(df_feat.columns)} columns.")
        
        # Save cache to ml/data/features/
        out_dir = os.path.join(os.path.dirname(__file__), "..", "ml", "data", "features")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "feature_matrix.parquet")
        df_feat.to_parquet(out_path, index=False)
        print(f"Feature matrix saved to '{out_path}'.")
    except Exception as e:
        print(f"Error building features: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
