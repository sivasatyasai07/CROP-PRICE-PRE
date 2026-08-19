import React from 'react';
import { Loader2, Sparkles } from 'lucide-react';
import type { Language } from '../../i18n/translations';
import { getDiseaseI18n } from '../../utils/i18nDisease';

export interface DiseaseLoadingStateProps {
  primaryMessage?: string;
  secondaryMessage?: string;
  loadingStep?: string;
  language?: Language;
}

export const DiseaseLoadingState: React.FC<DiseaseLoadingStateProps> = ({
  primaryMessage,
  secondaryMessage,
  loadingStep,
  language = 'en',
}) => {
  const dI18n = getDiseaseI18n(language);
  const mainText = loadingStep || primaryMessage || dI18n.analyzingFoliage;
  const subText = secondaryMessage || dI18n.loadingStepDiagnosis;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 2rem',
        background: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 4px 16px rgba(0,0,0,0.05)',
        textAlign: 'center',
        gap: '1.25rem',
      }}
    >
      <div
        style={{
          position: 'relative',
          width: '72px',
          height: '72px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Loader2
          size={56}
          className="spin"
          color="#16a34a"
          style={{ animation: 'spin 1.5s linear infinite' }}
        />
        <div
          style={{
            position: 'absolute',
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: '#dcfce7',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Sparkles size={16} color="#16a34a" />
        </div>
      </div>

      <div>
        <h4 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.35rem 0' }}>
          {mainText}
        </h4>
        <p style={{ fontSize: '0.88rem', color: '#64748b', margin: 0, maxWidth: '420px' }}>
          {subText}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#f8fafc', padding: '0.5rem 1rem', borderRadius: '50px', border: '1px solid #e2e8f0', fontSize: '0.78rem', color: '#475569' }}>
        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e', display: 'inline-block' }}></span>
        <span>{dI18n.openSetLabel}</span>
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
