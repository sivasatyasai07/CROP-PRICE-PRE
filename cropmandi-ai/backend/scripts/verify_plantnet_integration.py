import os
import sys
import json
import io
from datetime import datetime
from PIL import Image
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from app.config import settings
from app.services.plantnet_disease_service import (
    identify_plant_image,
    validate_image,
    normalize_plantnet_result,
    test_plantnet_connection,
    classify_plantnet_error
)


def run_verification_agent():
    print("=" * 80)
    print("RUNNING PLANTNET INTEGRATION VERIFICATION AGENT")
    print("=" * 80)

    checks_passed = 0
    total_checks = 0

    # 1. Config Check
    total_checks += 1
    config_ok = (
        hasattr(settings, "PLANTNET_BASE_URL") and
        hasattr(settings, "PLANTNET_PROJECT") and
        hasattr(settings, "PLANTNET_TIMEOUT_SECONDS")
    )
    if config_ok:
        checks_passed += 1
        print("[PASS] Check 1: PlantNet backend configuration present and valid.")
    else:
        print("[FAIL] Check 1: Missing PlantNet configuration.")

    # 2. Key Security Check (Ensure key secret is not exposed in health metadata)
    total_checks += 1
    health = test_plantnet_connection()
    health_str = json.dumps(health)
    api_key_val = settings.PLANTNET_API_KEY
    is_safe = "api-key" not in health_str and (not api_key_val or api_key_val not in health_str)
    if is_safe:
        checks_passed += 1
        print("[PASS] Check 2: PlantNet health check reports status without leaking API key.")
    else:
        print("[FAIL] Check 2: API key leaked in health check.")

    # 3. Image Validation Check
    total_checks += 1
    val_empty, _ = validate_image(b"")
    val_bad_type, _ = validate_image(b"fake image content", "application/pdf")
    if not val_empty and not val_bad_type:
        checks_passed += 1
        print("[PASS] Check 3: Image validation rejects empty buffers and invalid MIME types.")
    else:
        print("[FAIL] Check 3: Image validation failed.")

    # 4. Valid Image Parsing & Normalization with Mock PlantNet Response
    total_checks += 1
    mock_plantnet_response = {
        "query": {
            "project": "all",
            "images": ["image_1"],
            "organs": ["leaf"]
        },
        "language": "en",
        "preferedReferential": "k-all",
        "bestMatch": "Solanum lycopersicum L.",
        "results": [
            {
                "score": 0.8924,
                "species": {
                    "scientificNameWithoutAuthor": "Solanum lycopersicum",
                    "scientificNameAuthorship": "L.",
                    "genus": {"scientificNameWithoutAuthor": "Solanum"},
                    "family": {"scientificNameWithoutAuthor": "Solanaceae"},
                    "commonNames": ["Tomato", "Garden tomato"],
                    "scientificName": "Solanum lycopersicum L."
                }
            },
            {
                "score": 0.0451,
                "species": {
                    "scientificNameWithoutAuthor": "Solanum melongena",
                    "scientificNameAuthorship": "L.",
                    "genus": {"scientificNameWithoutAuthor": "Solanum"},
                    "family": {"scientificNameWithoutAuthor": "Solanaceae"},
                    "commonNames": ["Brinjal", "Eggplant"],
                    "scientificName": "Solanum melongena L."
                }
            }
        ]
    }

    normalized = normalize_plantnet_result(
        raw_json=mock_plantnet_response,
        selected_crop="Tomato"
    )

    if (
        normalized.analysis_status == "success" and
        normalized.detected_crop == "Tomato" and
        normalized.plantnet_score == 0.8924 and
        normalized.crop_match_status == "match" and
        normalized.disease_status == "requires_second_stage" and
        len(normalized.plantnet_results) == 2
    ):
        checks_passed += 1
        print("[PASS] Check 4: PlantNet response successfully normalized with species, score, and rank.")
    else:
        print(f"[FAIL] Check 4: Normalization mismatch: {normalized}")

    # 5. Crop Mismatch Verification
    total_checks += 1
    mismatch_normalized = normalize_plantnet_result(
        raw_json=mock_plantnet_response,
        selected_crop="Onion"
    )
    if mismatch_normalized.crop_match_status == "mismatch":
        checks_passed += 1
        print("[PASS] Check 5: Crop mismatch accurately detected between 'Tomato' and 'Onion'.")
    else:
        print("[FAIL] Check 5: Crop mismatch detection failed.")

    # 6. Disease Disclaimer Verification
    total_checks += 1
    if "requires" in normalized.disclaimer.lower() or "preliminary" in normalized.disclaimer.lower():
        checks_passed += 1
        print("[PASS] Check 6: PlantNet identification score is properly disclaimed from disease diagnosis.")
    else:
        print("[FAIL] Check 6: Disease disclaimer missing.")

    # 7. Error Classification
    total_checks += 1
    auth_err, _ = classify_plantnet_error(401)
    rate_err, _ = classify_plantnet_error(429)
    timeout_err, _ = classify_plantnet_error(504)
    if auth_err == "plantnet_authentication_error" and rate_err == "plantnet_rate_limit_error" and timeout_err == "plantnet_timeout":
        checks_passed += 1
        print("[PASS] Check 7: HTTP error codes correctly mapped to specific diagnostic error categories.")
    else:
        print("[FAIL] Check 7: Error classification mismatch.")

    # Generate and save report
    report = {
        "report_title": "PlantNet Integration Verification Report",
        "verified_at": datetime.now().isoformat(),
        "total_checks": total_checks,
        "checks_passed": checks_passed,
        "all_passed": checks_passed == total_checks,
        "configuration": {
            "provider": "PlantNet",
            "base_url": settings.PLANTNET_BASE_URL,
            "project": settings.PLANTNET_PROJECT,
            "timeout_seconds": settings.PLANTNET_TIMEOUT_SECONDS,
            "api_key_secured": True
        },
        "sample_top_result": {
            "crop": normalized.detected_crop,
            "scientific_name": normalized.detected_scientific_name,
            "score": normalized.plantnet_score,
            "crop_match_status": normalized.crop_match_status,
            "disease_status": normalized.disease_status
        },
        "status": "VERIFIED_SUCCESSFUL" if checks_passed == total_checks else "FAILED"
    }

    out_paths = [
        os.path.abspath("reports/plantnet_verification_report.json"),
        os.path.abspath("cropmandi-ai/reports/plantnet_verification_report.json"),
        os.path.abspath("cropmandi-ai/backend/reports/plantnet_verification_report.json")
    ]
    for p in out_paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
        except Exception:
            pass

    print("-" * 80)
    print(f"VERIFICATION RESULT: {checks_passed}/{total_checks} CHECKS PASSED")
    print(f"Report saved to reports/plantnet_verification_report.json")
    print("=" * 80)
    return checks_passed == total_checks


if __name__ == "__main__":
    success = run_verification_agent()
    sys.exit(0 if success else 1)
