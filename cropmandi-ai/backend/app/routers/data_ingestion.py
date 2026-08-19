from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import shutil
from app.database import get_db
from app.services.csv_ingestion_service import ingest_csv_data
from app.services.data_gov_service import fetch_data_gov_prices
from app.services.cleaning_service import run_cleaning_pipeline
from app.models import DataQualityReport

router = APIRouter(prefix="/api/v1/ingestion", tags=["Data Ingestion"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-csv")
def upload_csv_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    raw_records = ingest_csv_data(file_path, db)
    return {
        "status": "success",
        "filename": file.filename,
        "raw_records_imported": len(raw_records)
    }

@router.post("/fetch-data-gov")
def fetch_from_data_gov(
    state: str = "Andhra Pradesh",
    limit: int = 1000,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    try:
        raw_records = fetch_data_gov_prices(db, state=state, limit=limit, offset=offset)
        return {
            "status": "success",
            "source": "data.gov.in",
            "records_fetched": len(raw_records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clean")
def trigger_cleaning(db: Session = Depends(get_db)):
    report = run_cleaning_pipeline(db)
    return {
        "status": "success",
        "cleaning_report": report
    }

@router.get("/data-quality-report/latest")
def get_latest_quality_report(db: Session = Depends(get_db)):
    report = db.query(DataQualityReport).order_by(DataQualityReport.created_at.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="No quality report found.")
    return {
        "id": report.id,
        "file_name": report.file_name,
        "source": report.source,
        "created_at": report.created_at,
        "report": report.report_json
    }
