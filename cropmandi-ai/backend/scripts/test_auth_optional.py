import io
import time
import requests
import json
from PIL import Image
from app.services.user_store import read_users
from app.core.security import create_access_token

BASE_URL = "http://127.0.0.1:8000"

# Create a test leaf image
img = Image.new("RGB", (250, 250), color=(34, 139, 34))
buf = io.BytesIO()
img.save(buf, format="JPEG")
image_bytes = buf.getvalue()

users = read_users()
user = users[0]
token = create_access_token({"sub": user["id"], "email": user["email"]})

print("=" * 60)
print("TEST 1: UNLOGGED-OUT (ANONYMOUS) ANALYSIS WITHOUT AUTH HEADER")
print("=" * 60)
t0 = time.time()
resp_unauth = requests.post(
    f"{BASE_URL}/api/v1/disease/analyze",
    files={"file": ("guest_leaf.jpg", image_bytes, "image/jpeg")},
    data={"language": "en"},
    timeout=35
)
elapsed_unauth = time.time() - t0
print(f"Status Code: {resp_unauth.status_code} in {elapsed_unauth:.2f}s")
print(f"Response: {json.dumps(resp_unauth.json(), indent=2)[:400]}...")

print("\n" + "=" * 60)
print("TEST 2: LOGGED-IN ANALYSIS WITH AUTH HEADER")
print("=" * 60)
t0 = time.time()
resp_auth = requests.post(
    f"{BASE_URL}/api/v1/disease/analyze",
    headers={"Authorization": f"Bearer {token}"},
    files={"file": ("user_leaf.jpg", image_bytes, "image/jpeg")},
    data={"language": "en"},
    timeout=35
)
elapsed_auth = time.time() - t0
print(f"Status Code: {resp_auth.status_code} in {elapsed_auth:.2f}s")
print(f"Response: {json.dumps(resp_auth.json(), indent=2)[:400]}...")

print("\n" + "=" * 60)
print("TEST 3: VERIFY HISTORY ENDPOINT (STRICT AUTHENTICATION)")
print("=" * 60)
# Unauthenticated history request must return 401
resp_hist_unauth = requests.get(f"{BASE_URL}/api/v1/disease/history")
print(f"Unauthenticated /disease/history Status: {resp_hist_unauth.status_code} (Expected 401)")

# Authenticated history request must return 200 with saved records
resp_hist_auth = requests.get(
    f"{BASE_URL}/api/v1/disease/history",
    headers={"Authorization": f"Bearer {token}"}
)
print(f"Authenticated /disease/history Status: {resp_hist_auth.status_code} (Expected 200)")
if resp_hist_auth.status_code == 200:
    history_items = resp_hist_auth.json().get("items", [])
    print(f"Saved history items count: {len(history_items)}")
    if history_items:
        print(f"Latest saved analysis ID: {history_items[0].get('analysis_id')}")
