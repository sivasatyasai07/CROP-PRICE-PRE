import io
import json
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.services.user_store import create_user, read_users
from app.services.disease_history_store import read_user_history
from app.services.gemini_crop_disease_service import (
    validate_and_normalize_open_set_response,
    choose_best_candidate,
    create_open_set_crop_disease_prompt,
    calculate_display_confidence,
    INITIAL_VOCABULARY
)
from app.services.cv_feature_extractor import analyze_botanical_features

client = TestClient(app)


def generate_test_image_bytes(format="JPEG", size=(100, 100), color=(0, 200, 0)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


@pytest.fixture
def test_users():
    """Creates two test users for privacy isolation testing."""
    users_data = read_users()
    u1_email = "openset_alice@example.com"
    u2_email = "openset_bob@example.com"

    alice = next((u for u in users_data if u["email"] == u1_email), None)
    if not alice:
        alice = create_user(u1_email, "Alice OpenSet", "AliceFarmer123!")

    bob = next((u for u in users_data if u["email"] == u2_email), None)
    if not bob:
        bob = create_user(u2_email, "Bob OpenSet", "BobFarmer123!")

    alice_token = create_access_token({"sub": alice["id"], "email": alice["email"], "role": "farmer"})
    bob_token = create_access_token({"sub": bob["id"], "email": bob["email"], "role": "farmer"})

    return {
        "alice": alice,
        "bob": bob,
        "alice_token": alice_token,
        "bob_token": bob_token,
    }


def test_choose_best_candidate_highest_probability():
    """Tests that choose_best_candidate selects the highest valid probability candidate."""
    candidates = [
        {"name": "Soybean", "gemini_original_probability": 0.25, "combined_probability": None},
        {"name": "Groundnut", "gemini_original_probability": 0.78, "combined_probability": None},
        {"name": "Chickpea", "gemini_original_probability": 0.12, "combined_probability": None},
    ]
    res = choose_best_candidate(candidates)
    assert res is not None
    assert res["candidate"]["name"] == "Groundnut"
    assert res["probability"] == 0.78
    assert res["identification_status"] == "identified"  # >= 0.75


def test_choose_best_candidate_probable_and_low_confidence():
    """Tests identification_status thresholds for probable (0.45-0.74) and low_confidence (<0.45)."""
    # Probable test
    cand_prob = [{"name": "Maize", "gemini_original_probability": 0.62}]
    res_prob = choose_best_candidate(cand_prob)
    assert res_prob["identification_status"] == "probable"

    # Low confidence test
    cand_low = [{"name": "Sorghum", "gemini_original_probability": 0.35}]
    res_low = choose_best_candidate(cand_low)
    assert res_low["identification_status"] == "low_confidence"

    # All None or invalid probabilities
    cand_none = [{"name": "Unknown", "gemini_original_probability": None}]
    assert choose_best_candidate(cand_none) is None


def test_open_set_broad_crop_categories_and_outside_vocab():
    """
    Tests open-set response normalization for:
    - Oilseed (Groundnut - recognized outside initial 6)
    - Cereal (Maize)
    - Fruit (Mango)
    - Plantation (Coffee)
    - Pulse (Red gram)
    - Tuber/Root (Sweet potato)
    """
    # 1. Oilseed outside initial short 6
    raw_groundnut = {
        "analysis_status": "success",
        "plant_detected": True,
        "image_quality": {"status": "acceptable", "original_confidence": 0.88, "issues": []},
        "crop_recognition": {
            "identification_status": "probable",
            "best_crop": {"name": "Groundnut", "category": "oilseed", "gemini_original_probability": 0.71},
            "ranked_candidates": [
                {"name": "Groundnut", "category": "oilseed", "gemini_original_probability": 0.71, "supporting_evidence": ["Tetrafoliolate leaves"]},
                {"name": "Soybean", "category": "oilseed", "gemini_original_probability": 0.29, "supporting_evidence": ["Compound leaf"]}
            ],
            "feature_analysis": {
                "leaf_margin": {"type": "smooth / entire", "original_confidence": 0.85, "evidence": "Smooth margin", "reliability": "usable"},
                "leaf_shape": "obovate"
            }
        },
        "health_assessment": {"status": "fungal_disease", "confidence": 0.82, "visible_evidence": ["Cercospora spots"]},
        "primary_diagnosis": {"name": "Possible Early Leaf Spot", "category": "fungal_disease", "confidence": 0.78, "evidence": ["Yellow halo spots"]}
    }

    res_gn = validate_and_normalize_open_set_response(raw_groundnut, selected_crop="Tomato")
    assert res_gn.crop_recognition.best_crop.name == "Groundnut"
    assert res_gn.crop_recognition.best_crop.category == "oilseed"
    assert res_gn.crop_recognition.best_crop.crop_status == "recognized"  # In initial vocabulary list
    assert res_gn.crop_comparison.match_status == "mismatch"  # User chose Tomato but image was Groundnut

    # 2. Cereal: Maize
    raw_maize = {
        "analysis_status": "success",
        "plant_detected": True,
        "image_quality": {"status": "acceptable", "original_confidence": 0.92},
        "crop_recognition": {
            "best_crop": {"name": "Maize", "category": "cereal", "gemini_original_probability": 0.85},
            "ranked_candidates": [{"name": "Maize", "category": "cereal", "gemini_original_probability": 0.85}]
        },
        "health_assessment": {"status": "pest_damage", "confidence": 0.90},
        "primary_diagnosis": {"name": "Fall Armyworm Damage", "category": "pest_damage", "confidence": 0.88}
    }
    res_maize = validate_and_normalize_open_set_response(raw_maize)
    assert res_maize.crop_recognition.best_crop.name == "Maize"
    assert res_maize.crop_recognition.best_crop.category == "cereal"


def test_visually_similar_crops_ambiguity_and_extra_images():
    """Tests that close probabilities (gap < 0.15) trigger ambiguity warning and image suggestions."""
    raw_ambiguous = {
        "analysis_status": "success",
        "plant_detected": True,
        "image_quality": {"status": "acceptable", "original_confidence": 0.85},
        "crop_recognition": {
            "ranked_candidates": [
                {"name": "Cucumber", "category": "vegetable", "gemini_original_probability": 0.52},
                {"name": "Bottle gourd", "category": "vegetable", "gemini_original_probability": 0.48}
            ]
        },
        "health_assessment": {"status": "healthy", "confidence": 0.90},
        "primary_diagnosis": {"name": "Healthy Foliage", "confidence": 0.90}
    }

    res_amb = validate_and_normalize_open_set_response(raw_ambiguous)
    assert res_amb.crop_recognition.ambiguity.status in ("moderate", "high")
    assert res_amb.crop_recognition.ambiguity.top_candidate_gap == 0.04  # 0.52 - 0.48
    assert res_amb.next_image_request.needed is True
    assert len(res_amb.next_image_request.suggested_images) > 0


def test_non_plant_and_blurry_image_handling():
    """Non-plant and unusable images must be flagged with appropriate status."""
    raw_non_plant = {
        "analysis_status": "non_plant_image",
        "plant_detected": False,
        "image_quality": {"status": "non_plant_image", "issues": ["No plant structures detected."]},
        "crop_recognition": {"ranked_candidates": []},
        "health_assessment": {"status": "non_plant_image", "confidence": None},
        "primary_diagnosis": {"name": "Non-Plant Subject", "confidence": None}
    }
    res_np = validate_and_normalize_open_set_response(raw_non_plant)
    assert res_np.analysis_status == "non_plant_image"
    assert res_np.plant_detected is False
    assert res_np.crop_recognition.identification_status == "unidentified"


def test_cv_feature_extraction_method2():
    """Tests Method 2 botanical feature extractor returns metrics without faking calibrated classifier probability."""
    test_img = generate_test_image_bytes(size=(200, 200), color=(34, 139, 34))
    feats = analyze_botanical_features(test_img)
    assert feats["trained_classifier_available"] is False
    assert feats["classifier_probability"] is None
    assert feats["combined_probability"] is None
    assert "leaf_margin" in feats
    assert feats["leaf_margin"]["original_confidence"] is None


def test_open_set_history_persistence_and_isolation(test_users):
    """End-to-end endpoint test: verifies open-set crop history persistence in user JSON."""
    alice = test_users["alice"]
    alice_token = test_users["alice_token"]
    img_bytes = generate_test_image_bytes()

    response = client.post(
        "/api/v1/disease/analyze",
        headers={"Authorization": f"Bearer {alice_token}"},
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"crop": "Groundnut", "language": "en"}
    )
    assert response.status_code == 200
    res_data = response.json()
    analysis_id = res_data["analysis_id"]

    # Verify history JSON
    alice_hist = read_user_history(alice["id"])
    saved_item = next((a for a in alice_hist["analyses"] if a["analysis_id"] == analysis_id), None)
    assert saved_item is not None
    assert "detected_crop" in saved_item
    assert "detected_crop_category" in saved_item
    assert "ranked_candidates" in saved_item
    assert "feature_analysis" in saved_item
