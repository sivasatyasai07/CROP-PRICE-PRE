import os
import sys
import io
import json
import argparse
import requests
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.security import create_access_token
from app.services.user_store import create_user, find_user_by_email
from app.services.gemini_crop_disease_service import INITIAL_VOCABULARY

API_BASE_URL = "http://127.0.0.1:8000"


def generate_synthetic_crop_image(crop_type: str = "Groundnut") -> bytes:
    """Generates a synthetic plant leaf image with distinct botanical structures."""
    img = Image.new("RGB", (400, 400), color=(240, 248, 240))
    draw = ImageDraw.Draw(img)

    if crop_type == "Groundnut":
        # Draw 4 obovate leaflets (tetrafoliolate pattern)
        draw.ellipse([(140, 100), (200, 200)], fill=(46, 139, 87), outline=(34, 110, 60), width=2)
        draw.ellipse([(200, 100), (260, 200)], fill=(46, 139, 87), outline=(34, 110, 60), width=2)
        draw.ellipse([(120, 180), (190, 280)], fill=(46, 139, 87), outline=(34, 110, 60), width=2)
        draw.ellipse([(210, 180), (280, 280)], fill=(46, 139, 87), outline=(34, 110, 60), width=2)
        # Petiole & stem
        draw.line([(200, 200), (200, 360)], fill=(60, 140, 60), width=4)
        # Small Cercospora leaf spots
        draw.ellipse([(160, 140), (175, 155)], fill=(101, 67, 33), outline=(218, 165, 32), width=1)
        draw.ellipse([(230, 220), (245, 235)], fill=(101, 67, 33), outline=(218, 165, 32), width=1)
    else:
        # Default serrated single leaf
        draw.polygon([(200, 40), (320, 180), (280, 320), (200, 370), (120, 320), (80, 180)], fill=(34, 139, 34))
        draw.line([(200, 40), (200, 370)], fill=(20, 90, 20), width=4)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def run_verification(image_path: str = None, selected_crop: str = None):
    print("==================================================")
    print("  CROPMANDI AI — OPEN-SET CROP RECOGNITION AUDIT")
    print("==================================================")

    # 1. Ensure test user
    test_email = "openset_verifier@cropmandi.test"
    test_user = find_user_by_email(test_email)
    if not test_user:
        test_user = create_user(test_email, "OpenSet Verifier Farmer", "VerifierFarmer123!")
    test_uid = test_user["id"]

    token = create_access_token({"sub": test_uid, "email": test_email, "role": "farmer"})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get image bytes
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        print(f"Loaded image from: {image_path}")
    else:
        image_bytes = generate_synthetic_crop_image("Groundnut")
        print("Generated synthetic groundnut test image")

    # 3. Call endpoint
    url = f"{API_BASE_URL}/api/v1/disease/analyze"
    files = {"file": ("crop_test.jpg", image_bytes, "image/jpeg")}
    data = {"language": "en"}
    if selected_crop:
        data["crop"] = selected_crop

    print("\nCalling POST /api/v1/disease/analyze...")
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=75)
    except Exception as exc:
        print(f"Failed to connect to backend: {exc}")
        sys.exit(1)

    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}: {response.text}")
        sys.exit(1)

    resp_json = response.json()
    result = resp_json.get("result", {})
    crop_rec = result.get("crop_recognition", {})
    best_crop = crop_rec.get("best_crop", {})
    ranked_cands = crop_rec.get("ranked_candidates", [])
    feat_analysis = crop_rec.get("feature_analysis", {})
    leaf_margin = feat_analysis.get("leaf_margin", {})
    ident_status = crop_rec.get("identification_status", "unknown")

    best_name = best_crop.get("name", "Unidentified")
    best_cat = best_crop.get("category", "unknown")
    best_prob = best_crop.get("gemini_original_probability")
    margin_type = leaf_margin.get("type", "unavailable")
    margin_conf = leaf_margin.get("original_confidence")

    in_vocab = any(best_name.lower() == v.lower() for v in INITIAL_VOCABULARY)
    vocab_status = "Initial list" if in_vocab else "Outside initial list (Open-Set Recognized)"

    print("\n---------------- RANKED CANDIDATES ----------------")
    for idx, c in enumerate(ranked_cands, start=1):
        prob = c.get("gemini_original_probability")
        prob_str = f"{round(prob * 100)}%" if prob is not None else "Unavailable"
        print(f"{idx}. {c.get('name')} ({c.get('category')}) — Probability: {prob_str} [{c.get('crop_status')}]")
        if c.get("supporting_evidence"):
            print(f"   Supporting: {', '.join(c.get('supporting_evidence')[:2])}")

    print("\n---------------- AUDIT SUMMARY ----------------")
    print(f"Best crop:                    {best_name}")
    print(f"Category:                     {best_cat.capitalize()}")
    print(f"Status:                       {ident_status.capitalize()}")
    print(f"Gemini original probability:  {best_prob if best_prob is not None else 'Unavailable'}")
    print(f"Configured vocabulary status: {vocab_status}")
    print(f"Leaf margin:                  {margin_type.capitalize()}")
    print(f"Leaf margin confidence:       {margin_conf if margin_conf is not None else 'Unavailable'}")

    # Validation Checks
    valid_selection = True
    if ranked_cands:
        max_prob_cand = max(
            ranked_cands,
            key=lambda x: x.get("gemini_original_probability") if x.get("gemini_original_probability") is not None else -1
        )
        if max_prob_cand.get("gemini_original_probability") is not None and best_prob is not None:
            if best_prob < max_prob_cand.get("gemini_original_probability"):
                valid_selection = False

    verification_status = "PASS" if valid_selection else "FAIL"
    print(f"\nVerification:                 {verification_status}")

    # Persist JSON Report
    report = {
        "analysis_id": resp_json.get("analysis_id"),
        "best_crop": best_crop,
        "ranked_candidates": ranked_cands,
        "feature_analysis": feat_analysis,
        "identification_status": ident_status,
        "vocabulary_status": vocab_status,
        "verification_result": verification_status
    }
    report_file = os.path.join(BASE_DIR, "data", "open_set_verification_report.json")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved Report to: {report_file}")
    print("==================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Open-Set Crop Recognition")
    parser.add_argument("--image", type=str, default=None, help="Path to leaf image")
    parser.add_argument("--crop", type=str, default=None, help="User-selected crop")
    args = parser.parse_args()
    run_verification(args.image, args.crop)
