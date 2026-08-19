import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("cropmandi-ai/backend"))
sys.path.insert(0, os.path.abspath("."))

from app.config import settings
from app.services.plantnet_disease_service import identify_plant_image, validate_image
from PIL import Image
import io


def run_image_test(image_path: str, selected_crop: str = "Tomato"):
    print("=" * 80)
    print("PLANTNET API IMAGE IDENTIFICATION DIAGNOSTIC")
    print("=" * 80)

    # 1. Load image
    if not os.path.exists(image_path):
        print(f"Creating a valid sample leaf image at {image_path} for testing...")
        os.makedirs(os.path.dirname(os.path.abspath(image_path)), exist_ok=True)
        img = Image.new("RGB", (300, 300), color=(46, 139, 87))
        img.save(image_path, format="JPEG")

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    print(f"1. Testing Image: {image_path} ({len(img_bytes)} bytes)")
    valid, err_msg = validate_image(img_bytes, "image/jpeg")
    print(f"   Validation: {'Valid' if valid else f'Invalid ({err_msg})'}")
    print("-" * 80)

    start_time = datetime.now()
    res, model = identify_plant_image(
        image_bytes=img_bytes,
        mime_type="image/jpeg",
        filename=os.path.basename(image_path),
        selected_crop=selected_crop
    )
    elapsed_sec = (datetime.now() - start_time).total_seconds()

    print(f"2. PlantNet Response:")
    print(f"   Provider: {res.provider}")
    print(f"   Analysis Status: {res.analysis_status}")
    print(f"   Detected Crop: {res.detected_crop}")
    print(f"   Scientific Name: {res.detected_scientific_name}")
    print(f"   PlantNet Identification Score: {res.plantnet_score}")
    print(f"   Identification Status: {res.identification_status}")
    print(f"   Crop Match Status: {res.crop_match_status}")
    print(f"   Disease Status: {res.disease_status}")
    print(f"   Ranked Candidates Count: {len(res.plantnet_results)}")
    print(f"   Elapsed Time: {elapsed_sec:.2f}s")
    print("-" * 80)

    report_payload = {
        "report_name": "PlantNet API Diagnostic Report",
        "request_timestamp": datetime.now().isoformat(),
        "image_path": image_path,
        "image_size_bytes": len(img_bytes),
        "selected_crop": selected_crop,
        "provider": res.provider,
        "analysis_status": res.analysis_status,
        "detected_crop": res.detected_crop,
        "detected_scientific_name": res.detected_scientific_name,
        "plantnet_score": res.plantnet_score,
        "crop_match_status": res.crop_match_status,
        "disease_status": res.disease_status,
        "results_count": len(res.plantnet_results),
        "plantnet_results": [r.model_dump() if hasattr(r, "model_dump") else r.dict() for r in res.plantnet_results],
        "response_time_seconds": round(elapsed_sec, 2),
        "disclaimer": res.disclaimer
    }

    out_paths = [
        os.path.abspath("reports/plantnet_api_diagnostic.json"),
        os.path.abspath("cropmandi-ai/reports/plantnet_api_diagnostic.json"),
        os.path.abspath("cropmandi-ai/backend/reports/plantnet_api_diagnostic.json")
    ]
    for p in out_paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(report_payload, f, indent=2, default=str)
        except Exception:
            pass

    print(f"Diagnostic report saved to reports/plantnet_api_diagnostic.json")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test PlantNet Image Identification")
    parser.add_argument("--image", default="data/sample_leaf.jpg", help="Path to leaf image")
    parser.add_argument("--crop", default="Tomato", help="Selected crop name")
    args = parser.parse_args()

    run_image_test(args.image, args.crop)
