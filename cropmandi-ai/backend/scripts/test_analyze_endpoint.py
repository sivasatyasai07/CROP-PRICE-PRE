import io
import time
import requests
import json
from PIL import Image
from app.services.user_store import read_users
from app.core.security import create_access_token

BASE_URL = "http://127.0.0.1:8000"

users = read_users()
user = users[0]
token = create_access_token({"sub": user["id"], "email": user["email"]})
print(f"Using user: {user['email']} (id={user['id']})")

# Create a small green leaf test image
img = Image.new("RGB", (250, 250), color=(34, 139, 34))
buf = io.BytesIO()
img.save(buf, format="JPEG")
buf.seek(0)

headers = {
    "Authorization": f"Bearer {token}"
}
files = {
    "file": ("test_leaf.jpg", buf.getvalue(), "image/jpeg")
}
data = {
    "language": "en"
}

print("Testing POST /api/v1/disease/analyze...")
t0 = time.time()
try:
    resp = requests.post(
        f"{BASE_URL}/api/v1/disease/analyze",
        headers=headers,
        files=files,
        data=data,
        timeout=35
    )
    elapsed = time.time() - t0
    print(f"Status Code: {resp.status_code} in {elapsed:.2f}s")
    print("Response JSON:")
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    elapsed = time.time() - t0
    print(f"Request failed after {elapsed:.2f}s: {e}")
