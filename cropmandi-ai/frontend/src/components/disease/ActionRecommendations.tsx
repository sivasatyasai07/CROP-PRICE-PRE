import React from 'react';
import { CheckCircle2, Shield, Stethoscope } from 'lucide-react';
import type { ChemicalControlGuidance } from '../../types/disease';
import type { Language } from '../../i18n/translations';
import { getDiseaseI18n } from '../../utils/i18nDisease';

export interface ActionRecommendationsProps {
  immediateActions: string[];
  prevention: string[];
  chemicalGuidance?: string | ChemicalControlGuidance;
  language?: Language;
}

export const ActionRecommendations: React.FC<ActionRecommendationsProps> = ({
  immediateActions,
  prevention,
  chemicalGuidance,
  language = 'en',
}) => {
  const dI18n = getDiseaseI18n(language);

  const chemMessage =
    typeof chemicalGuidance === 'string'
      ? chemicalGuidance
      : chemicalGuidance?.message || dI18n.disclaimerText;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      
      {/* 2-Column Grid: Immediate Actions & Long-term Prevention */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
        
        {/* Immediate Actions */}
        <div
          style={{
            background: '#f0fdf4',
            borderRadius: '12px',
            border: '1px solid #bbf7d0',
            padding: '1rem 1.2rem',
          }}
        >
          <h4
            style={{
              fontSize: '0.88rem',
              fontWeight: 800,
              color: '#15803d',
              margin: '0 0 0.65rem 0',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <CheckCircle2 size={16} />
            <span>{dI18n.immediateActions}</span>
          </h4>

          {immediateActions && immediateActions.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.84rem', color: '#166534', lineHeight: 1.45 }}>
              {immediateActions.map((action, idx) => (
                <li key={idx} style={{ marginBottom: '0.35rem' }}>
                  {action}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ margin: 0, fontSize: '0.82rem', color: '#166534' }}>
              --
            </p>
          )}
        </div>

        {/* Preventive Suggestions */}
        <div
          style={{
            background: '#f8fafc',
            borderRadius: '12px',
            border: '1px solid #e2e8f0',
            padding: '1rem 1.2rem',
          }}
        >
          <h4
            style={{
              fontSize: '0.88rem',
              fontWeight: 800,
              color: '#0f172a',
              margin: '0 0 0.65rem 0',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Shield size={16} color="#0284c7" />
            <span>{dI18n.preventiveMeasures}</span>
          </h4>

          {prevention && prevention.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.84rem', color: '#334155', lineHeight: 1.45 }}>
              {prevention.map((prev, idx) => (
                <li key={idx} style={{ marginBottom: '0.35rem' }}>
                  {prev}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748b' }}>
              --
            </p>
          )}
        </div>

      </div>

      {/* Chemical Safety & Expert Guidance Note */}
      <div
        style={{
          background: '#eff6ff',
          borderRadius: '12px',
          border: '1px solid #bfdbfe',
          padding: '0.85rem 1.15rem',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.65rem',
        }}
      >
        <Stethoscope size={18} color="#2563eb" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#1e40af', marginBottom: '0.15rem' }}>
            {dI18n.chemicalControl}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#1e3a8a', lineHeight: 1.4 }}>
            {chemMessage}
          </div>
        </div>
      </div>

    </div>
  );
};
