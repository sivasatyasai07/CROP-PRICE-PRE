import requests
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.config import settings

def test_api():
    print("Testing data.gov.in API...")
    res_id = settings.DATA_GOV_RESOURCE_ID.lstrip('/')
    if res_id.startswith("resource/"):
        res_id = res_id[len("resource/"):]
    url = f"{settings.DATA_GOV_BASE_URL.rstrip('/')}/resource/{res_id}"
    print("Request URL:", url)
    print("API Key present:", bool(settings.DATA_GOV_API_KEY))
    params = {
        "api-key": settings.DATA_GOV_API_KEY,
        "format": "json",
        "limit": 5
    }
    headers = {"User-Agent": "Mozilla/5.0 CropMandiAI/2.0"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        print("HTTP Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            records = data.get("records", [])
            print(f"Success! Fetched {len(records)} records.")
            if records:
                print("Sample record:", json.dumps(records[0], indent=2))
        else:
            print("Response text:", r.text[:300])
    except Exception as e:
        print("Exception occurred:", e)

if __name__ == "__main__":
    test_api()
