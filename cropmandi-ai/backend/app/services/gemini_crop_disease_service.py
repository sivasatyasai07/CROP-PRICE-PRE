import os
import io
import json
import time
import logging
from typing import List, Optional, Dict, Any, Tuple
from PIL import Image
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import settings
from app.services.cv_feature_extractor import analyze_botanical_features
from app.schemas.disease import (
    DiseaseAnalysisResult,
    CropInfo,
    DiseaseInfo,
    ImageQualityAssessment,
    CropRecognition,
    CropCandidate,
    BestCrop,
    CropComparison,
    AmbiguityInfo,
    NextImageRequest,
    LeafMarginAnalysis,
    FeatureAnalysis,
    PlantPartInfo,
    HealthAssessment,
    PrimaryDiagnosis,
    AlternativeDiagnosis,
    ChemicalControlGuidance,
    ModelInfo,
    ValidationWarning
)

logger = logging.getLogger(__name__)

INITIAL_VOCABULARY = [
    "Tomato", "Potato", "Brinjal", "Carrot", "Cabbage", "Beetroot",
    "Chilli", "Capsicum", "Okra", "Onion", "Garlic", "Coriander",
    "Spinach", "Drumstick", "Cucumber", "Pumpkin", "Bottle gourd",
    "Bitter gourd", "Ridge gourd", "Beans", "Peas", "Cauliflower",
    "Radish", "Turnip", "Sweet potato", "Yam", "Banana", "Mango",
    "Papaya", "Guava", "Grapes", "Pomegranate", "Watermelon",
    "Muskmelon", "Rice", "Wheat", "Maize", "Sorghum", "Pearl millet",
    "Finger millet", "Groundnut", "Soybean", "Cotton", "Sugarcane",
    "Sunflower", "Sesame", "Red gram", "Green gram", "Black gram",
    "Chickpea", "Turmeric", "Ginger", "Black pepper", "Tea",
    "Coffee", "Coconut", "Arecanut"
]

LANGUAGE_NAME_MAP = {
    "en": "English",
    "te": "Telugu (తెలుగు)",
    "hi": "Hindi (हिंदी)",
    "ta": "Tamil (தமிழ்)",
    "ml": "Malayalam (മലയാളം)"
}

MODEL_CASCADE = [
    getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash")
]


def calculate_display_confidence(confidence: Optional[float]) -> Dict[str, Any]:
    """Computes presentation-layer display metrics."""
    if confidence is None or not isinstance(confidence, (int, float)):
        return {
            "reported_percentage": None,
            "display_text": "Confidence unavailable",
            "level": "Unavailable"
        }
    
    pct = round(float(confidence) * 100)
    level = "High" if confidence >= 0.75 else ("Moderate" if confidence >= 0.45 else "Low")
    return {
        "reported_percentage": pct,
        "display_text": f"{pct}%",
        "level": level
    }


def choose_best_candidate(candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    valid = []
    for candidate in candidates:
        prob = candidate.get("combined_probability") or candidate.get("confidence") or candidate.get("gemini_original_probability")
        if prob is not None and isinstance(prob, (int, float)) and 0.0 <= prob <= 1.0:
            valid.append((candidate, float(prob)))
            
    if not valid:
        return None
        
    valid.sort(key=lambda item: item[1], reverse=True)
    best_candidate, best_probability = valid[0]
    
    status = "identified" if best_probability >= 0.75 else ("probable" if best_probability >= 0.45 else "low_confidence")
    return {
        "candidate": best_candidate,
        "probability": best_probability,
        "identification_status": status
    }


def create_open_set_crop_disease_prompt(
    selected_crop: Optional[str] = None,
    selected_plant_part: Optional[str] = None,
    user_symptoms: Optional[str] = None,
    user_notes: Optional[str] = None,
    location: Optional[str] = None,
    growth_stage: Optional[str] = None,
    language: str = "en"
) -> str:
    """
    Builds the streamlined, farmer-friendly plant vision & disease diagnosis prompt for Gemini Flash.
    """
    target_lang_name = LANGUAGE_NAME_MAP.get(language.lower(), "English")
    
    multilingual_clause = ""
    if language.lower() != "en":
        multilingual_clause = f"""
==================================================
CRITICAL MULTILINGUAL INSTRUCTION
==================================================
The farmer requested the diagnostic result in {target_lang_name}.
You MUST generate the crop name, disease name, symptoms, possible causes, management actions, prevention, and explanations in {target_lang_name}.
Include the standard English names in parentheses where helpful, e.g. 'టమోటా (Tomato)', 'ముందస్తు తెగులు (Early Blight)'.
JSON property keys MUST remain strictly in English as specified below.
"""

    return f"""You are an expert Agricultural Plant Pathologist analyzing a crop photograph.

CRITICAL DIAGNOSIS PROTOCOL:
1. IDENTIFY THE CROP FIRST:
   - Identify the cultivated crop (e.g., Tomato, Paddy, Maize, Groundnut, Cotton, Chilli, Mango, Brinjal, Onion, Potato, etc.) directly from visible botanical features.
   - Do NOT expect the user to select the crop. You must recognize it yourself from the image.
   - If the image is not a plant or crop, set "analysis_status" to "non_plant_image".
   - If the crop is unclear or cannot be identified reliably, set "analysis_status" to "uncertain" and confidence to low.

2. IDENTIFY THE PLANT PART:
   - Identify which anatomical plant part is shown (e.g., Leaf, Stem, Fruit, Flower, Root, Whole Plant).

3. DETERMINE HEALTH STATUS:
   - Determine if the plant is "healthy", "diseased", or "uncertain".

4. PREDICT THE MOST LIKELY DISEASE:
   - Predict the most probable disease or condition based strictly on visible lesions, discoloration, or abnormalities.
   - Do not invent a disease. If the plant is healthy, set disease name to "Healthy Plant" or "Healthy".

5. EXPLAIN SYMPTOMS, CAUSES, AND GUIDANCE:
   - List visible symptoms in simple, clear, farmer-friendly terms.
   - Explain possible causes (pathogen, fungal, bacterial, environmental, etc.).
   - Provide practical "What to Do" management actions.
   - Provide preventive guidance for future crop protection.
   - Set risk level to "low", "medium", "high", or "uncertain".

{multilingual_clause}

OUTPUT SCHEMA (Return ONLY a single valid JSON object matching this exact structure):
{{
  "analysis_status": "success",
  "crop": {{
    "name": "Tomato",
    "confidence": 0.92
  }},
  "plant_part": "Leaf",
  "health_status": "diseased",
  "disease": {{
    "name": "Early Blight",
    "confidence": 0.91
  }},
  "symptoms": [
    "Concentric dark brown rings on lower leaves",
    "Yellow chlorotic halo around spots"
  ],
  "possible_causes": [
    "Alternaria solani fungal infection",
    "High humidity and prolonged leaf wetness"
  ],
  "management": [
    "Prune and destroy infected lower leaves",
    "Apply recommended copper-based protective fungicide"
  ],
  "prevention": [
    "Maintain adequate plant spacing for airflow",
    "Avoid overhead irrigation to keep foliage dry",
    "Practice crop rotation with non-solanaceous crops"
  ],
  "risk_level": "medium",
  "limitations": [
    "Assessment based on visible symptoms in the uploaded image"
  ],
  "disclaimer": "This is an AI-assisted preliminary assessment. Confirm with your local agricultural extension officer before applying chemical sprays."
}}
"""


def _sanitize_confidence(val: Any, field_name: str, warnings: List[ValidationWarning]) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        if 0.0 <= f <= 1.0:
            return round(f, 4)
        if 1.0 < f <= 100.0:
            return round(f / 100.0, 4)
        warnings.append(ValidationWarning(
            field=field_name,
            issue=f"Value {val} out of range [0.0, 1.0]",
            action="Set to None"
        ))
        return None
    except (ValueError, TypeError):
        warnings.append(ValidationWarning(
            field=field_name,
            issue=f"Could not parse '{val}' as float",
            action="Set to None"
        ))
        return None


def validate_and_normalize_open_set_response(
    raw_data: Dict[str, Any],
    method2_features: Optional[Dict[str, Any]] = None,
    selected_crop: Optional[str] = None,
    language: str = "en"
) -> DiseaseAnalysisResult:
    """
    Validates and normalizes Gemini's JSON response into DiseaseAnalysisResult.
    """
    warnings: List[ValidationWarning] = []

    raw_status = str(raw_data.get("analysis_status", "success")).lower().strip()
    if raw_status not in ["success", "uncertain", "non_plant_image"]:
        if "non_plant" in raw_status:
            analysis_status = "non_plant_image"
        elif "unclear" in raw_status or "uncertain" in raw_status or "error" in raw_status:
            analysis_status = "uncertain"
        else:
            analysis_status = "success"
    else:
        analysis_status = raw_status

    plant_detected = analysis_status != "non_plant_image"

    # 1. Parse Crop Info
    raw_crop = raw_data.get("crop")
    if isinstance(raw_crop, dict):
        crop_name = str(raw_crop.get("name") or "Unidentified Plant")
        crop_conf = _sanitize_confidence(raw_crop.get("confidence"), "crop.confidence", warnings)
    elif isinstance(raw_crop, str):
        crop_name = raw_crop
        crop_conf = None
    else:
        # Check backward-compatible crop_recognition
        cr_raw = raw_data.get("crop_recognition", {})
        best_raw = cr_raw.get("best_crop", {})
        crop_name = str(best_raw.get("name") or cr_raw.get("crop_name") or "Unidentified Plant")
        crop_conf = _sanitize_confidence(best_raw.get("gemini_original_probability") or cr_raw.get("confidence"), "crop.confidence", warnings)

    crop_info = CropInfo(name=crop_name, confidence=crop_conf)

    # 2. Parse Plant Part
    raw_part = raw_data.get("plant_part", "Leaf")
    if isinstance(raw_part, dict):
        plant_part_str = str(raw_part.get("name") or "Leaf")
        part_conf = _sanitize_confidence(raw_part.get("confidence"), "plant_part.confidence", warnings)
    else:
        plant_part_str = str(raw_part or "Leaf")
        part_conf = None

    # 3. Parse Health Status
    raw_health = str(raw_data.get("health_status") or raw_data.get("health_assessment", {}).get("status") or "diseased").lower().strip()
    if "healthy" in raw_health:
        health_status = "healthy"
    elif "non_plant" in raw_health or analysis_status == "non_plant_image":
        health_status = "uncertain"
    elif "uncertain" in raw_health or "unclear" in raw_health:
        health_status = "uncertain"
    else:
        health_status = "diseased"

    # 4. Parse Disease Info
    raw_disease = raw_data.get("disease")
    if isinstance(raw_disease, dict):
        disease_name = str(raw_disease.get("name") or ("Healthy Plant" if health_status == "healthy" else "Visual Anomaly"))
        disease_conf = _sanitize_confidence(raw_disease.get("confidence"), "disease.confidence", warnings)
    elif isinstance(raw_disease, str):
        disease_name = raw_disease
        disease_conf = None
    else:
        pd_raw = raw_data.get("primary_diagnosis", {})
        disease_name = str(pd_raw.get("name") or ("Healthy Plant" if health_status == "healthy" else "Visual Anomaly"))
        disease_conf = _sanitize_confidence(pd_raw.get("confidence"), "disease.confidence", warnings)

    disease_info = DiseaseInfo(name=disease_name, confidence=disease_conf)

    # 5. Parse Lists
    symptoms = [str(s) for s in raw_data.get("symptoms", []) if s]
    possible_causes = [str(c) for c in raw_data.get("possible_causes", []) if c]
    management = [str(m) for m in (raw_data.get("management") or raw_data.get("immediate_actions", [])) if m]
    prevention = [str(p) for p in raw_data.get("prevention", []) if p]
    limitations = [str(l) for l in raw_data.get("limitations", []) if l]
    risk_level = str(raw_data.get("risk_level", "medium")).lower().strip()
    if risk_level not in ["low", "medium", "high", "uncertain"]:
        risk_level = "medium"

    disclaimer = str(raw_data.get("disclaimer") or "This is an AI-assisted preliminary assessment based on visual evidence. Please confirm with your local agricultural extension officer.")

    # 6. Backward compatibility objects
    ident_status = "identified" if (crop_conf and crop_conf >= 0.75) else ("probable" if (crop_conf and crop_conf >= 0.45) else "low_confidence")
    best_crop = BestCrop(
        name=crop_name,
        category="cultivated_plant",
        crop_status="recognized",
        gemini_original_probability=crop_conf,
        combined_probability=crop_conf,
        final_selection_source="gemini"
    )

    crop_rec = CropRecognition(
        identification_status=ident_status,
        best_crop=best_crop,
        ranked_candidates=[
            CropCandidate(
                name=crop_name,
                category="cultivated_plant",
                crop_status="recognized",
                gemini_original_probability=crop_conf,
                combined_probability=crop_conf,
                supporting_evidence=symptoms[:2]
            )
        ],
        feature_analysis=FeatureAnalysis(),
        ambiguity=AmbiguityInfo(status="low", top_candidate_gap=None, message="")
    )

    crop_comparison = CropComparison(
        user_selected_crop=selected_crop,
        detected_best_crop=crop_name,
        match_status="not_provided" if not selected_crop else ("match" if selected_crop.lower() in crop_name.lower() else "uncertain"),
        reason=f"Crop identified as {crop_name}."
    )

    health_assessment = HealthAssessment(
        status=health_status,
        confidence=disease_conf,
        visible_evidence=symptoms
    )

    primary_diagnosis = PrimaryDiagnosis(
        name=disease_name,
        category="general",
        confidence=disease_conf,
        evidence=symptoms
    )

    return DiseaseAnalysisResult(
        analysis_status=analysis_status,
        crop=crop_info,
        plant_part=plant_part_str,
        health_status=health_status,
        disease=disease_info,
        symptoms=symptoms,
        possible_causes=possible_causes,
        management=management,
        prevention=prevention,
        risk_level=risk_level,
        limitations=limitations,
        disclaimer=disclaimer,
        plant_detected=plant_detected,
        image_quality=ImageQualityAssessment(
            status="acceptable" if analysis_status == "success" else "insufficient_evidence",
            original_confidence=crop_conf,
            issues=[]
        ),
        crop_recognition=crop_rec,
        crop_comparison=crop_comparison,
        next_image_request=NextImageRequest(needed=analysis_status == "uncertain"),
        health_assessment=health_assessment,
        primary_diagnosis=primary_diagnosis,
        alternative_diagnoses=[],
        immediate_actions=management,
        chemical_control_guidance=ChemicalControlGuidance(
            provided=False,
            message="Consult local agricultural extension officers before applying chemical sprays."
        ),
        model_disclaimer=disclaimer,
        language=language,
        validation_warnings=warnings
    )


def create_fallback_open_set_result(
    reason: str,
    selected_crop: Optional[str] = None,
    language: str = "en",
    status: str = "uncertain"
) -> DiseaseAnalysisResult:
    """Generates a clean structured fallback result for inconclusive or failed analyses."""
    return DiseaseAnalysisResult(
        analysis_status=status,
        crop=CropInfo(name="Unidentified Plant", confidence=None),
        plant_part="Unknown",
        health_status="uncertain",
        disease=DiseaseInfo(name="Inconclusive", confidence=None),
        symptoms=[],
        possible_causes=[reason],
        management=["Unable to identify the crop/disease reliably. Please upload a clearer image showing a leaf or affected part."],
        prevention=["Inspect crop foliage regularly in good daylight."],
        risk_level="uncertain",
        limitations=[reason],
        disclaimer="This is an AI-assisted preliminary assessment. Please consult an agricultural expert.",
        plant_detected=status != "non_plant_image",
        image_quality=ImageQualityAssessment(
            status="poor" if status == "unclear_image" else "insufficient_evidence",
            issues=[reason]
        ),
        crop_recognition=CropRecognition(
            identification_status="unidentified",
            best_crop=BestCrop(name="Unidentified Plant", category="unknown", crop_status="unrecognized"),
            ranked_candidates=[],
            feature_analysis=FeatureAnalysis()
        ),
        crop_comparison=CropComparison(
            user_selected_crop=selected_crop,
            detected_best_crop="Unidentified Plant",
            match_status="not_provided",
            reason=reason
        ),
        health_assessment=HealthAssessment(status="unclear", confidence=None, visible_evidence=[reason]),
        primary_diagnosis=PrimaryDiagnosis(name="Inconclusive Visual Evidence", category="unclear", confidence=None, evidence=[reason]),
        immediate_actions=["Please upload a clearer image showing a leaf or affected part."],
        language=language,
        validation_warnings=[]
    )


def analyze_crop_image(
    image_bytes_list: List[bytes],
    selected_crop: Optional[str] = None,
    selected_plant_part: Optional[str] = None,
    user_symptoms: Optional[str] = None,
    user_notes: Optional[str] = None,
    location: Optional[str] = None,
    growth_stage: Optional[str] = None,
    language: str = "en"
) -> Tuple[DiseaseAnalysisResult, ModelInfo]:
    """
    Executes the Gemini Flash Vision Crop Recognition and Disease Diagnosis Pipeline.
    """
    if not image_bytes_list:
        raise ValueError("At least one image is required for analysis.")

    # 1. Computer Vision Feature Analysis
    primary_bytes = image_bytes_list[0]
    method2_features = analyze_botanical_features(primary_bytes)

    # 2. PIL Image Validation
    pil_images: List[Image.Image] = []
    for idx, img_b in enumerate(image_bytes_list):
        try:
            img = Image.open(io.BytesIO(img_b))
            img.verify()
            img = Image.open(io.BytesIO(img_b))
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            pil_images.append(img)
        except Exception as exc:
            logger.warning("Image %d failed PIL validation: %s", idx, exc)
            return create_fallback_open_set_result(
                reason="The uploaded image is corrupted or in an unsupported format.",
                selected_crop=selected_crop,
                language=language,
                status="uncertain"
            ), ModelInfo(provider="System Validation", model_name="pil-validator", prompt_version="crop-disease-v2")

    # 3. Build Streamlined Prompt
    prompt = create_open_set_crop_disease_prompt(
        selected_crop=selected_crop,
        selected_plant_part=selected_plant_part,
        user_symptoms=user_symptoms,
        user_notes=user_notes,
        location=location,
        growth_stage=growth_stage,
        language=language
    )

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured.")
        raise ValueError("Gemini API key is not configured on the server.")

    # 4. Execute Gemini Vision
    preferred_model = getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash")
    fallback_models = [preferred_model, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
    seen_models = set()
    model_list = [m for m in fallback_models if not (m in seen_models or seen_models.add(m))]

    client = genai.Client(api_key=api_key)
    contents = [
        types.Part.from_bytes(data=img_b, mime_type="image/jpeg")
        for img_b in image_bytes_list
    ]
    contents.append(prompt)

    response = None
    successful_model = preferred_model
    last_exc = None

    for m in model_list:
        try:
            logger.info("[DISEASE] Calling Gemini model: %s", m)
            response = client.models.generate_content(
                model=m,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=getattr(settings, "GEMINI_TEMPERATURE", 0.1),
                )
            )
            if response and response.text:
                successful_model = m
                break
        except Exception as exc:
            logger.warning("[DISEASE] Gemini model %s failed: %s", m, exc)
            last_exc = exc
            continue

    if not response or not response.text:
        raise ValueError(f"Gemini API returned no response: {last_exc}")

    resp_text = response.text.strip()
    if resp_text.startswith("```json"):
        resp_text = resp_text[7:]
    if resp_text.startswith("```"):
        resp_text = resp_text[3:]
    if resp_text.endswith("```"):
        resp_text = resp_text[:-3]
    resp_text = resp_text.strip()

    try:
        raw_json = json.loads(resp_text)
    except json.JSONDecodeError as json_err:
        logger.error("[DISEASE] JSON decode error: %s. Raw text was: %s", json_err, resp_text[:200])
        raise ValueError(f"Could not parse Gemini response as JSON: {json_err}")

    normalized_result = validate_and_normalize_open_set_response(
        raw_data=raw_json,
        method2_features=method2_features,
        selected_crop=selected_crop,
        language=language
    )
    model_info = ModelInfo(
        provider="Google Gemini",
        model_name=successful_model,
        prompt_version="crop-disease-v2"
    )
    logger.info("[DISEASE] Analysis complete (model=%s)", successful_model)
    return normalized_result, model_info
