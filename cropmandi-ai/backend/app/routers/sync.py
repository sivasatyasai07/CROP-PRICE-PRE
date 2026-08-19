from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.sync import SyncStatusResponse, SyncRunRequest
from app.services.scheduler_service import get_sync_status, run_sync_task

router = APIRouter(prefix="/sync", tags=["synchronization"])

@router.get("/status", response_model=SyncStatusResponse)
def sync_status():
    """Returns current or latest backend API synchronization report."""
    status_data = get_sync_status()
    return SyncStatusResponse(**status_data)

@router.post("/run", response_model=SyncStatusResponse)
def trigger_sync(req: SyncRunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers an on-demand background API synchronization run."""
    background_tasks.add_task(run_sync_task, req.lookback_days)
    status_data = get_sync_status()
    status_data["status"] = "in_progress"
    return SyncStatusResponse(**status_data)
