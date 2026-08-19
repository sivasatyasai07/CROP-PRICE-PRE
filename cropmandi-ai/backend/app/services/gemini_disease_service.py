"""
Gemini Disease Service facade redirecting to gemini_crop_disease_service.
"""
from app.services.gemini_crop_disease_service import (
    analyze_crop_image,
    create_open_set_crop_disease_prompt as build_disease_prompt,
    create_open_set_crop_disease_prompt as create_disease_analysis_prompt,
    validate_and_normalize_open_set_response as validate_and_normalize_response,
    create_fallback_open_set_result as create_fallback_result,
    choose_best_candidate,
    calculate_display_confidence,
    MODEL_CASCADE,
    INITIAL_VOCABULARY
)
from app.config import settings

def get_model_metadata():
    return {
        "provider": "Google Gemini",
        "model_name": getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash"),
        "prompt_version": getattr(settings, "DISEASE_PROMPT_VERSION", "crop-disease-v2"),
        "temperature": getattr(settings, "GEMINI_TEMPERATURE", 0.1),
        "timeout_seconds": getattr(settings, "GEMINI_TIMEOUT_SECONDS", 60),
    }
