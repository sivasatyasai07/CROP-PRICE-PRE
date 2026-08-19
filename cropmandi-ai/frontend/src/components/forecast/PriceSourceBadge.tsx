import React from 'react';

export interface PriceSourceBadgeProps {
  priceSource: 'official_api' | 'official_csv' | 'predicted_model' | 'fallback_last_observed' | 'fallback_rolling_average' | 'unavailable' | 'predicted' | string;
  sourceLabel?: string | null;
  className?: string;
}

export const PriceSourceBadge: React.FC<PriceSourceBadgeProps> = ({
  priceSource,
  sourceLabel,
  className = ''
}) => {
  switch (priceSource) {
    case 'official_api':
      return (
        <span
          className={className}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.2rem 0.65rem',
            borderRadius: '50px',
            fontSize: '0.72rem',
            fontWeight: 800,
            background: '#dcfce7',
            color: '#166534',
            border: '1px solid #86efac',
            letterSpacing: '0.3px',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#16a34a' }}></span>
          {sourceLabel || 'Official API value'}
        </span>
      );

    case 'official_csv':
    case 'official_database':
      return (
        <span
          className={className}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.2rem 0.65rem',
            borderRadius: '50px',
            fontSize: '0.72rem',
            fontWeight: 800,
            background: '#e0f2fe',
            color: '#0369a1',
            border: '1px solid #bae6fd',
            letterSpacing: '0.3px',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#0284c7' }}></span>
          {sourceLabel || 'Official value from master-data.csv'}
        </span>
      );

    case 'predicted_model':
    case 'predicted':
      return (
        <span
          className={className}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.2rem 0.65rem',
            borderRadius: '50px',
            fontSize: '0.72rem',
            fontWeight: 800,
            background: '#fef3c7',
            color: '#92400e',
            border: '1px solid #fde68a',
            letterSpacing: '0.3px',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#f59e0b' }}></span>
          {sourceLabel || 'CatBoost model prediction'}
        </span>
      );

    case 'fallback_last_observed':
      return (
        <span
          className={className}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.2rem 0.65rem',
            borderRadius: '50px',
            fontSize: '0.72rem',
            fontWeight: 800,
            background: '#ffedd5',
            color: '#9a3412',
            border: '1px solid #fed7aa',
            letterSpacing: '0.3px',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#ea580c' }}></span>
          {sourceLabel || 'Last observed price fallback'}
        </span>
      );

    case 'fallback_rolling_average':
      return (
        <span
          className={className}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.2rem 0.65rem',
            borderRadius: '50px',
            fontSize: '0.72rem',
            fontWeight: 800,
            background: '#f1f5f9',
            color: '#475569',
            border: '1px solid #cbd5e1',
            letterSpacing: '0.3px',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#64748b' }}></span>
          {sourceLabel || 'Historical rolling-average fallback'}
        </span>
      );

    case 'unavailable':
    default:
      return (
        <span
          className={className}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.2rem 0.65rem',
            borderRadius: '50px',
            fontSize: '0.72rem',
            fontWeight: 800,
            background: '#fee2e2',
            color: '#991b1b',
            border: '1px solid #fca5a5',
            letterSpacing: '0.3px',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#dc2626' }}></span>
          {sourceLabel || 'Price unavailable'}
        </span>
      );
  }
};

