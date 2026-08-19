import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from app.schemas.auth import SignupRequest, LoginRequest, AuthResponse, UserOut
from app.services.user_store import (
    find_user_by_email,
    create_user,
    normalize_email,
    safe_user_dict
)
from app.core.security import (
    validate_password_rules,
    hash_password,
    verify_password,
    create_access_token
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest):
    email = normalize_email(req.email)
    errors: Dict[str, List[str]] = {}

    # Email validation
    if not email:
        errors["email"] = ["Email is required."]
    elif not EMAIL_REGEX.match(email):
        errors["email"] = ["Enter a valid email address."]

    # Password validation
    pass_res = validate_password_rules(req.password)
    if not pass_res["is_valid"]:
        errors["password"] = pass_res["errors"]

    # Confirm password validation
    if req.password != req.confirm_password:
        errors["confirm_password"] = ["Passwords do not match."]

    if errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Validation failed.",
                "code": "AUTH_VALIDATION_ERROR",
                "errors": errors
            }
        )

    # Check duplicate email
    if find_user_by_email(email):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "An account with this email already exists.",
                "code": "DUPLICATE_EMAIL",
                "errors": {"email": ["An account with this email already exists."]}
            }
        )

    # Hash password and save user (Default role: farmer)
    pwd_hash = hash_password(req.password)
    new_user = create_user(email=email, password_hash=pwd_hash, role="farmer")

    # Generate token
    token = create_access_token(data={"sub": new_user["id"], "email": new_user["email"], "role": new_user["role"]})

    return AuthResponse(
        message="Account created successfully.",
        user=UserOut(**safe_user_dict(new_user)),
        access_token=token,
        token_type="bearer"
    )

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    email = normalize_email(req.email)
    errors: Dict[str, List[str]] = {}

    if not email:
        errors["email"] = ["Email is required."]
    elif not EMAIL_REGEX.match(email):
        errors["email"] = ["Enter a valid email address."]

    if not req.password:
        errors["password"] = ["Password is required."]

    if errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Validation failed.",
                "code": "AUTH_VALIDATION_ERROR",
                "errors": errors
            }
        )

    user = find_user_by_email(email)
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Incorrect email or password.",
                "code": "INVALID_CREDENTIALS"
            }
        )

    if not user.get("is_active", True):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "Account is inactive. Please contact support.",
                "code": "INACTIVE_ACCOUNT"
            }
        )

    token = create_access_token(data={"sub": user["id"], "email": user["email"], "role": user.get("role", "farmer")})

    return AuthResponse(
        message="Login successful.",
        user=UserOut(**safe_user_dict(user)),
        access_token=token,
        token_type="bearer"
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return UserOut(**safe_user_dict(current_user))

@router.post("/logout")
def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"message": "Logged out successfully."}
