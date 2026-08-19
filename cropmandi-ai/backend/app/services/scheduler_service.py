import logging
import os
import threading
import time
import datetime
from typing import Dict, Any, Optional

from app.database import SessionLocal
from app.services.date_service import get_ist_now, get_ist_today, IST_TZ
from app.services.official_market_sync_service import sync_latest_market_data

logger = logging.getLogger(__name__)

# Config environment settings
STARTUP_SYNC_ENABLED = os.getenv("STARTUP_SYNC_ENABLED", "true").lower() == "true"
STARTUP_SYNC_LOOKBACK_DAYS = int(os.getenv("STARTUP_SYNC_LOOKBACK_DAYS", "7"))
STARTUP_SYNC_OVERLAP_DAYS = int(os.getenv("STARTUP_SYNC_OVERLAP_DAYS", "3"))

DAILY_SYNC_ENABLED = os.getenv("DAILY_SYNC_ENABLED", "true").lower() == "true"
DAILY_SYNC_HOUR = int(os.getenv("DAILY_SYNC_HOUR", "9"))
DAILY_SYNC_MINUTE = int(os.getenv("DAILY_SYNC_MINUTE", "0"))

# Global thread-safe sync report status
latest_sync_status: Dict[str, Any] = {
    "status": "idle",
    "started_at": get_ist_now(),
    "completed_at": None,
    "latest_api_date": get_ist_today(),
    "records_received": 0,
    "records_accepted": 0,
    "records_rejected": 0,
    "predictions_replaced": 0,
    "error": None
}
_status_lock = threading.Lock()

def update_sync_status(data: Dict[str, Any]):
    global latest_sync_status
    with _status_lock:
        latest_sync_status.update(data)

def get_sync_status() -> Dict[str, Any]:
    with _status_lock:
        return dict(latest_sync_status)

def run_sync_task(lookback_days: int = STARTUP_SYNC_LOOKBACK_DAYS):
    """Executes market sync, updates global status."""
    started_at = get_ist_now()
    update_sync_status({
        "status": "in_progress",
        "started_at": started_at,
        "error": None
    })
    
    db = SessionLocal()
    try:
        report = sync_latest_market_data(db=db, lookback_days=lookback_days)
        update_sync_status({
            "status": report.get("status", "success"),
            "completed_at": get_ist_now(),
            "latest_api_date": get_ist_today(),
            "records_accepted": report.get("records_accepted", 0),
            "records_rejected": report.get("records_rejected", 0),
            "predictions_replaced": report.get("predictions_replaced", 0),
            "error": report.get("error")
        })
    except Exception as exc:
        logger.exception("Synchronization task failed: %s", exc)
        update_sync_status({
            "status": "failed",
            "completed_at": get_ist_now(),
            "error": str(exc)
        })
    finally:
        db.close()

def start_background_startup_sync():
    """Non-blocking startup sync runner."""
    if not STARTUP_SYNC_ENABLED:
        logger.info("Startup synchronization disabled in configuration.")
        return

    logger.info("Starting background startup price sync (lookback=%s days)...", STARTUP_SYNC_LOOKBACK_DAYS)
    t = threading.Thread(target=run_sync_task, args=(STARTUP_SYNC_LOOKBACK_DAYS,), daemon=True)
    t.start()

def _daily_scheduler_loop():
    """Background loop checking Asia/Kolkata timezone every minute for scheduled daily sync."""
    logger.info("Daily scheduler thread running (target: %02d:%02d IST)...", DAILY_SYNC_HOUR, DAILY_SYNC_MINUTE)
    last_run_date = None

    while True:
        try:
            now_ist = get_ist_now()
            today_date = now_ist.date()

            if DAILY_SYNC_ENABLED and today_date != last_run_date:
                if now_ist.hour == DAILY_SYNC_HOUR and now_ist.minute >= DAILY_SYNC_MINUTE:
                    logger.info("Triggering scheduled daily price synchronization for IST date %s", today_date)
                    run_sync_task(lookback_days=STARTUP_SYNC_LOOKBACK_DAYS)
                    last_run_date = today_date

            time.sleep(30)
        except Exception as exc:
            logger.error("Error in daily scheduler loop: %s", exc)
            time.sleep(60)

def start_daily_scheduler():
    """Starts the daily background scheduler thread."""
    if not DAILY_SYNC_ENABLED:
        logger.info("Daily scheduler disabled in configuration.")
        return

    t = threading.Thread(target=_daily_scheduler_loop, daemon=True)
    t.start()
