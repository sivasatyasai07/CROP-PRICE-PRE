import React from 'react';
import { AlertTriangle } from 'lucide-react';
import type { Language } from '../../i18n/translations';
import { getDiseaseI18n } from '../../utils/i18nDisease';

export interface DiseaseDisclaimerProps {
  customText?: string;
  disclaimer?: string;
  language?: Language;
}

export const DiseaseDisclaimer: React.FC<DiseaseDisclaimerProps> = ({
  customText,
  disclaimer,
  language = 'en',
}) => {
  const dI18n = getDiseaseI18n(language);
  const displayText = disclaimer || customText || dI18n.disclaimerText;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.75rem',
        background: '#fffbeb',
        border: '1px solid #fde68a',
        borderRadius: '12px',
        padding: '0.85rem 1.15rem',
      }}
    >
      <AlertTriangle size={18} color="#d97706" style={{ flexShrink: 0, marginTop: '2px' }} />
      <div>
        <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#92400e', marginBottom: '0.15rem' }}>
          {dI18n.disclaimerTitle}
        </div>
        <div style={{ fontSize: '0.76rem', color: '#78350f', lineHeight: 1.45 }}>
          {displayText}
        </div>
      </div>
    </div>
  );
};
