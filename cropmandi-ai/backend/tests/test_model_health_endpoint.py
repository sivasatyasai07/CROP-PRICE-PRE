import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.model_registry import check_model_health, get_active_model_version, get_available_model_versions

client = TestClient(app)

def test_models_health_endpoint():
    """Verify GET /api/v1/models/health returns complete status schema."""
    response = client.get("/api/v1/models/health")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] in ["ready", "missing", "version_mismatch", "load_error"]
    assert "requested_version" in data
    assert "resolved_version" in data
    assert "h1_exists" in data
    assert "h2_exists" in data
    assert "h3_exists" in data
    assert "metadata_exists" in data
    assert "h1_loaded" in data
    assert "h2_loaded" in data
    assert "h3_loaded" in data
    assert "error" in data
    
    # In this deployment, all models are available and ready
    assert data["status"] == "ready"
    assert data["h1_exists"] is True
    assert data["h2_exists"] is True
    assert data["h3_exists"] is True
    assert data["metadata_exists"] is True
    assert data["h1_loaded"] is True
    assert data["h2_loaded"] is True
    assert data["h3_loaded"] is True
    assert data["error"] is None


def test_model_version_resolution():
    """Verify model version resolution finds available artifacts."""
    available = get_available_model_versions()
    assert len(available) > 0
    active = get_active_model_version()
    assert active is not None
    assert active in available
