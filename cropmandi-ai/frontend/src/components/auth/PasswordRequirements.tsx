import React from 'react';
import { Check, X } from 'lucide-react';

interface PasswordRequirementsProps {
  password: string;
  confirmPassword?: string;
  showConfirmCheck?: boolean;
}

export const PasswordRequirements: React.FC<PasswordRequirementsProps> = ({
  password,
  confirmPassword,
  showConfirmCheck = false,
}) => {
  const isStarted = password.length > 0;
  
  const rules = [
    {
      id: 'length',
      label: 'At least 6 characters',
      valid: password.length >= 6,
    },
    {
      id: 'uppercase',
      label: 'Contains one capital letter (A-Z)',
      valid: /[A-Z]/.test(password),
    },
    {
      id: 'symbol',
      label: 'Contains one symbol (e.g. @, #, !, $)',
      valid: /[^A-Za-z0-9\s]/.test(password),
    },
    {
      id: 'no_spaces',
      label: 'Contains no spaces',
      valid: password.length > 0 && !/\s/.test(password),
    },
  ];

  if (showConfirmCheck && confirmPassword !== undefined) {
    rules.push({
      id: 'match',
      label: 'Passwords match',
      valid: confirmPassword.length > 0 && password === confirmPassword,
    });
  }

  const allValid = rules.every(r => r.valid);

  return (
    <div
      style={{
        padding: '0.85rem 1rem',
        borderRadius: '8px',
        backgroundColor: 'rgba(248, 250, 252, 0.8)',
        border: '1px solid #e2e8f0',
        marginBottom: '1.2rem',
        fontSize: '0.82rem',
      }}
    >
      <p style={{ fontWeight: 700, color: '#475569', marginBottom: '0.5rem', marginTop: 0 }}>
        Password requirements:
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        {rules.map((r) => {
          let statusColor = '#64748b'; // neutral
          if (isStarted) {
            statusColor = r.valid ? '#10b981' : '#ef4444';
          }

          return (
            <div
              key={r.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                color: statusColor,
                fontWeight: r.valid && isStarted ? 600 : 500,
                transition: 'color 0.2s ease',
              }}
            >
              {isStarted ? (
                r.valid ? (
                  <Check size={14} style={{ color: '#10b981', flexShrink: 0 }} />
                ) : (
                  <X size={14} style={{ color: '#ef4444', flexShrink: 0 }} />
                )
              ) : (
                <span style={{ display: 'inline-block', width: 14, height: 14, borderRadius: '50%', border: '1px solid #cbd5e1', flexShrink: 0 }} />
              )}
              <span>{r.label}</span>
            </div>
          );
        })}
      </div>

      {isStarted && allValid && (
        <div
          style={{
            marginTop: '0.6rem',
            padding: '0.4rem 0.6rem',
            borderRadius: '6px',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            color: '#059669',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
          }}
        >
          <Check size={16} />
          <span>Password meets all requirements.</span>
        </div>
      )}
    </div>
  );
};
