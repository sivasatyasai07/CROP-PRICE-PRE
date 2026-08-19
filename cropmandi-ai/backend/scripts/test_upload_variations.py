import io
import time
import requests
import json
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

# Create a small green leaf test image
img = Image.new("RGB", (250, 250), color=(34, 139, 34))
buf = io.BytesIO()
img.save(buf, format="JPEG")
leaf_bytes = buf.getvalue()

print("=" * 60)
print("TEST VARIATION 1: Only 'file' provided, 'files' omitted")
print("=" * 60)
t0 = time.time()
resp1 = requests.post(
    f"{BASE_URL}/api/v1/disease/analyze",
    files={"file": ("leaf.jpg", leaf_bytes, "image/jpeg")},
    data={"language": "en"},
    timeout=35
)
print(f"Status Code: {resp1.status_code} in {time.time() - t0:.2f}s")
print("Response JSON:", resp1.json())
assert resp1.status_code in (200, 502, 504), f"Unexpected status: {resp1.status_code}"

print("\n" + "=" * 60)
print("TEST VARIATION 2: 'files' omitted entirely (same as above)")
print("=" * 60)
time.sleep(11)
t0 = time.time()
resp2 = requests.post(
    f"{BASE_URL}/api/v1/disease/analyze",
    files={"file": ("leaf.jpg", leaf_bytes, "image/jpeg")},
    timeout=35
)
print(f"Status Code: {resp2.status_code} in {time.time() - t0:.2f}s")
assert resp2.status_code in (200, 502, 504), f"Unexpected status: {resp2.status_code}"

print("\n" + "=" * 60)
print("TEST VARIATION 3: One file in 'files' and 'file' omitted")
print("=" * 60)
time.sleep(11)
t0 = time.time()
resp3 = requests.post(
    f"{BASE_URL}/api/v1/disease/analyze",
    files={"files": ("leaf_in_files.jpg", leaf_bytes, "image/jpeg")},
    timeout=35
)
print(f"Status Code: {resp3.status_code} in {time.time() - t0:.2f}s")
assert resp3.status_code in (200, 502, 504), f"Unexpected status: {resp3.status_code}"

print("\n" + "=" * 60)
print("TEST VARIATION 4: Multiple files in 'files' and 'file' provided")
print("=" * 60)
time.sleep(11)
t0 = time.time()
resp4 = requests.post(
    f"{BASE_URL}/api/v1/disease/analyze",
    files=[
        ("file", ("primary.jpg", leaf_bytes, "image/jpeg")),
        ("files", ("secondary1.jpg", leaf_bytes, "image/jpeg")),
        ("files", ("secondary2.jpg", leaf_bytes, "image/jpeg")),
    ],
    timeout=35
)
print(f"Status Code: {resp4.status_code} in {time.time() - t0:.2f}s")
assert resp4.status_code in (200, 502, 504), f"Unexpected status: {resp4.status_code}"

print("\n" + "=" * 60)
print("ALL 4 UPLOAD VARIATIONS TESTED SUCCESSFULLY (NO 422 ERRORS)!")
print("=" * 60)
