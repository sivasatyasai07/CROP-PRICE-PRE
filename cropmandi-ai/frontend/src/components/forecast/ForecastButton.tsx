import React from 'react';

export interface ForecastButtonProps {
  onClick: () => void;
  loading: boolean;
  loadingStep?: string;
  disabled?: boolean;
}

export const ForecastButton: React.FC<ForecastButtonProps> = ({
  onClick,
  loading,
  loadingStep,
  disabled = false,
}) => {
  return (
    <button
      id="btn-generate-3-days-forecast"
      type="button"
      onClick={onClick}
      disabled={loading || disabled}
      aria-busy={loading}
      style={{
        background: loading || disabled ? '#2d6a4f' : '#1b4332',
        color: '#ffffff',
        fontWeight: 700,
        fontSize: '0.92rem',
        padding: '0.75rem 1.25rem',
        borderRadius: '10px',
        border: 'none',
        cursor: loading || disabled ? 'not-allowed' : 'pointer',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        boxShadow: '0 2px 8px rgba(27, 67, 50, 0.25)',
        transition: 'all 0.2s ease',
        flex: 1,
        whiteSpace: 'nowrap',
        opacity: disabled && !loading ? 0.6 : 1,
      }}
    >
      {loading ? (
        <>
          <svg
            className="spin"
            style={{ width: '18px', height: '18px' }}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              opacity="0.25"
            ></circle>
            <path
              fill="currentColor"
              opacity="0.75"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span style={{ fontSize: '0.85rem' }}>{loadingStep || 'Generating forecast…'}</span>
        </>
      ) : (
        <>
          <svg
            style={{ width: '18px', height: '18px' }}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
            <path d="m9 16 2 2 4-4"></path>
          </svg>
          <span>Generate 3 Days Forecast</span>
        </>
      )}
    </button>
  );
};
