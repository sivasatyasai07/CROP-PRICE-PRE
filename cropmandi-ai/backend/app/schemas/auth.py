from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, List

class SignupRequest(BaseModel):
    email: str = Field(..., description="Farmer email address")
    password: str = Field(..., description="Account password")
    confirm_password: str = Field(..., description="Password confirmation")

class LoginRequest(BaseModel):
    email: str = Field(..., description="Farmer email address")
    password: str = Field(..., description="Account password")

class UserOut(BaseModel):
    id: str
    email: str
    role: str = "farmer"
    is_active: bool = True
    created_at: Optional[str] = None

class AuthResponse(BaseModel):
    message: str
    user: UserOut
    access_token: str
    token_type: str = "bearer"

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = "AUTH_ERROR"
    errors: Optional[Dict[str, List[str]]] = None
