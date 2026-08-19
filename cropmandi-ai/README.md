# CropMandi AI – 3-Day Farmer Mandi Price Prediction & Advisory System

CropMandi AI is an end-to-end Machine Learning and Decision Support system designed to provide 3-day market price forecasts for APMC mandis across India.

---

## 🔐 Authentication System

The application features a secure, prototype-ready authentication system supporting email registration, password validation, role-based access control, and atomic JSON account persistence.

### 1. Overview
- **User Roles**: `farmer` (default upon signup) and `admin`.
- **Session Handling**: JWT (JSON Web Token) Bearer authentication header.
- **Top-Right Header Controls**: Context-aware Login / Signup buttons when logged out, and email / user menu / Logout button when logged in.

### 2. Signup & Login Flow
1. **Signup**:
   - Email is normalized (trimmed and lowercased). Duplicate emails are rejected.
   - Password must pass all validation rules before submission.
   - Confirm password must match password exactly.
   - Passwords are salted and hashed with **bcrypt** prior to storage. Plain text passwords are **never** stored or logged.
2. **Login**:
   - Accepts registered email and password.
   - Returns JWT Access Token and user details.
   - Generic failure message (`"Incorrect email or password."`) prevents account enumeration.

### 3. Password Validation Rules
- **At least 6 characters**
- **At least one capital letter (A-Z)**
- **At least one symbol (e.g., @, #, !, $)**
- **Contains no spaces**
- **Confirm password match**

Validation is enforced in real-time on the **frontend** (with a live checklist) and validated securely on the **backend**.

### 4. JSON Account Storage
For development and student project demonstration, user account records are stored in:
`backend/data/users.json`

Example structure:
```json
{
  "users": [
    {
      "id": "8d5c8b6a-4fa7-4c9a-a43d-123456789abc",
      "email": "farmer@example.com",
      "password_hash": "$2b$12$mYGIfxqA25vO/OgBqtuSc.X9lZ5N7I8OMSjNWEWEBM4coXJEQzYUi",
      "role": "farmer",
      "is_active": true,
      "created_at": "2026-08-14T15:30:00Z",
      "updated_at": "2026-08-14T15:30:00Z"
    }
  ]
}
```

> ⚠️ **Development Note & Security Warning**:
> JSON account storage is used for prototype development. Production deployment should use PostgreSQL, a managed identity provider (e.g. Auth0, Firebase, Supabase), or a dedicated authentication database.
> Do **NOT** commit `backend/data/users.json` to version control. The file is listed in `.gitignore`. An example structure is provided in `backend/data/users.example.json`.

### 5. Environment Variables
Configure the following keys in `backend/.env`:
```env
AUTH_SECRET_KEY=cropmandi-super-secret-key-change-in-production-2026
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=1440
USERS_JSON_PATH=data/users.json
```

---

## 🧪 Testing Authentication

Run the backend pytest test suite to verify password rules, bcrypt hashing, signup, duplicate email rejection, login, and JWT verification:

```bash
cd backend
python -m pytest tests/test_auth.py
```

---

## 🚀 Running the Application

### 1. Start Backend API Server
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Start Frontend UI
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.
