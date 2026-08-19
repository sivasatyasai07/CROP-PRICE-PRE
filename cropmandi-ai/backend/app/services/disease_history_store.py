import os
import json
import time
import shutil
import tempfile
import hashlib
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Base Data Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
HISTORY_DIR = BASE_DIR / "data" / "disease_history"
IMAGES_DIR = BASE_DIR / "data" / "disease_images"

# Ensure root directories exist
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# In-memory lock for thread-safe concurrent writes
_file_locks: Dict[str, threading.Lock] = {}
_lock_mutex = threading.Lock()

# Rate limiting tracking (in-memory for prototype)
# user_id / ip -> list of timestamps
_user_request_timestamps: Dict[str, List[float]] = {}
_ip_request_timestamps: Dict[str, List[float]] = {}
_rate_limit_lock = threading.Lock()


def _get_user_lock(user_id: str) -> threading.Lock:
    with _lock_mutex:
        if user_id not in _file_locks:
            _file_locks[user_id] = threading.Lock()
        return _file_locks[user_id]


def get_user_history_path(user_id: str) -> Path:
    """Safe path resolution preventing path traversal."""
    safe_uid = "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))
    if not safe_uid:
        safe_uid = "anonymous"
    return HISTORY_DIR / f"user_{safe_uid}.json"


def get_user_images_dir(user_id: str) -> Path:
    """Safe user image directory resolution."""
    safe_uid = "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))
    if not safe_uid:
        safe_uid = "anonymous"
    udir = IMAGES_DIR / safe_uid
    udir.mkdir(parents=True, exist_ok=True)
    return udir


def initialize_user_history(user_id: str, email: str) -> Dict[str, Any]:
    """Initializes empty JSON structure for a user."""
    return {
        "user_id": user_id,
        "email": email,
        "analyses": []
    }


def read_user_history(user_id: str) -> Dict[str, Any]:
    """
    Reads user history JSON safely.
    Handles missing or corrupted files without crashing.
    """
    path = get_user_history_path(user_id)
    if not path.exists():
        return initialize_user_history(user_id, "")

    lock = _get_user_lock(user_id)
    with lock:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict) or "analyses" not in data:
                    raise ValueError("Malformed user history structure")
                return data
        except Exception as exc:
            logger.error("Corrupted history file for user %s: %s. Creating backup.", user_id, exc)
            # Create backup of corrupted file
            backup_path = path.with_suffix(f".corrupt_{int(time.time())}.json")
            try:
                shutil.copy2(path, backup_path)
            except Exception:
                pass
            return initialize_user_history(user_id, "")


def write_user_history(user_id: str, data: Dict[str, Any]) -> None:
    """
    Performs atomic write of user history JSON to prevent file corruption.
    Uses temporary file + atomic rename.
    """
    path = get_user_history_path(user_id)
    lock = _get_user_lock(user_id)

    with lock:
        # Write to temporary file in the same directory (ensures same filesystem for atomic rename)
        temp_fd, temp_path = tempfile.mkstemp(dir=str(HISTORY_DIR), prefix=f"tmp_user_{user_id}_", suffix=".json")
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, str(path))
        except Exception as exc:
            logger.error("Failed to write history for user %s: %s", user_id, exc)
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            raise IOError(f"Could not safely persist user history: {exc}")


def append_analysis(user_id: str, email: str, analysis_record: Dict[str, Any]) -> Dict[str, Any]:
    """Appends an analysis to user's history file."""
    history = read_user_history(user_id)
    history["user_id"] = user_id
    if email:
        history["email"] = email

    analyses = history.get("analyses", [])
    # Insert newest first
    analyses.insert(0, analysis_record)
    history["analyses"] = analyses

    write_user_history(user_id, history)
    return analysis_record


def get_analysis_by_id(user_id: str, analysis_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single analysis by ID if owned by user."""
    history = read_user_history(user_id)
    for item in history.get("analyses", []):
        if item.get("analysis_id") == analysis_id:
            return item
    return None


def delete_analysis(user_id: str, analysis_id: str) -> bool:
    """Deletes an analysis record and its stored image."""
    history = read_user_history(user_id)
    analyses = history.get("analyses", [])
    initial_len = len(analyses)
    
    filtered = [a for a in analyses if a.get("analysis_id") != analysis_id]
    if len(filtered) == initial_len:
        return False

    history["analyses"] = filtered
    write_user_history(user_id, history)

    # Delete image file if exists
    delete_disease_image(user_id, analysis_id)
    return True


def check_duplicate_image(user_id: str, sha256_hash: str, window_seconds: int = 3600) -> Optional[Dict[str, Any]]:
    """
    Checks if this exact image hash was recently analyzed by this user.
    Prevents duplicate redundant Gemini API calls.
    """
    history = read_user_history(user_id)
    now = time.time()

    for item in history.get("analyses", []):
        img_meta = item.get("image", {})
        if img_meta.get("sha256") == sha256_hash:
            created_at_str = item.get("created_at")
            if created_at_str:
                try:
                    dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    if (now - dt.timestamp()) < window_seconds:
                        return item
                except Exception:
                    pass
    return None


def check_rate_limit(user_id: str, ip_address: str) -> Tuple[bool, Optional[str]]:
    """
    Enforces per-user hourly limit and cooldown seconds.
    Returns (is_allowed, error_message).
    """
    now = time.time()
    max_per_hour = getattr(settings, "DISEASE_MAX_ANALYSES_PER_USER_PER_HOUR", 20)
    cooldown = getattr(settings, "DISEASE_COOLDOWN_SECONDS", 10)

    with _rate_limit_lock:
        # Check user timestamps
        if user_id not in _user_request_timestamps:
            _user_request_timestamps[user_id] = []

        timestamps = [t for t in _user_request_timestamps[user_id] if (now - t) < 3600]
        _user_request_timestamps[user_id] = timestamps

        if timestamps:
            last_request_time = timestamps[-1]
            elapsed = now - last_request_time
            if elapsed < cooldown:
                wait_time = int(cooldown - elapsed) + 1
                return False, f"Please wait {wait_time} second(s) before analyzing another image."

        if len(timestamps) >= max_per_hour:
            return False, f"Hourly analysis limit ({max_per_hour}/hr) reached. Please try again later."

        # Record this request
        _user_request_timestamps[user_id].append(now)

    return True, None


def save_disease_image(user_id: str, analysis_id: str, image_bytes: bytes, ext: str = "jpg") -> str:
    """Saves image bytes into private user storage."""
    safe_ext = "jpg" if ext.lower() in ("jpg", "jpeg") else ("png" if ext.lower() == "png" else "webp")
    user_dir = get_user_images_dir(user_id)
    filename = f"{analysis_id}.{safe_ext}"
    target_path = user_dir / filename

    with open(target_path, "wb") as f:
        f.write(image_bytes)

    return str(Path(user_id) / filename)


def get_disease_image_path(user_id: str, analysis_id: str) -> Optional[Path]:
    """Finds private image path for an analysis."""
    user_dir = get_user_images_dir(user_id)
    for ext in ("jpg", "jpeg", "png", "webp"):
        candidate = user_dir / f"{analysis_id}.{ext}"
        if candidate.exists():
            return candidate
    return None


def delete_disease_image(user_id: str, analysis_id: str) -> None:
    """Removes image file from storage."""
    user_dir = get_user_images_dir(user_id)
    for ext in ("jpg", "jpeg", "png", "webp"):
        candidate = user_dir / f"{analysis_id}.{ext}"
        if candidate.exists():
            try:
                os.remove(candidate)
            except Exception as e:
                logger.warning("Failed to delete image %s: %s", candidate, e)
