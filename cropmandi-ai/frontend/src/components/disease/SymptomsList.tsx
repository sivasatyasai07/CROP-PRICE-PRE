import React from 'react';
import { Eye, HelpCircle } from 'lucide-react';
import type { Language } from '../../i18n/translations';
import { getDiseaseI18n } from '../../utils/i18nDisease';

export interface SymptomsListProps {
  symptoms: string[];
  possibleCauses: string[];
  language?: Language;
}

export const SymptomsList: React.FC<SymptomsListProps> = ({ symptoms, possibleCauses, language = 'en' }) => {
  const dI18n = getDiseaseI18n(language);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
      
      {/* Observable Symptoms */}
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
            color: '#1e293b',
            margin: '0 0 0.65rem 0',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <Eye size={16} color="#2563eb" />
          <span>{dI18n.symptomsObserved}</span>
        </h4>

        {symptoms && symptoms.length > 0 ? (
          <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.84rem', color: '#334155', lineHeight: 1.6 }}>
            {symptoms.map((s, idx) => (
              <li key={idx} style={{ marginBottom: '0.25rem' }}>
                {s}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ fontSize: '0.82rem', color: '#64748b', margin: 0 }}>
            --
          </p>
        )}
      </div>

      {/* Possible Causes */}
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
            color: '#1e293b',
            margin: '0 0 0.65rem 0',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <HelpCircle size={16} color="#7c3aed" />
          <span>{dI18n.alternativePossibilities}</span>
        </h4>

        {possibleCauses && possibleCauses.length > 0 ? (
          <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.84rem', color: '#334155', lineHeight: 1.6 }}>
            {possibleCauses.map((c, idx) => (
              <li key={idx} style={{ marginBottom: '0.25rem' }}>
                {c}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ fontSize: '0.82rem', color: '#64748b', margin: 0 }}>
            --
          </p>
        )}
      </div>

    </div>
  );
};
