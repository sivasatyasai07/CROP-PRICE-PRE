import pytest
import io
import os
import sys
import json
from unittest.mock import patch, MagicMock
from PIL import Image

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.disease import DiseaseAnalysisResult
from app.services.plantnet_disease_service import (
    validate_image,
    classify_plantnet_error,
    validate_plantnet_response,
    normalize_plantnet_result,
    identify_plant_image,
    test_plantnet_connection as get_plantnet_connection_health,
    map_plantnet_species
)
from app.services.disease_history_store import (
    append_analysis,
    read_user_history,
    delete_analysis
)


@pytest.fixture(autouse=True)
def mock_gemini_stage2():
    with patch("app.services.gemini_crop_disease_service.analyze_crop_image") as mock_gem:
        mock_res = MagicMock()
        mock_res.disease = MagicMock(name="Leaf Spot", confidence=0.85)
        mock_res.health_status = "diseased"
        mock_res.health_assessment = None
        mock_res.primary_diagnosis = MagicMock(name="Leaf Spot")
        mock_res.alternative_diagnoses = []
        mock_res.symptoms = ["Yellowing leaf margins"]
        mock_res.possible_causes = ["Fungal spores"]
        mock_res.management = ["Apply fungicide"]
        mock_res.immediate_actions = ["Apply fungicide"]
        mock_res.prevention = ["Crop rotation"]
        mock_res.chemical_control_guidance = None
        mock_res.risk_level = "medium"
        mock_gem.return_value = (mock_res, MagicMock(model_name="gemini-3.6-flash"))
        yield mock_gem


@pytest.fixture
def sample_image_bytes():
    img = Image.new("RGB", (200, 200), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def mock_tomato_plantnet_json():
    return {
        "query": {"project": "all", "images": ["img1"], "organs": ["leaf"]},
        "language": "en",
        "bestMatch": "Solanum lycopersicum L.",
        "results": [
            {
                "score": 0.915,
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
                "score": 0.032,
                "species": {
                    "scientificNameWithoutAuthor": "Capsicum annuum",
                    "scientificNameAuthorship": "L.",
                    "genus": {"scientificNameWithoutAuthor": "Capsicum"},
                    "family": {"scientificNameWithoutAuthor": "Solanaceae"},
                    "commonNames": ["Chilli pepper", "Green Chilli"],
                    "scientificName": "Capsicum annuum L."
                }
            }
        ]
    }


def test_1_valid_image_and_valid_plantnet_response(sample_image_bytes, mock_tomato_plantnet_json):
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_tomato_plantnet_json
        mock_post.return_value = mock_resp

        with patch("app.config.settings.PLANTNET_API_KEY", "test_key"):
            res, model = identify_plant_image(
                image_bytes=sample_image_bytes,
                selected_crop="Tomato"
            )

            assert res.analysis_status == "success"
            assert res.detected_crop == "Tomato"
            assert res.plantnet_score == 0.915
            assert res.crop_match_status == "match"
            assert len(res.plantnet_results) == 2
            assert res.plantnet_results[0].scientific_name == "Solanum lycopersicum L."


def test_2_missing_api_key(sample_image_bytes):
    with patch("app.config.settings.PLANTNET_API_KEY", ""), patch("app.config.settings.GEMINI_API_KEY", ""):
        res, model = identify_plant_image(sample_image_bytes)
        assert res.analysis_status == "service_error"
        assert res.identification_status == "unavailable"


def test_3_invalid_api_key(sample_image_bytes):
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_post.return_value = mock_resp

        with patch("app.config.settings.PLANTNET_API_KEY", "invalid_key"), patch("app.config.settings.GEMINI_API_KEY", ""):
            res, model = identify_plant_image(sample_image_bytes)
            assert res.analysis_status == "plantnet_authentication_error"


def test_4_timeout_handling(sample_image_bytes):
    import requests
    with patch("requests.post", side_effect=requests.Timeout("Connection timeout")):
        with patch("app.config.settings.PLANTNET_API_KEY", "test_key"), patch("app.config.settings.GEMINI_API_KEY", ""):
            res, model = identify_plant_image(sample_image_bytes)
            assert res.analysis_status == "plantnet_timeout"


def test_5_rate_limit_handling(sample_image_bytes):
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"
        mock_post.return_value = mock_resp

        with patch("app.config.settings.PLANTNET_API_KEY", "test_key"), patch("app.config.settings.GEMINI_API_KEY", ""):
            res, model = identify_plant_image(sample_image_bytes)
            assert res.analysis_status == "plantnet_rate_limit_error"


def test_gemini_failure_fallback_to_plantnet(sample_image_bytes, mock_tomato_plantnet_json):
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_tomato_plantnet_json
        mock_post.return_value = mock_resp

        with patch("app.services.gemini_crop_disease_service.analyze_crop_image", side_effect=Exception("Gemini quota error")), \
             patch("app.config.settings.PLANTNET_API_KEY", "valid_plantnet_key"), \
             patch("app.config.settings.GEMINI_API_KEY", "gemini_key"):
            res, model = identify_plant_image(sample_image_bytes, selected_crop="Tomato")
            assert res.analysis_status == "success"
            assert res.detected_crop == "Tomato"
            assert res.provider == "PlantNet (Botanical Fallback)"
            assert any("Gemini pathology AI was temporarily unavailable" in w.issue for w in (res.validation_warnings or []))


def test_6_invalid_image_validation():
    valid, err = validate_image(b"", "image/jpeg")
    assert not valid
    assert "upload an image" in err.lower()

    valid, err = validate_image(b"corrupted binary", "image/jpeg")
    assert not valid
    assert "corrupted" in err.lower()


def test_7_empty_plantnet_results():
    empty_json = {"query": {}, "results": []}
    res = normalize_plantnet_result(raw_json=empty_json, selected_crop="Tomato")
    assert res.analysis_status == "insufficient_evidence"
    assert res.detected_crop is None
    assert res.plantnet_score is None


def test_8_malformed_json_response():
    valid, cat, results = validate_plantnet_response("not a dict", 200)
    assert not valid
    assert cat == "plantnet_invalid_response"


def test_9_missing_species_fields():
    malformed_results = {
        "results": [{"score": 0.5, "species": {}}]
    }
    res = normalize_plantnet_result(raw_json=malformed_results)
    assert res.analysis_status == "success"
    assert res.detected_crop == "Unknown species"


def test_10_invalid_score_handling():
    invalid_score_json = {
        "results": [{"score": "not_a_number", "species": {"scientificName": "Test"}}]
    }
    # Should handle gracefully without throwing uncaught exceptions
    valid, _, _ = validate_plantnet_response(invalid_score_json, 200)
    assert valid


def test_11_crop_match(mock_tomato_plantnet_json):
    res = normalize_plantnet_result(mock_tomato_plantnet_json, selected_crop="Tomato")
    assert res.crop_match_status == "match"


def test_12_crop_mismatch(mock_tomato_plantnet_json):
    res = normalize_plantnet_result(mock_tomato_plantnet_json, selected_crop="Potato")
    assert res.crop_match_status == "mismatch"


def test_13_outside_vocabulary_crop():
    outside_json = {
        "results": [
            {
                "score": 0.85,
                "species": {
                    "scientificNameWithoutAuthor": "Quercus robur",
                    "genus": {"scientificNameWithoutAuthor": "Quercus"},
                    "family": {"scientificNameWithoutAuthor": "Fagaceae"},
                    "commonNames": ["English oak"],
                    "scientificName": "Quercus robur L."
                }
            }
        ]
    }
    res = normalize_plantnet_result(outside_json)
    assert res.detected_crop == "English oak"
    assert res.crop_recognition.best_crop.crop_status == "recognized_outside_configured_vocabulary"


def test_14_15_user_history_isolation():
    user_a = "user_test_alpha"
    user_b = "user_test_beta"

    rec_a = {
        "analysis_id": "ana_alpha_1",
        "user_id": user_a,
        "created_at": "2026-08-19T10:00:00Z",
        "provider": "PlantNet",
        "detected_crop": "Tomato",
        "plantnet_score": 0.92
    }
    append_analysis(user_a, "alpha@test.com", rec_a)

    hist_a = read_user_history(user_a)
    hist_b = read_user_history(user_b)

    ids_a = [a["analysis_id"] for a in hist_a.get("analyses", [])]
    ids_b = [b["analysis_id"] for b in hist_b.get("analyses", [])]

    assert "ana_alpha_1" in ids_a
    assert "ana_alpha_1" not in ids_b

    # Cleanup
    delete_analysis(user_a, "ana_alpha_1")


def test_16_provider_error_not_labeled_unidentified_crop():
    err_cat, _ = classify_plantnet_error(503)
    assert err_cat == "plantnet_unavailable"
    assert err_cat != "unidentified"


def test_17_no_api_key_in_health_or_response():
    health = get_plantnet_connection_health()
    health_str = json.dumps(health)
    assert "api-key" not in health_str
    assert "AQ." not in health_str


def test_18_disease_diagnosis_not_claimed_from_plantnet():
    empty_json = {"results": [{"score": 0.88, "species": {"scientificName": "Solanum lycopersicum"}}]}
    res = normalize_plantnet_result(empty_json)
    assert res.disease_status == "requires_second_stage"
    assert "preliminary" in res.disclaimer.lower() or "expert" in res.disclaimer.lower()
