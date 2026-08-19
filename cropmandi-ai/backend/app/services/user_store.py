import os
import json
import uuid
import tempfile
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings

_file_lock = threading.Lock()

def get_user_file_path() -> str:
    path = settings.USERS_JSON_PATH
    if not os.path.isabs(path):
        # Resolve relative path from backend directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base_dir, path)
    return path

def initialize_user_file() -> str:
    path = get_user_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _file_lock:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            initial_data = {"users": []}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)
    return path

def read_users() -> List[Dict[str, Any]]:
    path = initialize_user_file()
    with _file_lock:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "users" in data and isinstance(data["users"], list):
                    return data["users"]
                return []
        except (json.JSONDecodeError, OSError):
            # Safe recovery if file is malformed or corrupted
            return []

def write_users(users: List[Dict[str, Any]]) -> bool:
    path = get_user_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _file_lock:
        dir_name = os.path.dirname(path)
        try:
            # Atomic write pattern: write to temp file then replace
            fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="users_tmp_", suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump({"users": users}, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_path, path)
            return True
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise RuntimeError(f"Failed to safely write users JSON store: {e}")

def normalize_email(email: str) -> str:
    if not email:
        return ""
    return email.strip().lower()

def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    clean_email = normalize_email(email)
    if not clean_email:
        return None
    users = read_users()
    for u in users:
        if normalize_email(u.get("email", "")) == clean_email:
            return u
    return None

def find_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    if not user_id:
        return None
    users = read_users()
    for u in users:
        if u.get("id") == str(user_id):
            return u
    return None

def create_user(email: str, password_hash: str, role: str = "farmer") -> Dict[str, Any]:
    clean_email = normalize_email(email)
    if not clean_email:
        raise ValueError("Email cannot be empty.")
    
    if role not in ["farmer", "admin"]:
        role = "farmer"
        
    if find_user_by_email(clean_email):
        raise ValueError("An account with this email already exists.")

    now_iso = datetime.utcnow().isoformat() + "Z"
    new_user = {
        "id": str(uuid.uuid4()),
        "email": clean_email,
        "password_hash": password_hash,
        "role": role,
        "is_active": True,
        "created_at": now_iso,
        "updated_at": now_iso
    }
    
    users = read_users()
    users.append(new_user)
    write_users(users)
    return new_user

def safe_user_dict(user: Dict[str, Any]) -> Dict[str, Any]:
    """Return user record with password_hash stripped for safe API serialization."""
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "role": user.get("role", "farmer"),
        "is_active": user.get("is_active", True),
        "created_at": user.get("created_at")
    }
