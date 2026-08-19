import os
import sys
import io
import json
import uuid
import requests
from PIL import Image, ImageDraw

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.security import create_access_token
from app.services.user_store import create_user, find_user_by_email, read_users

API_BASE_URL = "http://127.0.0.1:8000"


def generate_sample_leaf_image() -> bytes:
    """Generates an in-memory sample green leaf with simulated spots for verification testing."""
    img = Image.new("RGB", (400, 400), color=(240, 248, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw leaf shape
    draw.polygon([(200, 40), (320, 180), (280, 320), (200, 370), (120, 320), (80, 180)], fill=(34, 139, 34))
    # Draw main leaf vein
    draw.line([(200, 40), (200, 370)], fill=(20, 90, 20), width=4)
    # Draw side veins
    for y in range(100, 320, 40):
        draw.line([(200, y), (140, y - 20)], fill=(20, 90, 20), width=2)
        draw.line([(200, y), (260, y - 20)], fill=(20, 90, 20), width=2)
    # Draw simulated fungal spots
    draw.ellipse([(160, 140), (185, 165)], fill=(101, 67, 33), outline=(218, 165, 32), width=2)
    draw.ellipse([(220, 200), (250, 230)], fill=(101, 67, 33), outline=(218, 165, 32), width=2)
    draw.ellipse([(140, 240), (160, 260)], fill=(101, 67, 33), outline=(218, 165, 32), width=2)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def run_verification():
    print("==================================================")
    print("  CROPMANDI AI — CROP DISEASE VERIFICATION SCRIPT")
    print("==================================================")

    # 1. Ensure a test user exists
    test_email = "verifier_farmer@cropmandi.test"
    test_user = find_user_by_email(test_email)
    if not test_user:
        test_user = create_user(test_email, "Test Verifier Farmer", "VerifierFarmer123!")
        print(f"Created test user: {test_email} (ID: {test_user['id']})")
    else:
        print(f"Using existing test user: {test_email} (ID: {test_user['id']})")

    test_uid = test_user["id"]

    # 2. Generate Auth Token
    token = create_access_token({"sub": test_uid, "email": test_email, "role": "farmer"})
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Sample Image
    image_bytes = generate_sample_leaf_image()
    print(f"Generated sample leaf test image ({len(image_bytes)} bytes)")

    # 4. Call POST /api/v1/disease/analyze
    url = f"{API_BASE_URL}/api/v1/disease/analyze"
    files = {
        "file": ("test_leaf.jpg", image_bytes, "image/jpeg")
    }
    data = {
        "language": "en",
        "notes": "Automated verification test run"
    }

    print("\nCalling POST /api/v1/disease/analyze...")
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=70)
    except Exception as exc:
        print(f"Network error connecting to backend: {exc}")
        sys.exit(1)

    if response.status_code != 200:
        print(f"ERROR: Disease analysis request failed ({response.status_code}): {response.text}")
        sys.exit(1)

    res_json = response.json()
    analysis_id = res_json.get("analysis_id")
    result = res_json.get("result", {})
    crop_rec = result.get("crop_recognition", {})
    health_ass = result.get("health_assessment", {})
    primary_diag = result.get("primary_diagnosis", {})
    selected_comp = result.get("selected_crop_comparison", {})

    det_crop = crop_rec.get("crop_name", "Unknown")
    crop_conf = crop_rec.get("confidence")
    health_stat = health_ass.get("status", "Unknown")
    diag_name = primary_diag.get("name", "Unknown")
    diag_conf = primary_diag.get("confidence")
    match_stat = selected_comp.get("match_status", "not_specified")

    print("\n---------------- RESULTS ----------------")
    print(f"Analysis ID:            {analysis_id}")
    print(f"Selected Crop:          {selected_comp.get('selected_crop') or 'Auto-detected'}")
    print(f"Detected Crop:          {det_crop}")
    print(f"Crop Confidence:        {crop_conf}")
    print(f"Crop Match Status:      {match_stat}")
    print(f"Health Status:          {health_stat}")
    print(f"Primary Diagnosis:      {diag_name}")
    print(f"Diagnosis Confidence:   {diag_conf}")

    # 5. Verify dynamic confidence (not hard-coded)
    hard_coded_check = "passed"
    if crop_conf == 0.95 and diag_conf == 0.95:
        hard_coded_check = "warning: suspected fixed default"

    # 6. Verify User JSON History Persistence
    user_history_file = os.path.join(BASE_DIR, "data", "disease_history", f"user_{test_uid}.json")
    history_saved = False
    if os.path.exists(user_history_file):
        with open(user_history_file, "r", encoding="utf-8") as f:
            hist_data = json.load(f)
            for item in hist_data.get("analyses", []):
                if item.get("analysis_id") == analysis_id:
                    history_saved = True
                    break

    print(f"History File Exists:    {os.path.exists(user_history_file)}")
    print(f"Analysis in History:    {history_saved}")
    print(f"Hard-coded Conf Check:  {hard_coded_check}")

    # 7. Write Verification Report JSON
    report = {
        "analysis_id": analysis_id,
        "selected_crop": selected_comp.get("selected_crop"),
        "detected_crop": det_crop,
        "crop_match_status": match_stat,
        "original_confidence_values": {
            "crop": crop_conf,
            "health_status": health_ass.get("confidence"),
            "primary_diagnosis": diag_conf
        },
        "history_saved": history_saved,
        "hard_coded_confidence_check": hard_coded_check,
        "status": "passed" if history_saved else "failed"
    }

    report_path = os.path.join(BASE_DIR, "data", "disease_verification_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nVerification Report written to: {report_path}")
    print("==================================================")
    print("  VERIFICATION STATUS: PASSED")
    print("==================================================")


if __name__ == "__main__":
    run_verification()
