from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime

# Enums / Literal Types
AnalysisStatus = Literal[
    "success",
    "uncertain",
    "unclear_image",
    "crop_mismatch",
    "non_plant_image",
    "insufficient_evidence",
    "service_error",
    "plantnet_authentication_error",
    "plantnet_rate_limit_error",
    "plantnet_timeout",
    "plantnet_invalid_response",
    "plantnet_unavailable"
]

HealthStatus = Literal[
    "healthy",
    "diseased",
    "disease",
    "uncertain",
    "fungal_disease",
    "bacterial_disease",
    "viral_disease",
    "pest_damage",
    "nutrient_deficiency",
    "physical_damage",
    "abiotic_stress",
    "mixed_or_multiple",
    "unclear",
    "non_plant_image",
    "insufficient_evidence",
    "requires_second_stage",
    "not_started",
    "not_available"
]

IdentificationStatus = Literal[
    "identified",
    "probable",
    "low_confidence",
    "unidentified",
    "unavailable"
]

CropMatchStatus = Literal[
    "match",
    "mismatch",
    "uncertain",
    "not_provided",
    "not_specified"
]

CropCategory = Literal[
    "vegetable",
    "fruit",
    "cereal",
    "millet",
    "pulse",
    "oilseed",
    "spice",
    "plantation",
    "fiber",
    "tuber",
    "root",
    "leafy",
    "fodder",
    "cultivated_plant",
    "wild_plant",
    "ornamental",
    "unknown"
]


class PlantNetSpeciesCandidate(BaseModel):
    scientific_name: str = Field(description="Scientific botanical name e.g. Solanum lycopersicum L.")
    common_names: List[str] = Field(default_factory=list, description="Common names e.g. ['Tomato', 'Garden tomato']")
    family: Optional[str] = Field(default=None, description="Botanical family e.g. Solanaceae")
    score: float = Field(default=0.0, ge=0.0, description="PlantNet identification score")
    rank: int = Field(default=1, description="Rank in results list")


class ImageQualityAssessment(BaseModel):
    status: str = Field(default="acceptable", description="acceptable, partially_usable, poor, non_plant_image, insufficient_evidence")
    original_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)


class LeafMarginAnalysis(BaseModel):
    type: str = Field(default="unavailable", description="serrated, dentate, crenate, smooth/entire, lobed, undulate, irregular_damaged, unavailable")
    original_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence: str = Field(default="")
    reliability: str = Field(default="usable", description="usable, unreliable, unavailable")


class FeatureAnalysis(BaseModel):
    leaf_margin: LeafMarginAnalysis = Field(default_factory=LeafMarginAnalysis)
    leaf_shape: str = Field(default="")
    leaf_apex: str = Field(default="")
    leaf_base: str = Field(default="")
    leaf_venation: str = Field(default="")
    leaf_texture: str = Field(default="")
    leaf_arrangement: str = Field(default="")
    stem_features: str = Field(default="")
    fruit_features: str = Field(default="")
    flower_features: str = Field(default="")
    root_features: str = Field(default="")


class CropCandidate(BaseModel):
    name: str = Field(description="Crop name e.g. Tomato, Groundnut, Maize, Mango")
    category: str = Field(default="vegetable", description="vegetable, fruit, cereal, millet, pulse, oilseed, spice, plantation...")
    crop_status: str = Field(default="recognized", description="recognized or recognized_outside_configured_vocabulary")
    gemini_original_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    classifier_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    combined_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)


class BestCrop(BaseModel):
    name: str = Field(description="Selected highest-probability crop name")
    category: str = Field(default="vegetable")
    crop_status: str = Field(default="recognized", description="recognized or recognized_outside_configured_vocabulary")
    gemini_original_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    classifier_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    combined_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    final_selection_source: str = Field(default="plantnet_identification_score")


class AmbiguityInfo(BaseModel):
    status: str = Field(default="low", description="low, moderate, high")
    top_candidate_gap: Optional[float] = Field(default=None)
    message: str = Field(default="")


class CropRecognition(BaseModel):
    identification_status: IdentificationStatus = Field(default="probable")
    best_crop: BestCrop
    ranked_candidates: List[CropCandidate] = Field(default_factory=list)
    feature_analysis: FeatureAnalysis = Field(default_factory=FeatureAnalysis)
    ambiguity: AmbiguityInfo = Field(default_factory=AmbiguityInfo)

    @property
    def crop_name(self) -> str:
        return self.best_crop.name

    @property
    def confidence(self) -> Optional[float]:
        return self.best_crop.combined_probability or self.best_crop.gemini_original_probability


class CropComparison(BaseModel):
    user_selected_crop: Optional[str] = None
    detected_best_crop: str
    match_status: CropMatchStatus = Field(default="not_provided")
    reason: str = Field(default="")


class NextImageRequest(BaseModel):
    needed: bool = Field(default=False)
    suggested_images: List[str] = Field(default_factory=list)


class PlantPartInfo(BaseModel):
    name: str = Field(default="Leaf", description="Leaf, Stem, Fruit, Root, Flower, Whole plant, Multiple parts, Unknown")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class HealthAssessment(BaseModel):
    status: str = Field(default="requires_second_stage")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    visible_evidence: List[str] = Field(default_factory=list)


class PrimaryDiagnosis(BaseModel):
    name: str = Field(default="Plant Species Identified (Expert Diagnosis Pending)", description="Condition name")
    category: str = Field(default="requires_second_stage")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)


class AlternativeDiagnosis(BaseModel):
    name: str
    category: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reason: Optional[str] = None
    distinguishing_evidence: Optional[str] = None


class ChemicalControlGuidance(BaseModel):
    provided: bool = Field(default=False)
    message: str = Field(
        default="Consult a local agricultural extension officer or Krishi Vigyan Kendra (KVK) for approved regional products."
    )


class ValidationWarning(BaseModel):
    field: str
    issue: str
    action: str


class ModelInfo(BaseModel):
    provider: str = Field(default="PlantNet")
    model_name: str = Field(default="PlantNet-v2")
    project: str = Field(default="all")
    prompt_version: Optional[str] = Field(default=None)
    request_timestamp: Optional[str] = Field(default=None)


class CropInfo(BaseModel):
    name: str = Field(default="Unidentified Plant", description="Detected crop name e.g. Tomato, Groundnut")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class DiseaseInfo(BaseModel):
    name: str = Field(default="Expert diagnosis pending", description="Diagnosed disease")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class DiseaseAnalysisResult(BaseModel):
    analysis_status: str = Field(default="success", description="success | insufficient_evidence | non_plant_image | service_error")
    provider: str = Field(default="PlantNet")
    selected_crop: Optional[str] = None
    detected_crop: Optional[str] = None
    detected_scientific_name: Optional[str] = None
    crop_category: Optional[str] = None
    plantnet_score: Optional[float] = Field(default=None, description="PlantNet identification score")
    identification_status: str = Field(default="identified", description="identified | probable | low_confidence | unavailable")
    plantnet_results: List[PlantNetSpeciesCandidate] = Field(default_factory=list)
    crop_match_status: str = Field(default="not_provided", description="match | mismatch | uncertain | not_provided")
    disease_status: str = Field(default="requires_second_stage", description="not_started | unclear | requires_second_stage")

    crop: CropInfo = Field(default_factory=CropInfo)
    plant_part: str = Field(default="Leaf")
    health_status: str = Field(default="requires_second_stage")
    disease: DiseaseInfo = Field(default_factory=DiseaseInfo)
    symptoms: List[str] = Field(default_factory=list)
    possible_causes: List[str] = Field(default_factory=list)
    management: List[str] = Field(default_factory=list)
    prevention: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="low", description="low | medium | high | uncertain")
    limitations: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="PlantNet identification is an AI-assisted preliminary species identification and is not a guaranteed disease diagnosis."
    )

    # Backward compatibility fields
    plant_detected: bool = Field(default=True)
    image_quality: Optional[ImageQualityAssessment] = Field(default_factory=ImageQualityAssessment)
    crop_recognition: Optional[CropRecognition] = None
    crop_comparison: Optional[CropComparison] = None
    next_image_request: Optional[NextImageRequest] = Field(default_factory=NextImageRequest)
    health_assessment: Optional[HealthAssessment] = None
    primary_diagnosis: Optional[PrimaryDiagnosis] = None
    alternative_diagnoses: List[AlternativeDiagnosis] = Field(default_factory=list)
    immediate_actions: List[str] = Field(default_factory=list)
    chemical_control_guidance: Optional[ChemicalControlGuidance] = Field(default_factory=ChemicalControlGuidance)
    model_disclaimer: str = Field(
        default="Plant identified by PlantNet. Disease diagnosis requires a separate disease-analysis model or expert confirmation."
    )
    language: str = Field(default="en")
    validation_warnings: List[ValidationWarning] = Field(default_factory=list)


class ImageMetadata(BaseModel):
    original_filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    storage_reference: str


class DiseaseAnalysisResponse(BaseModel):
    message: str = Field(default="Crop image identified successfully via PlantNet.")
    analysis_id: str
    created_at: str
    provider: str = Field(default="PlantNet")
    model: Optional[ModelInfo] = None
    result: DiseaseAnalysisResult
    warnings: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="PlantNet identification is an AI-assisted preliminary identification and is not a guaranteed disease diagnosis."
    )


class DiseaseHistoryItem(BaseModel):
    analysis_id: str
    created_at: str
    provider: str = "PlantNet"
    selected_crop: Optional[str] = None
    detected_crop: Optional[str] = None
    detected_scientific_name: Optional[str] = None
    detected_crop_category: str = "vegetable"
    plantnet_score: Optional[float] = None
    crop_status: str = "recognized"
    identification_status: str = "identified"
    crop_match_status: str = "not_provided"
    plantnet_results: List[Dict[str, Any]] = Field(default_factory=list)
    plant_part: str = "Leaf"
    health_status: str = "requires_second_stage"
    disease_status: str = "requires_second_stage"
    ranked_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    original_confidence: Dict[str, Optional[float]] = Field(default_factory=dict)
    primary_diagnosis: Dict[str, Any] = Field(default_factory=dict)
    feature_analysis: Optional[Dict[str, Any]] = None
    ambiguity: Optional[Dict[str, Any]] = None
    next_image_request: Optional[Dict[str, Any]] = None
    symptoms: List[str] = Field(default_factory=list)
    possible_causes: List[str] = Field(default_factory=list)
    immediate_actions: List[str] = Field(default_factory=list)
    prevention: List[str] = Field(default_factory=list)
    image_quality: Dict[str, Any] = Field(default_factory=dict)
    has_image: bool = True
    image_url: Optional[str] = None
    image_metadata: Optional[ImageMetadata] = None
    model: Optional[ModelInfo] = None
    language: str = "en"
    warnings: List[str] = Field(default_factory=list)
    disclaimer: str = "PlantNet identification is an AI-assisted preliminary identification and is not a guaranteed disease diagnosis."

    # Compatibility aliases
    crop: Optional[str] = None
    user_id: Optional[str] = None
    user_symptoms: Optional[str] = None
    user_notes: Optional[str] = None
    image: Optional[ImageMetadata] = None
    result: Optional[DiseaseAnalysisResult] = None


class DiseaseHistoryListResponse(BaseModel):
    analyses: List[DiseaseHistoryItem]
    total_count: int
    user_id: str
