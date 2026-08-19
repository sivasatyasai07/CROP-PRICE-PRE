import os
import uuid
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status, Header
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
import io
import logging

from app.config import settings
from app.core.dependencies import get_current_user
from app.core.security import decode_access_token
from app.services.user_store import find_user_by_id
from app.schemas.disease import (
    DiseaseAnalysisResponse,
    DiseaseHistoryListResponse,
    DiseaseHistoryItem,
    DiseaseAnalysisResult,
    ImageMetadata,
    ModelInfo
)
from app.services.plantnet_disease_service import (
    identify_plant_image,
    test_plantnet_connection,
    validate_image
)
from app.services.disease_history_store import (
    append_analysis,
    read_user_history,
    get_analysis_by_id,
    delete_analysis,
    save_disease_image,
    get_disease_image_path,
    check_rate_limit
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/disease", tags=["Crop Disease Detection & Identification"])


def get_optional_auth_user(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
) -> Optional[Dict[str, Any]]:
    """
    Optionally extracts and verifies JWT token from Authorization header or query param.
    Returns user dict if valid; returns None if unauthenticated. Never raises 401.
    """
    token_str = None
    if authorization and authorization.startswith("Bearer "):
        token_str = authorization.replace("Bearer ", "").strip()
    elif token and isinstance(token, str):
        token_str = token.strip()

    if not token_str:
        return None

    try:
        payload = decode_access_token(token_str)
        if not payload or "sub" not in payload:
            return None
        return find_user_by_id(payload["sub"])
    except Exception as exc:
        logger.debug("Optional user auth decode failed: %s", exc)
        return None


def get_auth_user(
    user: Optional[Dict[str, Any]] = Depends(get_optional_auth_user)
) -> Dict[str, Any]:
    """
    Strictly verifies JWT token and retrieves user payload.
    Raises HTTP 401 if unauthenticated.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access disease history."
        )
    return user


@router.get("/health")
def get_disease_service_health():
    """
    Diagnostic health-check reporting PlantNet configuration status, project, and readiness
    without exposing secrets or full URL with keys.
    """
    return test_plantnet_connection()


@router.post("/analyze", response_model=DiseaseAnalysisResponse)
async def analyze_crop_disease(
    file: Optional[UploadFile] = File(None, description="Primary crop leaf or plant image"),
    files: Optional[List[UploadFile]] = File(None, description="Optional multi-image uploads"),
    crop: Optional[str] = Form(None, description="Optional selected crop"),
    selected_crop: Optional[str] = Form(None, description="Alias for crop selection"),
    plant_part: Optional[str] = Form(None, description="Optional plant part e.g. Leaf, Stem, Fruit"),
    symptoms: Optional[str] = Form(None, description="Optional symptoms observed by farmer"),
    notes: Optional[str] = Form(None, description="Optional field notes"),
    location: Optional[str] = Form(None, description="Optional farm location"),
    growth_stage: Optional[str] = Form(None, description="Optional crop growth stage"),
    language: Optional[str] = Form("en", description="Preferred output language: en, te, hi, ta, ml"),
    user: Optional[Dict[str, Any]] = Depends(get_optional_auth_user)
):
    """
    Analyzes uploaded crop images with PlantNet v2 API.
    - Accurately identifies crop/plant species using botanical vision models.
    - Generates PlantNet identification score and ranked candidate alternatives.
    - Validates image integrity, MIME format, and size.
    - If authenticated, saves analysis and image to user's private JSON history.
    """
    user_id = user["id"] if user else None
    email = user.get("email", "") if user else ""

    logger.info("[DISEASE] Request received (user_id=%s, provider=PlantNet)", user_id or "anonymous")

    # 1. Collect all genuine uploaded files
    uploaded_files: List[UploadFile] = []
    
    if files:
        for item in files:
            if getattr(item, "filename", None) and item.filename.strip():
                uploaded_files.append(item)

    if file and getattr(file, "filename", None) and file.filename.strip():
        if file not in uploaded_files:
            uploaded_files.insert(0, file)

    if not uploaded_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload an image of the crop foliage or affected plant."
        )

    # 2. Read primary image
    primary_file = uploaded_files[0]
    content_type = (primary_file.content_type or "image/jpeg").lower()
    primary_filename = primary_file.filename or "leaf_image.jpg"
    primary_bytes = await primary_file.read()

    # 3. Validate image
    valid, err_msg = validate_image(primary_bytes, content_type)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg or "Invalid image file."
        )

    # 4. Rate limiting check
    rate_limit_key = user_id or "anonymous_guest"
    allowed, rate_err = check_rate_limit(rate_limit_key, "")
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=rate_err or "Analysis rate limit exceeded. Please wait a moment."
        )

    # 5. Execute PlantNet identification
    effective_crop = crop or selected_crop
    analysis_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    sha256_hash = hashlib.sha256(primary_bytes).hexdigest()
    timeout_seconds = float(getattr(settings, "PLANTNET_TIMEOUT_SECONDS", 60))

    try:
        analysis_result, model_info = await asyncio.wait_for(
            asyncio.to_thread(
                identify_plant_image,
                image_bytes=primary_bytes,
                mime_type=content_type,
                filename=primary_filename,
                selected_crop=effective_crop,
                plant_part=plant_part,
                symptoms=symptoms,
                notes=notes,
                location=location,
                growth_stage=growth_stage,
                language=language or "en"
            ),
            timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        logger.error("[DISEASE] PlantNet analysis timed out after %s seconds", timeout_seconds)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"PlantNet identification timed out after {int(timeout_seconds)} seconds. Please try again."
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("[DISEASE] PlantNet request failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PlantNet identification error: {str(exc)}"
        )

    # 6. Save history ONLY if user is authenticated
    if user_id:
        logger.info("[DISEASE] Saving history for authenticated user (user_id=%s)", user_id)
        ext = primary_filename.split(".")[-1] if ("." in primary_filename) else "jpg"
        storage_ref = save_disease_image(user_id, analysis_id, primary_bytes, ext)

        image_meta = {
            "original_filename": primary_filename,
            "mime_type": content_type,
            "size_bytes": len(primary_bytes),
            "sha256": sha256_hash,
            "storage_reference": storage_ref
        }

        result_dict = analysis_result.model_dump() if hasattr(analysis_result, "model_dump") else analysis_result.dict()
        model_dict = model_info.model_dump() if hasattr(model_info, "model_dump") else model_info.dict()

        history_record = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "created_at": now_iso,
            "provider": "PlantNet",
            "selected_crop": effective_crop,
            "detected_crop": analysis_result.detected_crop or "Unidentified Plant",
            "detected_scientific_name": analysis_result.detected_scientific_name,
            "detected_crop_category": analysis_result.crop_category or "vegetable",
            "plantnet_score": analysis_result.plantnet_score,
            "crop_status": "recognized" if analysis_result.detected_crop else "unidentified",
            "identification_status": analysis_result.identification_status,
            "crop_match_status": analysis_result.crop_match_status,
            "plantnet_results": [
                r.model_dump() if hasattr(r, "model_dump") else r.dict()
                for r in analysis_result.plantnet_results
            ],
            "plant_part": analysis_result.plant_part,
            "health_status": analysis_result.health_status,
            "disease_status": analysis_result.disease_status,
            "original_confidence": {
                "plantnet_score": analysis_result.plantnet_score,
            },
            "primary_diagnosis": {
                "name": analysis_result.primary_diagnosis.name if analysis_result.primary_diagnosis else "Plant Species Identified",
                "category": analysis_result.primary_diagnosis.category if analysis_result.primary_diagnosis else "requires_second_stage",
                "confidence": analysis_result.plantnet_score,
                "evidence": analysis_result.primary_diagnosis.evidence if analysis_result.primary_diagnosis else []
            },
            "symptoms": analysis_result.symptoms,
            "possible_causes": analysis_result.possible_causes,
            "immediate_actions": analysis_result.immediate_actions,
            "prevention": analysis_result.prevention,
            "image_quality": {
                "status": analysis_result.image_quality.status if analysis_result.image_quality else "acceptable",
                "score": analysis_result.image_quality.score if analysis_result.image_quality else analysis_result.plantnet_score,
                "issues": analysis_result.image_quality.issues if analysis_result.image_quality else []
            },
            "user_symptoms": symptoms,
            "user_notes": notes,
            "image": image_meta,
            "result": result_dict,
            "model": model_dict,
            "language": language or "en",
            "warnings": [w.issue if hasattr(w, "issue") else str(w) for w in analysis_result.validation_warnings],
            "disclaimer": analysis_result.disclaimer
        }

        append_analysis(user_id, email, history_record)
    else:
        logger.info("[DISEASE] Guest user analysis completed (history not saved)")

    logger.info("[DISEASE] Completed")

    return DiseaseAnalysisResponse(
        message="Crop image identified successfully via PlantNet.",
        analysis_id=analysis_id,
        created_at=now_iso,
        provider="PlantNet",
        model=model_info,
        result=analysis_result,
        warnings=[w.issue if hasattr(w, "issue") else str(w) for w in analysis_result.validation_warnings],
        disclaimer=analysis_result.disclaimer
    )


@router.get("/history", response_model=DiseaseHistoryListResponse)
def get_user_disease_history(
    crop: Optional[str] = Query(None, description="Filter by crop name"),
    status: Optional[str] = Query(None, description="Filter by health status"),
    limit: int = Query(20, ge=1, le=100),
    user: Dict[str, Any] = Depends(get_auth_user)
):
    """
    Returns user-isolated crop disease and plant identification history list.
    """
    user_id = user["id"]
    history_data = read_user_history(user_id)
    analyses_raw = history_data.get("analyses", [])

    filtered_items: List[DiseaseHistoryItem] = []
    for item in analyses_raw:
        res = item.get("result", {})
        det_crop = item.get("detected_crop") or res.get("detected_crop") or res.get("crop_recognition", {}).get("crop_name") or item.get("crop") or "Unknown"
        h_status = item.get("health_status") or res.get("health_status") or "requires_second_stage"

        if crop and crop.lower() not in det_crop.lower():
            continue
        if status and status.lower() not in h_status.lower():
            continue

        p_diag = item.get("primary_diagnosis") or res.get("primary_diagnosis") or {
            "name": "Plant Species Identified",
            "category": h_status,
            "confidence": item.get("plantnet_score"),
            "evidence": []
        }

        conf_dict = item.get("original_confidence", {})
        if not conf_dict and "confidence" in p_diag:
            conf_dict = {
                "plantnet_score": item.get("plantnet_score") or p_diag.get("confidence")
            }

        filtered_items.append(DiseaseHistoryItem(
            analysis_id=item.get("analysis_id", ""),
            created_at=item.get("created_at", ""),
            provider=item.get("provider", "PlantNet"),
            selected_crop=item.get("selected_crop") or item.get("crop"),
            detected_crop=det_crop,
            detected_scientific_name=item.get("detected_scientific_name") or res.get("detected_scientific_name"),
            plantnet_score=item.get("plantnet_score") or res.get("plantnet_score"),
            crop_match_status=item.get("crop_match_status", "not_provided"),
            plantnet_results=item.get("plantnet_results", []),
            plant_part=item.get("plant_part", "Leaf"),
            health_status=h_status,
            disease_status=item.get("disease_status", "requires_second_stage"),
            original_confidence=conf_dict,
            primary_diagnosis=p_diag,
            symptoms=item.get("symptoms") or res.get("symptoms", []),
            possible_causes=item.get("possible_causes") or res.get("possible_causes", []),
            immediate_actions=item.get("immediate_actions") or res.get("immediate_actions", []),
            prevention=item.get("prevention") or res.get("prevention", []),
            image_quality=item.get("image_quality") or res.get("image_quality", {}),
            has_image=bool(item.get("image")),
            image_url=f"/api/v1/disease/image/{item.get('analysis_id')}",
            model=ModelInfo(**item.get("model", {})) if item.get("model") else None,
            language=item.get("language", "en"),
            warnings=item.get("warnings", []),
            disclaimer=item.get("disclaimer", "PlantNet identification is an AI-assisted preliminary species identification.")
        ))

    total_count = len(filtered_items)
    paginated = filtered_items[:limit]

    return DiseaseHistoryListResponse(
        analyses=paginated,
        total_count=total_count,
        user_id=user_id
    )


@router.get("/history/{analysis_id}")
def get_disease_analysis_detail(
    analysis_id: str,
    user: Dict[str, Any] = Depends(get_auth_user)
):
    """
    Retrieves full detail of a single disease analysis owned by user.
    """
    user_id = user["id"]
    analysis = get_analysis_by_id(user_id, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease analysis record not found or access denied."
        )
    return analysis


@router.delete("/history/{analysis_id}")
def delete_disease_history_record(
    analysis_id: str,
    user: Dict[str, Any] = Depends(get_auth_user)
):
    """
    Deletes an analysis record and its corresponding stored image.
    """
    user_id = user["id"]
    success = delete_analysis(user_id, analysis_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease analysis record not found."
        )
    return {
        "success": True,
        "message": "Analysis record and stored image deleted successfully."
    }


@router.get("/image/{analysis_id}")
def stream_disease_image(
    analysis_id: str,
    user: Dict[str, Any] = Depends(get_auth_user)
):
    """
    Streams the private stored disease image only to its owner.
    """
    user_id = user["id"]
    img_path = get_disease_image_path(user_id, analysis_id)
    if not img_path or not os.path.exists(img_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored image not found."
        )

    ext = img_path.split(".")[-1].lower()
    media_type = "image/jpeg"
    if ext == "png":
        media_type = "image/png"
    elif ext == "webp":
        media_type = "image/webp"

    return FileResponse(img_path, media_type=media_type)
