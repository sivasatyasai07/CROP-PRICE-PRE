import React from 'react';
import { AlertTriangle, AlertCircle, Info, Leaf } from 'lucide-react';
import type { Language } from '../../i18n/translations';

export interface DiagnosisConfidenceProps {
  confidence?: number | null;
  scoreLabel?: string;
  language?: Language;
}

export const DiagnosisConfidence: React.FC<DiagnosisConfidenceProps> = ({ 
  confidence, 
  scoreLabel = "PlantNet identification score", 
}) => {
  if (confidence === null || confidence === undefined || typeof confidence !== 'number') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '999px',
            background: '#f1f5f9',
            border: '1px solid #e2e8f0',
            color: '#64748b',
            fontSize: '0.82rem',
            fontWeight: 800,
          }}
        >
          <Info size={15} />
          <span>{scoreLabel}: --</span>
        </div>
      </div>
    );
  }

  const percentage = Math.round(confidence * 100);

  let badgeLabel = 'Identified';
  let badgeColor = '#16a34a';
  let badgeBg = '#dcfce7';
  let badgeBorder = '#bbf7d0';
  let Icon = Leaf;
  let isLow = false;

  if (confidence < 0.25) {
    badgeLabel = 'Low score';
    badgeColor = '#dc2626';
    badgeBg = '#fef2f2';
    badgeBorder = '#fee2e2';
    Icon = AlertCircle;
    isLow = true;
  } else if (confidence < 0.60) {
    badgeLabel = 'Probable';
    badgeColor = '#d97706';
    badgeBg = '#fef3c7';
    badgeBorder = '#fde68a';
    Icon = AlertTriangle;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '999px',
            background: badgeBg,
            border: `1px solid ${badgeBorder}`,
            color: badgeColor,
            fontSize: '0.82rem',
            fontWeight: 800,
          }}
        >
          <Icon size={15} />
          <span>
            {scoreLabel}: {percentage}% ({badgeLabel})
          </span>
        </div>
      </div>

      <p style={{ fontSize: '0.78rem', color: '#64748b', margin: 0, lineHeight: 1.4 }}>
        PlantNet identification is an AI-assisted preliminary botanical identification and is not a guaranteed disease diagnosis.
      </p>

      {isLow && (
        <div
          style={{
            background: '#fef2f2',
            border: '1px solid #fee2e2',
            borderRadius: '8px',
            padding: '0.5rem 0.75rem',
            color: '#dc2626',
            fontSize: '0.78rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <AlertCircle size={15} />
          <span>Low identification score. Upload a clearer image showing the leaf, flower, or fruit.</span>
        </div>
      )}
    </div>
  );
};
