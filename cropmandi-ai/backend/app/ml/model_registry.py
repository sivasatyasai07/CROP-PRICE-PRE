import os
import joblib
import logging
import hashlib
from datetime import datetime
from typing import Dict, Tuple, Optional, Any, List
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Search candidate directories for model artifacts
def find_model_dir() -> str:
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models"),
        os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models"),
        os.path.join(os.getcwd(), "cropmandi-ai", "ml", "models"),
        os.path.join(os.getcwd(), "ml", "models"),
    ]
    for c in candidates:
        norm = os.path.abspath(c)
        if os.path.exists(norm) and os.path.isdir(norm):
            return norm
    # Default fallback
    default_dir = os.path.abspath(candidates[0])
    os.makedirs(default_dir, exist_ok=True)
    return default_dir

MODEL_DIR = find_model_dir()


def get_model_path(model_version: str, horizon: int) -> str:
    v = model_version.lstrip("v")
    possible_names = [
        f"catboost_h{horizon}_v{model_version}.cbm",
        f"catboost_h{horizon}_vv{v}.cbm",
        f"catboost_h{horizon}_v{v}.cbm",
    ]
    for name in possible_names:
        p = os.path.join(MODEL_DIR, name)
        if os.path.exists(p):
            return p
    return os.path.join(MODEL_DIR, possible_names[0])


def get_metadata_path(model_version: str) -> str:
    v = model_version.lstrip("v")
    possible_names = [
        f"metadata_v{model_version}.pkl",
        f"metadata_vv{v}.pkl",
        f"metadata_v{v}.pkl",
    ]
    for name in possible_names:
        p = os.path.join(MODEL_DIR, name)
        if os.path.exists(p):
            return p
    return os.path.join(MODEL_DIR, possible_names[0])


def get_available_model_versions() -> List[str]:
    """Scans MODEL_DIR and returns sorted list of all model versions with complete H1, H2, H3 and metadata."""
    if not os.path.exists(MODEL_DIR):
        return []
    
    files = os.listdir(MODEL_DIR)
    h1_versions = set()
    for f in files:
        if f.startswith("catboost_h1_") and f.endswith(".cbm"):
            v_part = f[len("catboost_h1_"):-len(".cbm")].lstrip("v")
            h1_versions.add(v_part)

    valid_versions = []
    for v in sorted(h1_versions, reverse=True):
        p1 = get_model_path(v, 1)
        p2 = get_model_path(v, 2)
        p3 = get_model_path(v, 3)
        pm = get_metadata_path(v)
        if os.path.exists(p1) and os.path.exists(p2) and os.path.exists(p3) and os.path.exists(pm):
            valid_versions.append(f"v{v}")
    return valid_versions


def get_active_model_version(db: Optional[Session] = None) -> str:
    """Authoritatively resolves the active model version from DB ModelRun or newest valid artifact."""
    if db:
        try:
            from app.models import ModelRun
            active_run = db.query(ModelRun).filter(ModelRun.is_active == True).order_by(ModelRun.created_at.desc()).first()
            if active_run and active_run.model_version:
                v = active_run.model_version
                p1 = get_model_path(v, 1)
                p2 = get_model_path(v, 2)
                p3 = get_model_path(v, 3)
                if os.path.exists(p1) and os.path.exists(p2) and os.path.exists(p3):
                    return v
        except Exception as exc:
            logger.warning("Could not query active ModelRun from DB: %s", exc)

    available = get_available_model_versions()
    if available:
        return available[0]
    
    return "v20260818_153724"


def save_model_artifacts(model_version: str, models: dict, metadata: dict):
    for h, model in models.items():
        path = get_model_path(model_version, h)
        model.save_model(path)
        
    meta_path = get_metadata_path(model_version)
    joblib.dump(metadata, meta_path)


def load_model_artifacts(model_version: str) -> Tuple[Dict[int, Any], Dict[str, Any]]:
    models = {}
    for h in [1, 2, 3]:
        path = get_model_path(model_version, h)
        if os.path.exists(path):
            try:
                from catboost import CatBoostRegressor
                cb = CatBoostRegressor()
                cb.load_model(path)
                models[h] = cb
            except Exception as exc:
                logger.error("Failed to load CatBoost artifact for H%d from %s: %s", h, path, exc)
                
    meta_path = get_metadata_path(model_version)
    metadata = {}
    if os.path.exists(meta_path):
        try:
            metadata = joblib.load(meta_path)
        except Exception as exc:
            logger.error("Failed to load metadata artifact from %s: %s", meta_path, exc)

    return models, metadata


def compute_file_sha256(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def check_model_health(db: Optional[Session] = None, requested_version: Optional[str] = None) -> Dict[str, Any]:
    """Generates a complete diagnostic report for the deployed ML model artifacts."""
    active_version = get_active_model_version(db)
    target_ver = requested_version or active_version
    
    h1_path = get_model_path(target_ver, 1)
    h2_path = get_model_path(target_ver, 2)
    h3_path = get_model_path(target_ver, 3)
    meta_path = get_metadata_path(target_ver)

    h1_exists = os.path.exists(h1_path)
    h2_exists = os.path.exists(h2_path)
    h3_exists = os.path.exists(h3_path)
    meta_exists = os.path.exists(meta_path)

    models, metadata = load_model_artifacts(target_ver)
    h1_loaded = 1 in models
    h2_loaded = 2 in models
    h3_loaded = 3 in models

    feature_schema_match = True
    feature_count = 0
    if metadata and "feature_columns" in metadata:
        from app.ml.feature_engineering import FEATURE_COLUMNS
        feature_count = len(metadata["feature_columns"])
        feature_schema_match = metadata["feature_columns"] == FEATURE_COLUMNS

    all_loaded = h1_loaded and h2_loaded and h3_loaded and meta_exists

    if all_loaded and feature_schema_match:
        status = "ready"
        message = f"All multi-horizon CatBoost models (H1, H2, H3) and conformal metadata for version {target_ver} loaded successfully."
        error_msg = None
    elif not (h1_exists or h2_exists or h3_exists):
        status = "missing"
        message = "Model artifacts are not available in this deployment."
        error_msg = message
    elif requested_version and requested_version != active_version:
        status = "version_mismatch"
        message = f"Requested version {requested_version} does not match active deployed version {active_version}."
        error_msg = message
    elif not feature_schema_match:
        status = "schema_mismatch"
        message = "Loaded model feature schema does not match runtime FEATURE_COLUMNS definition."
        error_msg = message
    else:
        status = "load_error"
        message = "One or more horizon model artifacts failed to load properly."
        error_msg = message

    return {
        "status": status,
        "requested_version": requested_version or active_version,
        "resolved_version": active_version,
        "active_model_version": active_version,
        "h1_exists": h1_exists,
        "h2_exists": h2_exists,
        "h3_exists": h3_exists,
        "metadata_exists": meta_exists,
        "h1_loaded": h1_loaded,
        "h2_loaded": h2_loaded,
        "h3_loaded": h3_loaded,
        "error": error_msg,
        "artifact_directory": "cropmandi-ai/ml/models",
        "horizons": {
            "h1": {
                "exists": h1_exists,
                "loaded": h1_loaded,
                "path": os.path.basename(h1_path) if h1_exists else None,
                "sha256": compute_file_sha256(h1_path) if h1_exists else None,
            },
            "h2": {
                "exists": h2_exists,
                "loaded": h2_loaded,
                "path": os.path.basename(h2_path) if h2_exists else None,
                "sha256": compute_file_sha256(h2_path) if h2_exists else None,
            },
            "h3": {
                "exists": h3_exists,
                "loaded": h3_loaded,
                "path": os.path.basename(h3_path) if h3_exists else None,
                "sha256": compute_file_sha256(h3_path) if h3_exists else None,
            }
        },
        "feature_count": feature_count,
        "feature_schema_match": feature_schema_match,
        "message": message,
        "checked_at": datetime.utcnow().isoformat()
    }
