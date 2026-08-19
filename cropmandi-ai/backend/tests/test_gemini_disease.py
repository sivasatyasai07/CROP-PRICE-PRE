import sys
import os
import io
import json
import pytest
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.gemini_disease_service import (
    create_fallback_result,
    validate_and_normalize_response,
    build_disease_prompt,
    get_model_metadata,
    choose_best_candidate,
    calculate_display_confidence
)


def create_dummy_leaf_image(color=(34, 139, 34)) -> bytes:
    img = Image.new("RGB", (224, 224), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_fallback_message_structure():
    fallback = create_fallback_result("The uploaded image is blurry.", "Groundnut", "en", "unclear_image")
    assert fallback.analysis_status == "unclear_image"
    assert fallback.crop_recognition.best_crop.name == "Groundnut"
    assert fallback.health_assessment.status == "unclear"
    assert fallback.primary_diagnosis.name == "Inconclusive Visual Evidence"
    assert fallback.primary_diagnosis.confidence is None
    assert fallback.chemical_control_guidance.provided is False
    assert "preliminary assessment" in fallback.model_disclaimer


def test_open_set_mock_responses_categories():
    """Tests open-set crop recognition across multiple agricultural categories."""
    categories_to_test = [
        ("Mango", "fruit", 0.82),
        ("Coffee", "plantation", 0.76),
        ("Red gram", "pulse", 0.74),
        ("Turmeric", "spice", 0.85),
        ("Cotton", "fiber", 0.79),
        ("Sweet potato", "tuber", 0.81),
    ]

    for crop_name, category, prob in categories_to_test:
        raw_mock = {
            "analysis_status": "success",
            "plant_detected": True,
            "image_quality": {"status": "acceptable", "original_confidence": 0.90},
            "crop_recognition": {
                "identification_status": "identified" if prob >= 0.75 else "probable",
                "best_crop": {"name": crop_name, "category": category, "gemini_original_probability": prob},
                "ranked_candidates": [
                    {"name": crop_name, "category": category, "gemini_original_probability": prob, "supporting_evidence": ["Morphology"]}
                ],
                "feature_analysis": {"leaf_margin": {"type": "entire", "original_confidence": 0.85, "evidence": "Smooth margin", "reliability": "usable"}}
            },
            "health_assessment": {"status": "healthy", "confidence": 0.88},
            "primary_diagnosis": {"name": "Healthy Specimen", "category": "healthy", "confidence": 0.88}
        }
        res = validate_and_normalize_response(raw_mock)
        assert res.crop_recognition.best_crop.name == crop_name
        assert res.crop_recognition.best_crop.category == category
        assert res.crop_recognition.best_crop.gemini_original_probability == prob


def test_model_metadata():
    meta = get_model_metadata()
    assert meta["provider"] == "Google Gemini"
    assert "model_name" in meta
    assert meta["prompt_version"] == "crop-disease-v2"
