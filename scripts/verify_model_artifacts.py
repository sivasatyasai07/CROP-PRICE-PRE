import os
import sys
import json
import logging

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "cropmandi-ai", "backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.ml.model_registry import check_model_health, get_active_model_version, load_model_artifacts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_model_artifacts")

def main():
    os.makedirs("reports", exist_ok=True)
    db = SessionLocal()
    try:
        health = check_model_health(db)
        logger.info("Model Health Check Result: %s", health)
        
        report_path = "reports/model_artifact_deployment_report.json"
        with open(report_path, "w") as f:
            json.dump(health, f, indent=2)
            
        logger.info("Model Artifact Deployment Report saved to %s", report_path)
        
        if health.get("status") not in ["ready"]:
            logger.error("Model verification failed with status: %s", health.get("status"))
            sys.exit(1)
        else:
            logger.info("SUCCESS: All multi-horizon CatBoost model artifacts and metadata are verified.")
            sys.exit(0)
    finally:
        db.close()

if __name__ == "__main__":
    main()
