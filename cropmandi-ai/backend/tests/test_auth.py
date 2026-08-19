import pytest
import os
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import validate_password_rules, hash_password, verify_password, create_access_token
from app.services.user_store import read_users, write_users, get_user_file_path

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_clean_user_store():
    # Store backup or clear test file
    path = get_user_file_path()
    original_data = None
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                original_data = json.load(f)
        except Exception:
            original_data = {"users": []}
            
    # Reset for clean test execution
    write_users([])
    yield
    # Restore original data
    if original_data is not None:
        write_users(original_data.get("users", []))

def test_password_validation_rules():
    # Valid passwords
    assert validate_password_rules("Farmer@123")["is_valid"] is True
    assert validate_password_rules("Crop#AI2026")["is_valid"] is True
    assert validate_password_rules("Tomato!A1")["is_valid"] is True

    # Invalid passwords
    res1 = validate_password_rules("farmer@123")
    assert res1["is_valid"] is False
    assert "at least one capital letter" in str(res1["errors"]).lower()

    res2 = validate_password_rules("FARMER123")
    assert res2["is_valid"] is False
    assert "at least one symbol" in str(res2["errors"]).lower()

    res3 = validate_password_rules("Fa@12")
    assert res3["is_valid"] is False
    assert "at least 6 characters" in str(res3["errors"]).lower()

    res4 = validate_password_rules("Farmer @123")
    assert res4["is_valid"] is False
    assert "not contain spaces" in str(res4["errors"]).lower()

def test_password_hashing():
    pwd = "Farmer@123"
    h1 = hash_password(pwd)
    h2 = hash_password(pwd)

    assert h1 != pwd
    assert h2 != pwd
    # Verify salting produces different hashes
    assert h1 != h2

    assert verify_password(pwd, h1) is True
    assert verify_password(pwd, h2) is True
    assert verify_password("Wrong@123", h1) is False

def test_signup_flow():
    payload = {
        "email": "  Farmer.Rao@example.com  ",
        "password": "Farmer@123",
        "confirm_password": "Farmer@123"
    }
    res = client.post("/api/v1/auth/signup", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["message"] == "Account created successfully."
    assert data["user"]["email"] == "farmer.rao@example.com"
    assert data["user"]["role"] == "farmer"
    assert "access_token" in data
    assert "password_hash" not in data["user"]
    assert "password" not in data

    # Test duplicate email rejection (case-insensitive)
    dup_res = client.post("/api/v1/auth/signup", json={
        "email": "FARMER.RAO@EXAMPLE.COM",
        "password": "Farmer@123",
        "confirm_password": "Farmer@123"
    })
    assert dup_res.status_code == 400
    assert dup_res.json()["code"] == "DUPLICATE_EMAIL"

def test_login_flow():
    # Create test account
    client.post("/api/v1/auth/signup", json={
        "email": "login.test@example.com",
        "password": "Farmer@123",
        "confirm_password": "Farmer@123"
    })

    # Test successful login
    res = client.post("/api/v1/auth/login", json={
        "email": "LOGIN.TEST@example.com",
        "password": "Farmer@123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "Login successful."
    assert data["user"]["email"] == "login.test@example.com"
    token = data["access_token"]

    # Test invalid password
    bad_res = client.post("/api/v1/auth/login", json={
        "email": "login.test@example.com",
        "password": "WrongPassword@123"
    })
    assert bad_res.status_code == 401
    assert bad_res.json()["detail"] == "Incorrect email or password."

    # Test me endpoint with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "login.test@example.com"
