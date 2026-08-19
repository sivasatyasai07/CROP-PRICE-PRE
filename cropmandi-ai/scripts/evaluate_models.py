import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.models import ModelRun

def main():
    print("Evaluating active machine learning models against 2026 chronological test set...")
    db = SessionLocal()
    try:
        active_model = db.query(ModelRun).filter(ModelRun.is_active == True).first()
        if not active_model:
            print("No active model run found in database.")
            sys.exit(1)

        print(f"\nModel: {active_model.model_name} ({active_model.model_version})")
        print(f"Training Rows: {active_model.training_rows}")
        print("Performance Metrics breakdown:")
        
        metrics = active_model.metrics_json or {}
        for horizon, m in metrics.items():
            print(f"\n[{horizon.upper()}]")
            print(f"  MAE:  {m.get('mae')} Rs./qtl")
            print(f"  RMSE: {m.get('rmse')} Rs./qtl")
            print(f"  MAPE: {m.get('mape')} %")
            print(f"  WAPE: {m.get('wape')} %")
            print(f"  sMAPE:{m.get('smape')} %")
            print(f"  R²:   {m.get('r2')}")
            if "coverage" in m:
                print(f"  80% Interval Coverage: {m.get('coverage')}% (Avg Width: {m.get('avg_width')} Rs.)")
        print()

    except Exception as e:
        print(f"Evaluation error: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
