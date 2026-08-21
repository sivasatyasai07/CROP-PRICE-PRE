import os
import json
import uuid
import shutil
import tempfile
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings

_file_lock = threading.Lock()

def get_user_file_path() -> str:
    path = settings.USERS_JSON_PATH
    if not os.path.isabs(path):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base_dir, path)
    return path

def get_login_details_file_path() -> str:
    path = getattr(settings, "LOGIN_DETAILS_JSON_PATH", "data/login_details.json")
    if not os.path.isabs(path):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base_dir, path)
    return path

def _sync_to_root_data(source_path: str, filename: str):
    """Mirror data file to workspace root data/ folder if exists."""
    try:
        root_data_dir = os.path.abspath(os.path.join(os.path.dirname(source_path), "..", "..", "data"))
        if os.path.exists(root_data_dir):
            dest = os.path.join(root_data_dir, filename)
            shutil.copyfile(source_path, dest)
    except Exception:
        pass

def initialize_user_file() -> str:
    path = get_user_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _file_lock:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            initial_data = {"users": []}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)
            _sync_to_root_data(path, "users.json")
    return path

def initialize_login_details_file() -> str:
    path = get_login_details_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _file_lock:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            initial_data = {
                "description": "CropMandi AI User Login and Authentication Records",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "total_logins": 0,
                "login_history": [],
                "registered_users": []
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)
            _sync_to_root_data(path, "login_details.json")
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
            return []

def write_users(users: List[Dict[str, Any]]) -> bool:
    path = get_user_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _file_lock:
        dir_name = os.path.dirname(path)
        try:
            fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="users_tmp_", suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump({"users": users}, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_path, path)
            _sync_to_root_data(path, "users.json")
            return True
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise RuntimeError(f"Failed to safely write users JSON store: {e}")

def read_login_details() -> Dict[str, Any]:
    path = initialize_login_details_file()
    with _file_lock:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {"login_history": [], "registered_users": []}
        except (json.JSONDecodeError, OSError):
            return {"login_history": [], "registered_users": []}

def write_login_details(data: Dict[str, Any]) -> bool:
    path = get_login_details_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    with _file_lock:
        dir_name = os.path.dirname(path)
        try:
            fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="login_tmp_", suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_path, path)
            _sync_to_root_data(path, "login_details.json")
            return True
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise RuntimeError(f"Failed to safely write login details JSON store: {e}")

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
        "login_count": 1,
        "last_login_at": now_iso,
        "created_at": now_iso,
        "updated_at": now_iso
    }
    
    users = read_users()
    users.append(new_user)
    write_users(users)
    
    # Also record registration and initial login in login_details.json
    record_login_event(
        email=clean_email,
        status="success",
        role=role,
        user_id=new_user["id"],
        event="signup"
    )
    
    return new_user

def record_login_event(
    email: str,
    status: str = "success",
    role: Optional[str] = "farmer",
    user_id: Optional[str] = None,
    failure_reason: Optional[str] = None,
    event: str = "login",
    client_ip: Optional[str] = None
) -> Dict[str, Any]:
    """Records every login or signup attempt with timestamps in login_details.json and updates user metrics."""
    clean_email = normalize_email(email)
    now_iso = datetime.utcnow().isoformat() + "Z"
    
    login_entry = {
        "event_id": str(uuid.uuid4()),
        "event_type": event,
        "email": clean_email,
        "user_id": user_id,
        "role": role or "farmer",
        "status": status,
        "timestamp": now_iso,
        "failure_reason": failure_reason,
        "client_ip": client_ip
    }
    
    # 1. Update login_details.json
    login_data = read_login_details()
    history = login_data.get("login_history", [])
    history.append(login_entry)
    login_data["login_history"] = history
    login_data["total_logins"] = len(history)
    
    # Update registered users summary in login_details
    registered = login_data.get("registered_users", [])
    user_found = False
    for r in registered:
        if normalize_email(r.get("email", "")) == clean_email:
            user_found = True
            if status == "success":
                r["last_login_at"] = now_iso
                r["login_count"] = r.get("login_count", 0) + 1
            r["last_attempt_status"] = status
            break
            
    if not user_found and clean_email:
        registered.append({
            "user_id": user_id,
            "email": clean_email,
            "role": role or "farmer",
            "first_seen": now_iso,
            "last_login_at": now_iso if status == "success" else None,
            "login_count": 1 if status == "success" else 0,
            "last_attempt_status": status
        })
    login_data["registered_users"] = registered
    write_login_details(login_data)
    
    # 2. If login succeeded, update last_login_at and login_count in users.json
    if status == "success":
        try:
            users = read_users()
            changed = False
            for u in users:
                if normalize_email(u.get("email", "")) == clean_email:
                    u["last_login_at"] = now_iso
                    u["login_count"] = u.get("login_count", 0) + 1
                    u["updated_at"] = now_iso
                    changed = True
                    break
            if changed:
                write_users(users)
        except Exception:
            pass
            
    return login_entry

def safe_user_dict(user: Dict[str, Any]) -> Dict[str, Any]:
    """Return user record with password_hash stripped for safe API serialization."""
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "role": user.get("role", "farmer"),
        "is_active": user.get("is_active", True),
        "login_count": user.get("login_count", 1),
        "last_login_at": user.get("last_login_at"),
        "created_at": user.get("created_at")
    }

