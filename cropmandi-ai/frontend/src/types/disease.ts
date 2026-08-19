export type AnalysisStatus =
  | 'success'
  | 'unclear_image'
  | 'crop_mismatch'
  | 'non_plant_image'
  | 'insufficient_evidence'
  | 'service_error'
  | 'plantnet_authentication_error'
  | 'plantnet_rate_limit_error'
  | 'plantnet_timeout'
  | 'plantnet_invalid_response'
  | 'plantnet_unavailable';

export type HealthStatus =
  | 'healthy'
  | 'disease'
  | 'fungal_disease'
  | 'bacterial_disease'
  | 'viral_disease'
  | 'pest_damage'
  | 'nutrient_deficiency'
  | 'physical_damage'
  | 'abiotic_stress'
  | 'mixed_or_multiple'
  | 'unclear'
  | 'non_plant_image'
  | 'insufficient_evidence'
  | 'diseased'
  | 'requires_second_stage'
  | 'not_started'
  | 'not_available';

export type IdentificationStatus = 'identified' | 'probable' | 'low_confidence' | 'unidentified' | 'unavailable';

export type CropMatchStatus = 'match' | 'mismatch' | 'uncertain' | 'not_provided' | 'not_specified';

export interface PlantNetSpeciesCandidate {
  scientific_name: string;
  common_names: string[];
  family?: string | null;
  score: number;
  rank: number;
}

export interface ImageQualityAssessment {
  status: 'acceptable' | 'partially_usable' | 'poor' | 'non_plant_image' | 'insufficient_evidence' | 'unclear';
  score?: number | null;
  original_confidence?: number | null;
  issues: string[];
}

export interface LeafMarginAnalysis {
  type: string;
  original_confidence?: number | null;
  evidence: string;
  reliability: 'usable' | 'unreliable' | 'unavailable' | string;
}

export interface FeatureAnalysis {
  leaf_margin?: LeafMarginAnalysis;
  leaf_shape?: string;
  leaf_apex?: string;
  leaf_base?: string;
  leaf_venation?: string;
  leaf_texture?: string;
  leaf_arrangement?: string;
  stem_features?: string;
  fruit_features?: string;
  flower_features?: string;
  root_features?: string;
}

export interface CropCandidate {
  name: string;
  category: string;
  crop_status?: string;
  gemini_original_probability?: number | null;
  classifier_probability?: number | null;
  combined_probability?: number | null;
  supporting_evidence?: string[];
  contradicting_evidence?: string[];
}

export interface BestCrop {
  name: string;
  category: string;
  crop_status?: string;
  gemini_original_probability?: number | null;
  classifier_probability?: number | null;
  combined_probability?: number | null;
  final_selection_source?: string;
}

export interface AmbiguityInfo {
  status: 'low' | 'moderate' | 'high' | string;
  top_candidate_gap?: number | null;
  message?: string;
}

export interface NextImageRequest {
  needed: boolean;
  suggested_images?: string[];
}

export interface CropRecognition {
  identification_status: IdentificationStatus;
  best_crop: BestCrop;
  ranked_candidates: CropCandidate[];
  feature_analysis?: FeatureAnalysis;
  ambiguity?: AmbiguityInfo;

  // Backward compatibility
  crop_name?: string;
  confidence?: number | null;
}

export interface CropComparison {
  user_selected_crop?: string | null;
  detected_best_crop: string;
  match_status: CropMatchStatus;
  reason: string;
}

export interface PlantPartInfo {
  name: string;
  confidence?: number | null;
}

export interface HealthAssessment {
  status: HealthStatus | string;
  confidence?: number | null;
  visible_evidence: string[];
}

export interface PrimaryDiagnosis {
  name: string;
  category?: string;
  confidence?: number | null;
  evidence: string[];
}

export interface AlternativeDiagnosis {
  name: string;
  category?: string;
  confidence?: number | null;
  reason?: string;
  distinguishing_evidence?: string;
}

export interface ChemicalControlGuidance {
  provided: boolean;
  message: string;
}

export interface ModelInfo {
  provider: string;
  model_name: string;
  project?: string;
  prompt_version?: string;
  temperature?: number;
  request_timestamp?: string;
}

export interface ValidationWarning {
  field: string;
  issue: string;
  action: string;
}

export interface CropInfo {
  name: string;
  confidence?: number | null;
}

export interface DiseaseInfo {
  name: string;
  confidence?: number | null;
}

export interface DiseaseAnalysisResult {
  analysis_status?: AnalysisStatus | string;
  provider?: string;
  selected_crop?: string | null;
  detected_crop?: string | null;
  detected_scientific_name?: string | null;
  crop_category?: string | null;
  plantnet_score?: number | null;
  identification_status?: IdentificationStatus | string;
  plantnet_results?: PlantNetSpeciesCandidate[];
  crop_match_status?: CropMatchStatus | string;
  disease_status?: string;

  crop?: CropInfo | string;
  plant_part?: PlantPartInfo | string;
  health_status?: HealthStatus | string;
  disease?: DiseaseInfo;
  symptoms?: string[];
  possible_causes?: string[];
  management?: string[];
  prevention?: string[];
  risk_level?: string;
  limitations?: string[];
  disclaimer?: string;

  // Optional and backward compatibility fields
  image_quality?: ImageQualityAssessment;
  plant_detected?: boolean;
  crop_recognition?: CropRecognition;
  crop_comparison?: CropComparison;
  next_image_request?: NextImageRequest;
  health_assessment?: HealthAssessment;
  primary_diagnosis?: PrimaryDiagnosis;
  alternative_diagnoses?: AlternativeDiagnosis[];
  immediate_actions?: string[];
  chemical_control_guidance?: ChemicalControlGuidance;
  model_disclaimer?: string;
  language?: string;
  validation_warnings?: ValidationWarning[];
  selected_crop_comparison?: CropComparison;
  alternative_possibilities?: AlternativeDiagnosis[];
}

export interface ImageMetadata {
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  storage_reference: string;
}

export interface DiseaseAnalysisResponse {
  message: string;
  analysis_id: string;
  created_at: string;
  provider?: string;
  model?: ModelInfo;
  result: DiseaseAnalysisResult;
  warnings?: string[];
  disclaimer?: string;
}

export interface DiseaseHistoryItem {
  analysis_id: string;
  created_at: string;
  provider?: string;
  selected_crop?: string | null;
  detected_crop: string;
  detected_scientific_name?: string | null;
  detected_crop_category?: string;
  plantnet_score?: number | null;
  crop_status?: string;
  identification_status?: string;
  crop_match_status?: string;
  plantnet_results?: PlantNetSpeciesCandidate[];
  plant_part: string;
  health_status: string;
  disease_status?: string;
  ranked_candidates?: CropCandidate[];
  original_confidence: {
    crop?: number | null;
    plantnet_score?: number | null;
    plant_part?: number | null;
    health_status?: number | null;
    primary_diagnosis?: number | null;
  };
  gemini_original_probability?: number | null;
  classifier_probability?: number | null;
  combined_probability?: number | null;
  feature_analysis?: FeatureAnalysis;
  ambiguity?: AmbiguityInfo;
  next_image_request?: NextImageRequest;
  primary_diagnosis: {
    name: string;
    category?: string;
    confidence?: number | null;
    evidence: string[];
  };
  symptoms: string[];
  possible_causes: string[];
  immediate_actions: string[];
  prevention: string[];
  image_quality?: Record<string, any>;
  has_image?: boolean;
  image_url?: string;
  image_metadata?: ImageMetadata;
  model?: ModelInfo;
  language?: string;
  warnings?: string[];
  disclaimer?: string;

  // Compatibility aliases
  crop?: string;
  user_id?: string;
  user_symptoms?: string | null;
  user_notes?: string | null;
  image?: ImageMetadata;
  result?: DiseaseAnalysisResult;
}

export interface DiseaseHistoryListResponse {
  analyses: DiseaseHistoryItem[];
  total_count: number;
  user_id: string;
}
