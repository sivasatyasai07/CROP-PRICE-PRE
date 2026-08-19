import React from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import type { Language } from '../../i18n/translations';
import { getDiseaseI18n } from '../../utils/i18nDisease';

export interface DiseaseAnalysisButtonProps {
  onClick: () => void;
  loading: boolean;
  disabled?: boolean;
  language?: Language;
}

export const DiseaseAnalysisButton: React.FC<DiseaseAnalysisButtonProps> = ({
  onClick,
  loading,
  disabled = false,
  language = 'en',
}) => {
  const dI18n = getDiseaseI18n(language);

  return (
    <button
      type="button"
      id="btn-analyze-crop-disease"
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        width: '100%',
        padding: '0.85rem 1.5rem',
        borderRadius: '12px',
        border: 'none',
        background: disabled ? '#94a3b8' : 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
        color: '#ffffff',
        fontSize: '0.98rem',
        fontWeight: 800,
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.6rem',
        boxShadow: disabled ? 'none' : '0 4px 14px rgba(22, 163, 74, 0.3)',
        transition: 'all 0.2s ease',
      }}
    >
      {loading ? (
        <>
          <Loader2 size={20} className="animate-spin" />
          <span>{dI18n.analyzingFoliage}</span>
        </>
      ) : (
        <>
          <Sparkles size={20} color="#fef08a" />
          <span>{dI18n.analyzeBtn}</span>
        </>
      )}
    </button>
  );
};
