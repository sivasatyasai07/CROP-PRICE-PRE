import io
import os
import time
import json
import uuid
import hashlib
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from PIL import Image

from app.config import settings
from app.schemas.disease import (
    DiseaseAnalysisResult,
    ModelInfo,
    CropInfo,
    DiseaseInfo,
    PlantPartInfo,
    HealthAssessment,
    PrimaryDiagnosis,
    AlternativeDiagnosis,
    BestCrop,
    CropCandidate,
    CropRecognition,
    CropComparison,
    AmbiguityInfo,
    FeatureAnalysis,
    LeafMarginAnalysis,
    NextImageRequest,
    ChemicalControlGuidance,
    ValidationWarning,
    PlantNetSpeciesCandidate,
    ImageQualityAssessment
)

logger = logging.getLogger(__name__)

# Botanical scientific name to common Indian agricultural crop mapping
BOTANICAL_SPECIES_TO_CROP: Dict[str, Dict[str, str]] = {
    "solanum lycopersicum": {"crop": "Tomato", "category": "vegetable"},
    "lycopersicon esculentum": {"crop": "Tomato", "category": "vegetable"},
    "allium cepa": {"crop": "Onion", "category": "vegetable"},
    "solanum tuberosum": {"crop": "Potato", "category": "tuber"},
    "citrus limon": {"crop": "Lemon", "category": "fruit"},
    "citrus aurantiifolia": {"crop": "Lemon", "category": "fruit"},
    "citrus": {"crop": "Lemon", "category": "fruit"},
    "solanum melongena": {"crop": "Brinjal", "category": "vegetable"},
    "brassica oleracea": {"crop": "Cabbage", "category": "vegetable"},
    "brassica oleracea var. capitata": {"crop": "Cabbage", "category": "vegetable"},
    "brassica oleracea var. botrytis": {"crop": "Cauliflower", "category": "vegetable"},
    "capsicum annuum": {"crop": "Green Chilli", "category": "spice"},
    "capsicum frutescens": {"crop": "Green Chilli", "category": "spice"},
    "capsicum": {"crop": "Green Chilli", "category": "spice"},
    "cyamopsis tetragonoloba": {"crop": "Cluster Beans", "category": "pulse"},
    "luffa acutangula": {"crop": "Ridgeguard", "category": "vegetable"},
    "luffa aegyptiaca": {"crop": "Ridgeguard", "category": "vegetable"},
    "oryza sativa": {"crop": "Paddy", "category": "cereal"},
    "zea mays": {"crop": "Maize", "category": "cereal"},
    "sorghum bicolor": {"crop": "Jowar", "category": "millet"},
    "arachis hypogaea": {"crop": "Groundnut", "category": "oilseed"},
    "ricinus communis": {"crop": "Castor Seed", "category": "oilseed"},
    "helianthus annuus": {"crop": "Sunflower", "category": "oilseed"},
    "cicer arietinum": {"crop": "Bengal Gram", "category": "pulse"},
    "cajanus cajan": {"crop": "Red Gram", "category": "pulse"},
    "vigna mungo": {"crop": "Black Gram", "category": "pulse"},
    "trachyspermum ammi": {"crop": "Ajwan", "category": "spice"},
    "curcuma longa": {"crop": "Turmeric", "category": "spice"},
    "zingiber officinale": {"crop": "Ginger", "category": "spice"},
    "musa acuminata": {"crop": "Banana", "category": "fruit"},
    "mangifera indica": {"crop": "Mango", "category": "fruit"},
    "carica papaya": {"crop": "Papaya", "category": "fruit"},
    "gossypium hirsutum": {"crop": "Cotton", "category": "fiber"},
    "saccharum officinarum": {"crop": "Sugarcane", "category": "plantation"},
}


def validate_image(data: bytes, content_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validates uploaded image binary, MIME type, file size, and decoding integrity.
    """
    if not data or len(data) == 0:
        return False, "Please upload an image."

    max_mb = getattr(settings, "PLANTNET_MAX_IMAGE_SIZE_MB", 10)
    if len(data) > max_mb * 1024 * 1024:
        return False, f"Image size must not exceed {max_mb} MB."

    allowed_types = [t.strip().lower() for t in getattr(settings, "DISEASE_ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/webp").split(",")]
    if content_type:
        clean_type = content_type.strip().lower()
        if clean_type not in allowed_types and clean_type not in ("image/jpg", "image/jpeg", "image/png", "image/webp"):
            return False, "Only JPG, PNG, and WEBP images are supported."

    try:
        pil_img = Image.open(io.BytesIO(data))
        pil_img.verify()
    except Exception:
        return False, "The uploaded file is corrupted or cannot be opened."

    return True, None


def map_plantnet_organ(plant_part: Optional[str]) -> str:
    """
    Maps plant part to PlantNet organ taxonomy ('leaf', 'flower', 'fruit', 'bark', 'auto').
    """
    if not plant_part:
        return "auto"
    p_low = plant_part.strip().lower()
    if "leaf" in p_low or "foliage" in p_low:
        return "leaf"
    if "flower" in p_low or "bloom" in p_low:
        return "flower"
    if "fruit" in p_low or "pod" in p_low or "grain" in p_low or "berry" in p_low:
        return "fruit"
    if "stem" in p_low or "bark" in p_low or "trunk" in p_low or "branch" in p_low:
        return "bark"
    return "auto"


def map_plantnet_species(species_dict: Dict[str, Any]) -> Tuple[str, str, str, str]:
    """
    Maps species dictionary from PlantNet to (canonical_crop_name, scientific_name, category, crop_status).
    """
    sci_name_full = species_dict.get("scientificName", "")
    sci_name_no_author = species_dict.get("scientificNameWithoutAuthor", sci_name_full).strip()
    sci_lower = sci_name_no_author.lower()

    common_names = species_dict.get("commonNames", [])
    common_en = common_names[0] if common_names else ""

    # 1. Direct scientific match in agricultural mapping
    if sci_lower in BOTANICAL_SPECIES_TO_CROP:
        info = BOTANICAL_SPECIES_TO_CROP[sci_lower]
        return info["crop"], sci_name_full, info["category"], "recognized"

    # 2. Genus level lookup
    genus_dict = species_dict.get("genus", {})
    genus_name = genus_dict.get("scientificNameWithoutAuthor", "").lower()
    if genus_name in BOTANICAL_SPECIES_TO_CROP:
        info = BOTANICAL_SPECIES_TO_CROP[genus_name]
        return info["crop"], sci_name_full, info["category"], "recognized"

    # 3. Fallback to common name or scientific name
    display_name = common_en if common_en else (sci_name_no_author if sci_name_no_author else "Unknown species")
    category = "cultivated_plant"
    family = species_dict.get("family", {}).get("scientificNameWithoutAuthor", "").lower()
    if "solanaceae" in family:
        category = "vegetable"
    elif "poaceae" in family:
        category = "cereal"
    elif "fabaceae" in family:
        category = "pulse"
    elif "brassicaceae" in family:
        category = "vegetable"
    elif "rutaceae" in family:
        category = "fruit"

    return display_name, sci_name_full, category, "recognized_outside_configured_vocabulary"


def classify_plantnet_error(status_code: int, exc: Optional[Exception] = None) -> Tuple[str, str]:
    """
    Classifies HTTP errors and exceptions into sanitized, safe diagnostic categories.
    """
    if status_code in (401, 403):
        return "plantnet_authentication_error", "PlantNet API authentication failed. Check API key configuration."
    if status_code == 404:
        return "plantnet_invalid_response", "The configured PlantNet project or endpoint was not found."
    if status_code == 429:
        return "plantnet_rate_limit_error", "PlantNet API rate limit exceeded. Please wait a moment."
    if status_code in (408, 504) or isinstance(exc, requests.Timeout):
        return "plantnet_timeout", "PlantNet identification service timed out. Please try again."
    if status_code >= 500:
        return "plantnet_unavailable", "PlantNet identification service is temporarily unavailable."
    return "service_error", "An error occurred while communicating with PlantNet service."


def validate_plantnet_response(json_data: Any, status_code: int) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Validates PlantNet API JSON response structure.
    """
    if status_code != 200:
        err_cat, err_msg = classify_plantnet_error(status_code)
        return False, err_cat, []

    if not isinstance(json_data, dict):
        return False, "plantnet_invalid_response", []

    results = json_data.get("results", [])
    if not isinstance(results, list):
        return False, "plantnet_invalid_response", []

    if len(results) == 0:
        return True, "insufficient_evidence", []

    return True, "success", results


def normalize_plantnet_result(
    raw_json: Dict[str, Any],
    selected_crop: Optional[str] = None,
    plant_part: Optional[str] = None,
    symptoms: Optional[str] = None,
    notes: Optional[str] = None,
    language: str = "en"
) -> DiseaseAnalysisResult:
    """
    Converts raw PlantNet JSON into the standardized CropMandi AI response schema.
    """
    results = raw_json.get("results", [])
    if not results:
        return DiseaseAnalysisResult(
            analysis_status="insufficient_evidence",
            provider="PlantNet",
            selected_crop=selected_crop,
            detected_crop=None,
            detected_scientific_name=None,
            crop_category=None,
            plantnet_score=None,
            identification_status="unavailable",
            plantnet_results=[],
            crop_match_status="uncertain" if selected_crop else "not_provided",
            disease_status="not_available",
            symptoms=[symptoms] if symptoms else [],
            warnings=[ValidationWarning(field="plantnet_results", issue="PlantNet could not identify this image confidently.", action="upload_clearer_image")],
            limitations=["Image lacked sufficient botanical identifying features."],
            disclaimer="PlantNet identification is an AI-assisted preliminary species identification and is not a guaranteed disease diagnosis."
        )

    # Parse ranked candidate species
    species_candidates: List[PlantNetSpeciesCandidate] = []
    ranked_crop_candidates: List[CropCandidate] = []

    for rank_idx, res in enumerate(results[:5]):
        score_val = float(res.get("score", 0.0))
        sp_data = res.get("species", {})
        sci_name = sp_data.get("scientificName", "Unknown species")
        com_names = sp_data.get("commonNames", [])
        fam_name = sp_data.get("family", {}).get("scientificNameWithoutAuthor")

        candidate_obj = PlantNetSpeciesCandidate(
            scientific_name=sci_name,
            common_names=com_names,
            family=fam_name,
            score=round(score_val, 4),
            rank=rank_idx + 1
        )
        species_candidates.append(candidate_obj)

        crop_nm, _, cat_nm, status_nm = map_plantnet_species(sp_data)
        ranked_crop_candidates.append(
            CropCandidate(
                name=crop_nm,
                category=cat_nm,
                crop_status=status_nm,
                gemini_original_probability=round(score_val, 4),
                combined_probability=round(score_val, 4),
                supporting_evidence=[f"Botanical family: {fam_name}"] if fam_name else []
            )
        )

    top_res = results[0]
    top_score = float(top_res.get("score", 0.0))
    top_sp = top_res.get("species", {})
    detected_crop, det_sci_name, det_category, crop_status = map_plantnet_species(top_sp)

    # Determine identification status from score
    if top_score >= 0.60:
        ident_status = "identified"
    elif top_score >= 0.25:
        ident_status = "probable"
    else:
        ident_status = "low_confidence"

    # Crop match comparison
    match_status = "not_provided"
    match_reason = ""
    warnings_list: List[ValidationWarning] = []

    if selected_crop:
        from app.utils.market_normalization import normalize_commodity_name
        norm_selected = normalize_commodity_name(selected_crop).lower()
        norm_detected = detected_crop.lower()

        if norm_selected in norm_detected or norm_detected in norm_selected:
            match_status = "match"
            match_reason = f"Identified plant matches selected crop '{selected_crop}'."
        else:
            match_status = "mismatch"
            match_reason = f"The selected crop '{selected_crop}' may differ from the plant identified in the image ('{detected_crop}')."
            warnings_list.append(
                ValidationWarning(
                    field="crop_match_status",
                    issue=match_reason,
                    action="verify_selected_crop"
                )
            )

    if top_score < 0.25:
        warnings_list.append(
            ValidationWarning(
                field="plantnet_score",
                issue="Low identification score. Please upload a clearer image of foliage, flower, or fruit.",
                action="upload_clearer_image"
            )
        )

    best_crop_obj = BestCrop(
        name=detected_crop,
        category=det_category,
        crop_status=crop_status,
        gemini_original_probability=round(top_score, 4),
        combined_probability=round(top_score, 4),
        final_selection_source="PlantNet identification score"
    )

    crop_rec_obj = CropRecognition(
        identification_status=ident_status,
        best_crop=best_crop_obj,
        ranked_candidates=ranked_crop_candidates,
        feature_analysis=FeatureAnalysis(
            leaf_margin=LeafMarginAnalysis(type="analyzed", reliability="usable", evidence=f"Identified species: {det_sci_name}")
        ),
        ambiguity=AmbiguityInfo(status="low" if top_score >= 0.50 else "moderate", message=match_reason)
    )

    crop_comp_obj = CropComparison(
        user_selected_crop=selected_crop,
        detected_best_crop=detected_crop,
        match_status=match_status,
        reason=match_reason
    )

    health_assess_obj = HealthAssessment(
        status="requires_second_stage",
        confidence=None,
        visible_evidence=[symptoms] if symptoms else []
    )

    primary_diag_obj = PrimaryDiagnosis(
        name="Plant Species Identified (Disease Diagnosis Requires Expert / Pathology Stage)",
        category="requires_second_stage",
        confidence=None,
        evidence=[f"Species: {det_sci_name} ({detected_crop})", f"Identification Score: {round(top_score * 100, 1)}%"]
    )

    image_quality_obj = ImageQualityAssessment(
        status="acceptable" if top_score >= 0.30 else "poor",
        score=round(top_score, 2),
        issues=[w.issue for w in warnings_list]
    )

    return DiseaseAnalysisResult(
        analysis_status="success",
        provider="PlantNet",
        selected_crop=selected_crop,
        detected_crop=detected_crop,
        detected_scientific_name=det_sci_name,
        crop_category=det_category,
        plantnet_score=round(top_score, 4),
        identification_status=ident_status,
        plantnet_results=species_candidates,
        crop_match_status=match_status,
        disease_status="requires_second_stage",
        crop=CropInfo(name=detected_crop, confidence=round(top_score, 4)),
        plant_part=plant_part or "Leaf",
        health_status="requires_second_stage",
        disease=DiseaseInfo(name="Disease diagnosis requires expert confirmation", confidence=None),
        symptoms=[symptoms] if symptoms else [],
        possible_causes=[notes] if notes else [],
        management=["Consult local agricultural extension officer or Krishi Vigyan Kendra (KVK) for certified crop disease diagnosis."],
        prevention=["Use certified disease-free seeds and maintain balanced irrigation."],
        risk_level="low",
        limitations=["PlantNet identifies plant species from image visual features. Disease diagnosis requires separate pathology validation."],
        disclaimer="Plant identified by PlantNet. Disease diagnosis requires a separate disease-analysis model or expert confirmation.",
        plant_detected=True,
        image_quality=image_quality_obj,
        crop_recognition=crop_rec_obj,
        crop_comparison=crop_comp_obj,
        health_assessment=health_assess_obj,
        primary_diagnosis=primary_diag_obj,
        chemical_control_guidance=ChemicalControlGuidance(
            provided=False,
            message="Consult a local agricultural extension officer or Krishi Vigyan Kendra (KVK) for approved regional disease control products."
        ),
        language=language,
        validation_warnings=warnings_list
    )


def identify_plant_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    filename: str = "leaf_image.jpg",
    selected_crop: Optional[str] = None,
    plant_part: Optional[str] = None,
    symptoms: Optional[str] = None,
    notes: Optional[str] = None,
    location: Optional[str] = None,
    growth_stage: Optional[str] = None,
    language: str = "en"
) -> Tuple[DiseaseAnalysisResult, ModelInfo]:
    """
    Main entry point: validates image, constructs multipart/form-data POST to PlantNet API,
    and returns normalized disease analysis result.
    """
    valid, err_msg = validate_image(image_bytes, mime_type)
    if not valid:
        raise ValueError(err_msg or "Invalid image file")

    plantnet_key = (settings.PLANTNET_API_KEY or "").strip()
    gemini_key = (settings.GEMINI_API_KEY or "").strip()

    plantnet_result: Optional[DiseaseAnalysisResult] = None
    plantnet_model: Optional[ModelInfo] = None
    plantnet_error: Optional[str] = None
    plantnet_error_category: Optional[str] = None

    gemini_result: Optional[DiseaseAnalysisResult] = None
    gemini_model: Optional[ModelInfo] = None
    gemini_error: Optional[str] = None

    now_iso = datetime.now(timezone.utc).isoformat()

    # -------------------------------------------------------------
    # 1. PLANTNET BOTANICAL IDENTIFICATION (if key configured)
    # -------------------------------------------------------------
    if plantnet_key:
        base_url = settings.PLANTNET_BASE_URL.rstrip("/")
        project = settings.PLANTNET_PROJECT or "all"
        endpoint = f"{base_url}/{project}"
        timeout_sec = float(getattr(settings, "PLANTNET_TIMEOUT_SECONDS", 120))
        max_retries = int(getattr(settings, "PLANTNET_MAX_RETRIES", 2))

        organ = map_plantnet_organ(plant_part)
        params = {"api-key": plantnet_key}
        files = [("images", (filename, image_bytes, mime_type))]
        data = {"organs": [organ]}

        logger.info("[PLANTNET] Sending multipart POST request to %s (project=%s, organ=%s, size=%d bytes)",
                    f"{base_url}/{project}", project, organ, len(image_bytes))

        response_json = None
        last_status = 0
        last_error: Optional[Exception] = None

        for attempt in range(1, max_retries + 2):
            try:
                resp = requests.post(
                    endpoint,
                    params=params,
                    files=files,
                    data=data,
                    timeout=timeout_sec,
                    headers={"User-Agent": "CropMandiAI/2.0 (PlantNetClient)"}
                )
                last_status = resp.status_code

                if resp.status_code == 200:
                    response_json = resp.json()
                    break

                if resp.status_code == 429:
                    logger.warning("[PLANTNET] Rate limit 429 on attempt %d", attempt)
                    time.sleep(1.5 * attempt)
                    continue

                if resp.status_code in (401, 403):
                    logger.error("[PLANTNET] Authentication failure (HTTP %d)", resp.status_code)
                    break

                if resp.status_code >= 500:
                    logger.warning("[PLANTNET] Server error HTTP %d on attempt %d", resp.status_code, attempt)
                    time.sleep(1.0 * attempt)
                    continue

                logger.warning("[PLANTNET] API returned HTTP %d", resp.status_code)
                break

            except requests.Timeout as exc:
                logger.warning("[PLANTNET] Timeout on attempt %d: %s", attempt, exc)
                last_error = exc
                time.sleep(1.0)
            except requests.RequestException as exc:
                logger.warning("[PLANTNET] Request exception on attempt %d: %s", attempt, exc)
                last_error = exc
                time.sleep(1.0)

        plantnet_model = ModelInfo(
            provider="PlantNet",
            model_name="PlantNet-v2",
            project=project,
            request_timestamp=now_iso
        )

        if last_status == 200 and response_json is not None:
            plantnet_result = normalize_plantnet_result(
                raw_json=response_json,
                selected_crop=selected_crop,
                plant_part=plant_part,
                symptoms=symptoms,
                notes=notes,
                language=language
            )
        else:
            err_cat, err_desc = classify_plantnet_error(last_status, last_error)
            plantnet_error_category = err_cat
            plantnet_error = err_desc
            logger.warning("[PLANTNET] Identification did not succeed: %s (%s)", err_cat, err_desc)

    # -------------------------------------------------------------
    # 2. GEMINI AI VISION PATHOLOGY & DISEASE DIAGNOSIS
    # -------------------------------------------------------------
    if gemini_key:
        try:
            from app.services.gemini_crop_disease_service import analyze_crop_image
            effective_crop = (plantnet_result.detected_crop if plantnet_result else None) or selected_crop
            logger.info("[GEMINI] Running Disease & Pathology Analysis (effective_crop=%s)", effective_crop)
            gemini_result, gemini_model = analyze_crop_image(
                image_bytes_list=[image_bytes],
                selected_crop=effective_crop,
                selected_plant_part=plant_part,
                user_symptoms=symptoms,
                user_notes=notes,
                location=location,
                growth_stage=growth_stage,
                language=language or "en"
            )
            logger.info("[GEMINI] Disease Analysis successful: %s (%s)",
                        gemini_result.disease.name if hasattr(gemini_result.disease, 'name') else gemini_result.disease,
                        gemini_result.health_status)

        except Exception as exc:
            gemini_error = str(exc)
            logger.warning("[GEMINI] Disease diagnosis failed: %s (will use PlantNet fallback if available)", exc)

    # -------------------------------------------------------------
    # 3. RECONCILIATION & FALLBACK RESOLUTION
    # -------------------------------------------------------------

    # Case A: Both PlantNet & Gemini Succeeded -> Combine botanical species + disease pathology
    if plantnet_result and gemini_result:
        final_result = plantnet_result
        final_result.disease = gemini_result.disease
        final_result.health_status = gemini_result.health_status
        final_result.health_assessment = gemini_result.health_assessment
        final_result.primary_diagnosis = gemini_result.primary_diagnosis
        final_result.alternative_diagnoses = gemini_result.alternative_diagnoses
        final_result.symptoms = gemini_result.symptoms or final_result.symptoms
        final_result.possible_causes = gemini_result.possible_causes or final_result.possible_causes
        final_result.management = gemini_result.management or final_result.management
        final_result.immediate_actions = gemini_result.immediate_actions or final_result.immediate_actions
        final_result.prevention = gemini_result.prevention or final_result.prevention
        final_result.chemical_control_guidance = gemini_result.chemical_control_guidance
        final_result.risk_level = gemini_result.risk_level
        final_result.disease_status = "diagnosed" if gemini_result.health_status != "uncertain" else "unclear"
        final_result.provider = "PlantNet + Gemini AI"

        final_model = ModelInfo(
            provider="PlantNet + Gemini AI",
            model_name=f"PlantNet-v2 + {getattr(gemini_model, 'model_name', 'gemini-3.6-flash')}",
            project=settings.PLANTNET_PROJECT or "all",
            request_timestamp=now_iso
        )
        return final_result, final_model

    # Case B: Gemini Succeeded (PlantNet was empty or failed) -> Use Gemini Vision
    if gemini_result:
        gemini_result.provider = "Gemini AI Vision"
        if plantnet_error:
            if gemini_result.validation_warnings is None:
                gemini_result.validation_warnings = []
            gemini_result.validation_warnings.append(ValidationWarning(
                field="plantnet_fallback",
                issue=f"PlantNet botanical check unavailable ({plantnet_error}); complete diagnosis provided by Gemini Vision.",
                action="none"
            ))
        return gemini_result, (gemini_model or ModelInfo(provider="Google Gemini", model_name="gemini-3.6-flash", request_timestamp=now_iso))

    # Case C: Gemini Failed -> Fallback to PlantNet botanical identification!
    if plantnet_result:
        logger.info("[FALLBACK] Gemini Vision failed (%s); returning PlantNet botanical identification fallback", gemini_error)
        plantnet_result.provider = "PlantNet (Botanical Fallback)"
        if plantnet_result.validation_warnings is None:
            plantnet_result.validation_warnings = []
        plantnet_result.validation_warnings.append(ValidationWarning(
            field="gemini_ai",
            issue="Gemini pathology AI was temporarily unavailable; plant species accurately identified via PlantNet.",
            action="consult_kvk"
        ))
        plantnet_result.disclaimer = "Plant species identified via PlantNet. Since AI pathology service was unavailable, please consult your local Krishi Vigyan Kendra (KVK) or agricultural extension officer for disease confirmation."
        return plantnet_result, (plantnet_model or ModelInfo(provider="PlantNet", model_name="PlantNet-v2", request_timestamp=now_iso))

    # Case D: Both Failed or Unconfigured
    err_msg = "Both Gemini Vision and PlantNet identification services are temporarily unavailable."
    if gemini_error:
        err_msg += f" Gemini error: {gemini_error}."
    if plantnet_error:
        err_msg += f" PlantNet error: {plantnet_error}."

    fallback_error_result = DiseaseAnalysisResult(
        analysis_status=plantnet_error_category or "service_error",
        provider="PlantNet / Gemini",
        selected_crop=selected_crop,
        identification_status="unavailable",
        disease_status="not_available",
        validation_warnings=[ValidationWarning(field="service_availability", issue=err_msg, action="retry_later")],
        limitations=["AI identification services temporarily unavailable."],
        disclaimer="Service is temporarily unavailable. Please verify API configuration in backend/.env and try again."
    )
    fallback_model = ModelInfo(provider="System", model_name="fallback", request_timestamp=now_iso)
    return fallback_error_result, fallback_model


def test_plantnet_connection() -> Dict[str, Any]:
    """
    Safe diagnostic health-check without exposing API key.
    """
    api_key_present = bool(settings.PLANTNET_API_KEY and len(settings.PLANTNET_API_KEY.strip()) > 0)
    base_url_ok = bool(settings.PLANTNET_BASE_URL)
    now_iso = datetime.now(timezone.utc).isoformat()

    status_str = "ready" if api_key_present and base_url_ok else "configuration_error"
    msg = "PlantNet service is configured and ready." if status_str == "ready" else "PlantNet backend credentials are not configured."

    return {
        "provider": "PlantNet",
        "configured": api_key_present,
        "base_url_configured": base_url_ok,
        "api_key_present": api_key_present,
        "api_key_valid": "not_checked" if not api_key_present else "valid",
        "project": settings.PLANTNET_PROJECT,
        "status": status_str,
        "checked_at": now_iso,
        "message": msg
    }
