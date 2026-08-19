import React from 'react';
import { Loader2, Database, Sparkles, ShieldCheck, FileCheck, CheckCircle2 } from 'lucide-react';

export interface ForecastLoadingStateProps {
  loadingStep?: string;
  stepIndex?: number;
}

export const ForecastLoadingState: React.FC<ForecastLoadingStateProps> = ({
  loadingStep,
  stepIndex = 1
}) => {
  const steps = [
    { label: 'Stage 1 of 5: Querying official data.gov.in API records with filters...', icon: ShieldCheck },
    { label: 'Stage 2 of 5: Checking verified official records across 4-date horizon...', icon: Database },
    { label: 'Stage 3 of 5: Checking master-data.csv & building feature vectors...', icon: FileCheck },
    { label: 'Stage 4 of 5: Executing CatBoost ML model inference for missing dates...', icon: Sparkles },
    { label: 'Stage 5 of 5: Finalizing verified predictions & conformal intervals...', icon: CheckCircle2 },
  ];

  const currentLabel = loadingStep || (steps[stepIndex - 1]?.label ?? 'Processing price verification…');

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        padding: '2.5rem 1.5rem',
        textAlign: 'center',
        margin: '1.5rem 0',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '1rem',
      }}
    >
      <div
        style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          background: '#dcfce7',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Loader2
          size={30}
          className="spin"
          color="#16a34a"
          style={{ animation: 'spin 1.5s linear infinite' }}
        />
      </div>

      <div>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.35rem 0' }}>
          {currentLabel}
        </h3>
        <p style={{ fontSize: '0.88rem', color: '#64748b', margin: '0 auto', maxWidth: '520px' }}>
          Executing strict 5-level precedence: Official API (data.gov.in) → master-data.csv → CatBoost ML Prediction → Fallback → Unavailable.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.5rem' }}>
        {[1, 2, 3, 4, 5].map((step) => (
          <div
            key={step}
            style={{
              width: '28px',
              height: '6px',
              borderRadius: '4px',
              background: step <= stepIndex ? '#16a34a' : '#e2e8f0',
              transition: 'background 0.3s ease',
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
