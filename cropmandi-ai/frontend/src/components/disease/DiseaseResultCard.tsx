import React from 'react';
import type { DiseaseAnalysisResult, ImageMetadata } from '../../types/disease';
import type { Language } from '../../i18n/translations';
import {
  AlertTriangle,
  Activity,
  Sparkles,
  Layers,
  Leaf,
  CheckCircle2,
  XCircle,
  ServerCrash,
  ShieldAlert,
  ShieldCheck,
  Stethoscope,
  Wrench,
  CheckCheck,
} from 'lucide-react';
import { DiagnosisConfidence } from './DiagnosisConfidence';

export interface DiseaseResultCardProps {
  result: DiseaseAnalysisResult;
  imageMeta?: ImageMetadata;
  imageUrl?: string;
  createdAt?: string;
  language?: Language;
}

export const DiseaseResultCard: React.FC<DiseaseResultCardProps> = ({
  result,
}) => {
  const status = result.analysis_status || 'success';

  const isServiceError = [
    'service_error',
    'plantnet_authentication_error',
    'plantnet_unavailable',
    'plantnet_timeout',
    'plantnet_rate_limit_error',
    'plantnet_invalid_response',
  ].includes(status);

  const isInsufficientEvidence = status === 'insufficient_evidence';
  const isNonPlant = status === 'non_plant_image';

  // 1. SERVICE ERROR / PROVIDER UNAVAILABLE STATE
  if (isServiceError) {
    let errorTitle = 'Plant Identification Service Unavailable';
    let errorMessage = 'Plant identification service is temporarily unavailable. Please try again later.';

    if (status === 'plantnet_authentication_error') {
      errorTitle = 'PlantNet Authentication Error';
      errorMessage = 'PlantNet API authentication failed. Please verify the API key in the backend environment.';
    } else if (status === 'plantnet_rate_limit_error') {
      errorTitle = 'PlantNet Rate Limit Reached';
      errorMessage = 'PlantNet API rate limit exceeded. Please wait a moment and try again.';
    } else if (status === 'plantnet_timeout') {
      errorTitle = 'PlantNet Connection Timeout';
      errorMessage = 'PlantNet identification service timed out. Please try again.';
    }

    return (
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          border: '1px solid #fecaca',
          boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#dc2626' }}>
          <ServerCrash size={28} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
            {errorTitle}
          </h3>
        </div>

        <div
          style={{
            background: '#fef2f2',
            border: '1px solid #fee2e2',
            borderRadius: '12px',
            padding: '1.25rem',
            color: '#991b1b',
            fontSize: '0.95rem',
            lineHeight: 1.5,
          }}
        >
          <strong>{errorMessage}</strong>
          {result.validation_warnings && result.validation_warnings.length > 0 && (
            <ul style={{ marginTop: '0.75rem', marginBottom: 0, paddingLeft: '1.25rem' }}>
              {result.validation_warnings.map((w, idx) => (
                <li key={idx}>{typeof w === 'string' ? w : w.issue}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    );
  }

  // 2. INSUFFICIENT EVIDENCE / NON-PLANT IMAGE STATE
  if (isInsufficientEvidence || isNonPlant) {
    return (
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          border: '1px solid #fed7aa',
          boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#c2410c' }}>
          <AlertTriangle size={28} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
            {isNonPlant ? 'Non-Plant Image Detected' : 'PlantNet Could Not Confidently Identify Plant'}
          </h3>
        </div>

        <div
          style={{
            background: '#fff7ed',
            border: '1px solid #ffedd5',
            borderRadius: '12px',
            padding: '1.25rem',
            color: '#9a3412',
            fontSize: '0.95rem',
            lineHeight: 1.5,
          }}
        >
          <strong>
            {isNonPlant
              ? 'Please upload a clear image of a crop leaf, fruit, flower, or foliage.'
              : 'PlantNet could not identify this image confidently. Upload a clearer image showing the leaf, fruit, stem, or whole plant.'}
          </strong>
          {result.validation_warnings && result.validation_warnings.length > 0 && (
            <ul style={{ marginTop: '0.75rem', marginBottom: 0, paddingLeft: '1.25rem' }}>
              {result.validation_warnings.map((w, idx) => (
                <li key={idx}>{typeof w === 'string' ? w : w.issue}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    );
  }

  // 3. SUCCESSFUL IDENTIFICATION & DISEASE DIAGNOSIS VIEW
  const cropName = result.detected_crop || (typeof result.crop === 'object' && result.crop !== null ? result.crop.name : (result.crop || 'Crop'));
  const scientificName = result.detected_scientific_name || result.plantnet_results?.[0]?.scientific_name || null;
  const plantnetScore = result.plantnet_score ?? (typeof result.crop === 'object' && result.crop !== null ? result.crop.confidence : null);
  const familyName = result.plantnet_results?.[0]?.family || null;

  const isMismatch = result.crop_match_status === 'mismatch';
  const selectedCrop = result.selected_crop;

  // Disease diagnosis details
  const diseaseName = (typeof result.disease === 'object' && result.disease !== null ? result.disease.name : result.disease) || result.primary_diagnosis?.name || 'Healthy Plant';
  const isHealthy = (result.health_status === 'healthy') || diseaseName.toLowerCase().includes('healthy');
  const symptoms = result.symptoms || [];
  const causes = result.possible_causes || [];
  const management = (result.management && result.management.length > 0 ? result.management : result.immediate_actions) || [];
  const prevention = result.prevention || [];
  const riskLevel = result.risk_level || (isHealthy ? 'low' : 'medium');

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        padding: '2rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
      }}
    >
      {/* 1. TOP HERO SUMMARY GRID */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
        }}
      >
        {/* Identified Plant */}
        <div
          style={{
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '12px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.35rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#166534', fontSize: '0.82rem', fontWeight: 700 }}>
            <Leaf size={16} />
            <span>Identified Crop</span>
          </div>
          <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#14532d' }}>
            {cropName}
          </div>
          {scientificName && (
            <div style={{ fontSize: '0.82rem', color: '#15803d', fontStyle: 'italic' }}>
              {scientificName}
            </div>
          )}
          {familyName && (
            <div style={{ fontSize: '0.75rem', color: '#166534' }}>
              Family: {familyName}
            </div>
          )}
        </div>

        {/* Botanical / Identification Score */}
        <div
          style={{
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '12px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#475569', fontSize: '0.82rem', fontWeight: 700 }}>
            <Sparkles size={16} />
            <span>Identification Confidence</span>
          </div>
          <DiagnosisConfidence confidence={plantnetScore} scoreLabel="Identification score" />
        </div>

        {/* Health / Risk Status */}
        <div
          style={{
            background: isHealthy ? '#f0fdf4' : '#fff1f2',
            border: isHealthy ? '1px solid #bbf7d0' : '1px solid #fecdd3',
            borderRadius: '12px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.35rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: isHealthy ? '#166534' : '#9f1239', fontSize: '0.82rem', fontWeight: 700 }}>
            {isHealthy ? <ShieldCheck size={16} /> : <ShieldAlert size={16} />}
            <span>Crop Health Status</span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: isHealthy ? '#15803d' : '#be123c' }}>
            {isHealthy ? 'Healthy Foliage' : 'Disease Detected'}
          </div>
          <div style={{ fontSize: '0.8rem', color: isHealthy ? '#166534' : '#9f1239', textTransform: 'capitalize' }}>
            Risk Level: <strong>{riskLevel}</strong>
          </div>
        </div>

        {/* Selected Crop Match Status */}
        {selectedCrop && (
          <div
            style={{
              background: isMismatch ? '#fff1f2' : '#f0fdf4',
              border: isMismatch ? '1px solid #fecdd3' : '1px solid #bbf7d0',
              borderRadius: '12px',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.35rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: isMismatch ? '#9f1239' : '#166534', fontSize: '0.82rem', fontWeight: 700 }}>
              {isMismatch ? <XCircle size={16} /> : <CheckCircle2 size={16} />}
              <span>Crop Verification</span>
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: isMismatch ? '#be123c' : '#15803d' }}>
              {isMismatch ? 'Selected Crop Mismatch' : 'Crop Match Confirmed'}
            </div>
            <div style={{ fontSize: '0.78rem', color: isMismatch ? '#9f1239' : '#166534', lineHeight: 1.35 }}>
              {isMismatch
                ? `The selected crop '${selectedCrop}' may differ from identified crop '${cropName}'.`
                : `Uploaded image matches selected crop '${selectedCrop}'.`}
            </div>
          </div>
        )}
      </div>

      {/* 2. PRIMARY DISEASE DIAGNOSIS CARD */}
      <div
        style={{
          background: isHealthy ? '#f0fdf4' : '#fffbeb',
          border: isHealthy ? '1px solid #86efac' : '1px solid #fde68a',
          borderRadius: '12px',
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Stethoscope size={24} color={isHealthy ? '#16a34a' : '#d97706'} />
            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: isHealthy ? '#166534' : '#92400e', textTransform: 'uppercase' }}>
                Primary Pathology Diagnosis
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 800, color: isHealthy ? '#14532d' : '#78350f' }}>
                {diseaseName}
              </div>
            </div>
          </div>
          <span
            style={{
              background: isHealthy ? '#dcfce7' : '#fef3c7',
              color: isHealthy ? '#15803d' : '#92400e',
              border: `1px solid ${isHealthy ? '#bbf7d0' : '#fde68a'}`,
              borderRadius: '20px',
              padding: '0.35rem 0.85rem',
              fontWeight: 700,
              fontSize: '0.82rem',
            }}
          >
            {isHealthy ? 'No Active Infection' : 'Action Required'}
          </span>
        </div>
      </div>

      {/* 3. SYMPTOMS & CAUSES SECTION */}
      {(symptoms.length > 0 || causes.length > 0) && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1rem',
          }}
        >
          {/* Visible Symptoms */}
          {symptoms.length > 0 && (
            <div
              style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                padding: '1.25rem',
              }}
            >
              <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Activity size={18} color="var(--primary)" />
                Observed Symptoms
              </h4>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {symptoms.map((sym, idx) => (
                  <li key={idx} style={{ fontSize: '0.88rem', color: '#334155', lineHeight: 1.45 }}>
                    {sym}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Possible Causes */}
          {causes.length > 0 && (
            <div
              style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                padding: '1.25rem',
              }}
            >
              <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <AlertTriangle size={18} color="#d97706" />
                Underlying Causes & Pathogens
              </h4>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {causes.map((cause, idx) => (
                  <li key={idx} style={{ fontSize: '0.88rem', color: '#334155', lineHeight: 1.45 }}>
                    {cause}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 4. MANAGEMENT ACTIONS (WHAT TO DO) */}
      {management.length > 0 && (
        <div
          style={{
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '12px',
            padding: '1.25rem 1.5rem',
          }}
        >
          <h4 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#166534', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Wrench size={18} color="#16a34a" />
            Recommended Immediate Actions & Management
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {management.map((step, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.6rem',
                  background: '#ffffff',
                  padding: '0.65rem 0.9rem',
                  borderRadius: '8px',
                  border: '1px solid #dcfce7',
                  fontSize: '0.88rem',
                  color: '#14532d',
                  lineHeight: 1.45,
                }}
              >
                <CheckCheck size={18} color="#16a34a" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. PREVENTATIVE CARE */}
      {prevention.length > 0 && (
        <div
          style={{
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '12px',
            padding: '1.25rem 1.5rem',
          }}
        >
          <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <ShieldCheck size={18} color="var(--primary)" />
            Future Prevention & Field Hygiene
          </h4>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {prevention.map((prev, idx) => (
              <li key={idx} style={{ fontSize: '0.88rem', color: '#475569', lineHeight: 1.45 }}>
                {prev}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 6. PLANTNET RANKED CANDIDATE MATCHES (if available) */}
      {result.plantnet_results && result.plantnet_results.length > 0 && (
        <div
          style={{
            background: '#f8fafc',
            borderRadius: '12px',
            padding: '1.25rem 1.5rem',
            border: '1px solid #e2e8f0',
          }}
        >
          <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Layers size={18} color="var(--primary)" />
            Ranked PlantNet Candidate Matches
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {result.plantnet_results.map((cand, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: '#ffffff',
                  padding: '0.65rem 1rem',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '0.88rem',
                }}
              >
                <div>
                  <strong style={{ color: '#0f172a' }}>#{cand.rank} {cand.scientific_name}</strong>
                  {cand.common_names && cand.common_names.length > 0 && (
                    <span style={{ color: '#64748b', marginLeft: '0.5rem', fontSize: '0.82rem' }}>
                      ({cand.common_names.slice(0, 2).join(', ')})
                    </span>
                  )}
                </div>
                <span
                  style={{
                    background: '#f1f5f9',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '6px',
                    fontWeight: 700,
                    fontSize: '0.82rem',
                    color: '#334155',
                  }}
                >
                  Score: {Math.round(cand.score * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7. DISCLAIMER */}
      <div
        style={{
          background: '#f8fafc',
          borderLeft: '4px solid #94a3b8',
          padding: '0.85rem 1.15rem',
          borderRadius: '8px',
          fontSize: '0.78rem',
          color: '#64748b',
          lineHeight: 1.45,
        }}
      >
        <strong>Disclaimer:</strong> {result.disclaimer || 'This is an AI-assisted preliminary crop disease assessment. Confirm with your local agricultural extension officer or Krishi Vigyan Kendra (KVK) before applying chemical treatments.'}
      </div>
    </div>
  );
};
