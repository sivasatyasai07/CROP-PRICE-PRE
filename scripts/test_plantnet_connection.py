import os
import sys
import io
import requests
from datetime import datetime
from PIL import Image

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("cropmandi-ai/backend"))
sys.path.insert(0, os.path.abspath("."))

from app.config import settings


def test_plantnet_connection():
    print("=" * 80)
    print("PLANTNET API BACKEND CONNECTION & SECURITY TEST")
    print("=" * 80)

    api_key = settings.PLANTNET_API_KEY
    base_url = settings.PLANTNET_BASE_URL.rstrip("/")
    project = settings.PLANTNET_PROJECT or "all"

    print(f"1. Configuration Check:")
    print(f"   Base URL: {base_url}")
    print(f"   Project: {project}")
    print(f"   API Key: {'[SET - SECURELY LOADED FROM ENVIRONMENT]' if api_key else '[NOT CONFIGURED]'}")
    print(f"   Timeout: {settings.PLANTNET_TIMEOUT_SECONDS}s")
    print(f"   Max Retries: {settings.PLANTNET_MAX_RETRIES}")
    print("-" * 80)

    if not api_key:
        print("[WARNING] PLANTNET_API_KEY is not set in backend environment (.env).")
        print("To configure, add PLANTNET_API_KEY=your_key in backend/.env")
        print("=" * 80)
        sys.exit(0)

    # Generate a lightweight valid synthetic JPEG leaf image in-memory for testing
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    endpoint = f"{base_url}/{project}"
    params = {"api-key": api_key}
    files = [("images", ("test_leaf.jpg", img_bytes, "image/jpeg"))]
    data = {"organs": ["leaf"]}

    print("2. Sending Real Multipart/Form-Data POST Request...")
    try:
        start_time = datetime.now()
        resp = requests.post(
            endpoint,
            params=params,
            files=files,
            data=data,
            timeout=float(settings.PLANTNET_TIMEOUT_SECONDS),
            headers={"User-Agent": "CropMandiAI/2.0 (PlantNetTest)"}
        )
        elapsed_sec = (datetime.now() - start_time).total_seconds()

        print(f"   HTTP Status: {resp.status_code}")
        print(f"   Content-Type: {resp.headers.get('Content-Type')}")
        print(f"   Elapsed Time: {elapsed_sec:.2f}s")

        if resp.status_code == 200:
            json_data = resp.json()
            results = json_data.get("results", [])
            print(f"   Response Keys: {list(json_data.keys())}")
            print(f"   Results Count: {len(results)}")
            if results:
                top = results[0]
                sp = top.get("species", {})
                print(f"   Top Match: {sp.get('scientificName')} (Score: {top.get('score')})")
            print("-" * 80)
            print("PLANTNET API TEST RESULT: SUCCESS (HTTP 200)")
            print("=" * 80)
            sys.exit(0)
        elif resp.status_code in (401, 403):
            print("   [ERROR] PlantNet Authentication Failed (HTTP 401/403). Check API key.")
            print("=" * 80)
            sys.exit(1)
        else:
            print(f"   [NOTICE] PlantNet returned HTTP {resp.status_code}: {resp.text[:200]}")
            print("=" * 80)
            sys.exit(0)

    except Exception as exc:
        print(f"   [ERROR] Connection Exception: {exc}")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    test_plantnet_connection()
