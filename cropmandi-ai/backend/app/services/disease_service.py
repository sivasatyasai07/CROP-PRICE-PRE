import os
import json
import io
import numpy as np
from PIL import Image
import onnxruntime as ort
from typing import Dict, Any, List

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "disease_model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.onnx")
CLASS_NAMES_PATH = os.path.join(MODEL_DIR, "class_names.json")

# Global session and class names cache
_onnx_session = None
_class_names: List[str] = []

# Supported crops in PlantVillage MobileNetV3 model
SUPPORTED_CROPS = {
    "tomato": ["tomato"],
    "potato": ["potato"],
    "green chilli": ["pepper", "chilli", "chili"],
    "brinjal": [],
}

SUPPORTED_CROP_NAMES = ["Tomato", "Potato", "Green Chilli"]

def get_onnx_session():
    global _onnx_session, _class_names
    if _onnx_session is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(CLASS_NAMES_PATH):
            raise FileNotFoundError(f"Disease model files missing in {MODEL_DIR}")
        
        with open(CLASS_NAMES_PATH, "r") as f:
            _class_names = json.load(f)
            
        _onnx_session = ort.InferenceSession(MODEL_PATH)
    return _onnx_session, _class_names


def is_crop_supported(crop_name: str) -> bool:
    if not crop_name:
        return False
    c_lower = crop_name.lower().strip()
    return any(c_lower in sc or sc in c_lower for sc in ["tomato", "potato", "chilli", "chili", "pepper", "capsicum"])


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess raw image bytes for MobileNetV3 (ImageNet normalization)
    Input shape: (1, 3, 224, 224)
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_resized = img.resize((224, 224), Image.Resampling.BILINEAR)
    img_arr = np.array(img_resized, dtype=np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_norm = (img_arr - mean) / std

    # Transpose (H, W, C) -> (C, H, W) and add batch dimension -> (1, C, H, W)
    input_tensor = np.transpose(img_norm, (2, 0, 1))
    return np.expand_dims(input_tensor, axis=0).astype(np.float32)


def clean_disease_name(raw_label: str) -> str:
    """Format label string to clean human readable title"""
    formatted = raw_label.replace("___", " - ").replace("__", " ").replace("_", " ")
    return " ".join([word.capitalize() for word in formatted.split()])


def run_disease_inference(image_bytes: bytes, selected_crop: str) -> Dict[str, Any]:
    if not is_crop_supported(selected_crop):
        return {
            "status": "unsupported_crop",
            "message": f"Disease detection is currently unavailable for {selected_crop}. Supported crops: {', '.join(SUPPORTED_CROP_NAMES)}."
        }

    try:
        session, class_names = get_onnx_session()
        input_tensor = preprocess_image(image_bytes)

        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name

        res = session.run([output_name], {input_name: input_tensor})
        logits = res[0][0]

        # Softmax calculation
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        # Get top indices
        top_indices = np.argsort(probs)[::-1]
        top1_idx = top_indices[0]
        top1_confidence = float(probs[top1_idx])

        # Low confidence threshold (40%)
        if top1_confidence < 0.40:
            return {
                "status": "low_confidence",
                "message": "The image could not be identified reliably. Please capture a clearer image of the leaf with good lighting."
            }

        top_predictions = []
        for idx in top_indices[:3]:
            raw_label = class_names[idx]
            top_predictions.append({
                "label": raw_label,
                "display_label": clean_disease_name(raw_label),
                "confidence": round(float(probs[idx]), 3)
            })

        top1_raw_label = class_names[top1_idx]
        return {
            "status": "success",
            "crop": selected_crop,
            "disease": top1_raw_label,
            "disease_display_name": clean_disease_name(top1_raw_label),
            "confidence": round(top1_confidence, 3),
            "top_predictions": top_predictions
        }

    except Exception as e:
        return {
            "status": "model_error",
            "message": f"Error running MobileNetV3 inference: {str(e)}"
        }
