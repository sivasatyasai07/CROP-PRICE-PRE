import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import bcrypt
from jose import JWTError, jwt
from app.config import settings

def validate_password_rules(password: str) -> Dict[str, Any]:
    """
    Validates password rules:
    - Min 6 characters
    - At least 1 uppercase letter
    - At least 1 symbol
    - No spaces
    Returns dict containing rule booleans, is_valid status, and specific error messages.
    """
    errors: List[str] = []
    
    if not password:
        return {
            "is_valid": False,
            "has_min_length": False,
            "has_uppercase": False,
            "has_symbol": False,
            "has_no_spaces": False,
            "errors": ["Password is required."]
        }
        
    has_min_length = len(password) >= 6
    has_uppercase = bool(re.search(r"[A-Z]", password))
    has_symbol = bool(re.search(r"[^A-Za-z0-9\s]", password))
    has_no_spaces = " " not in password

    if not has_min_length:
        errors.append("Password must contain at least 6 characters.")
    if not has_uppercase:
        errors.append("Password must contain at least one capital letter.")
    if not has_symbol:
        errors.append("Password must contain at least one symbol.")
    if not has_no_spaces:
        errors.append("Password must not contain spaces.")

    is_valid = has_min_length and has_uppercase and has_symbol and has_no_spaces

    return {
        "is_valid": is_valid,
        "has_min_length": has_min_length,
        "has_uppercase": has_uppercase,
        "has_symbol": has_symbol,
        "has_no_spaces": has_no_spaces,
        "errors": errors
    }

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM])
        return payload
    except JWTError:
        return None
