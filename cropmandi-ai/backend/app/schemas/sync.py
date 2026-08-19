from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict, Any

class SyncStatusResponse(BaseModel):
    status: str # success, in_progress, failed
    started_at: datetime
    completed_at: Optional[datetime] = None
    latest_api_date: Optional[date] = None
    records_received: int = 0
    records_accepted: int = 0
    records_rejected: int = 0
    predictions_replaced: int = 0
    rejection_reasons: Dict[str, int] = {}
    error: Optional[str] = None

class SyncRunRequest(BaseModel):
    lookback_days: int = 7
    overlap_days: int = 3
    force: bool = False
