import os
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")

os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(model_version: str, horizon: int) -> str:
    return os.path.join(MODEL_DIR, f"catboost_h{horizon}_v{model_version}.cbm")

def get_metadata_path(model_version: str) -> str:
    return os.path.join(MODEL_DIR, f"metadata_v{model_version}.pkl")

def save_model_artifacts(model_version: str, models: dict, metadata: dict):
    for h, model in models.items():
        path = get_model_path(model_version, h)
        model.save_model(path)
        
    meta_path = get_metadata_path(model_version)
    joblib.dump(metadata, meta_path)

def load_model_artifacts(model_version: str) -> tuple:
    models = {}
    for h in [1, 2, 3]:
        path = get_model_path(model_version, h)
        if os.path.exists(path):
            from catboost import CatBoostRegressor
            cb = CatBoostRegressor()
            cb.load_model(path)
            models[h] = cb
            
    meta_path = get_metadata_path(model_version)
    metadata = {}
    if os.path.exists(meta_path):
        metadata = joblib.load(meta_path)

    return models, metadata
