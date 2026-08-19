import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface PasswordInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  autocomplete?: string;
  error?: string;
  required?: boolean;
}

export const PasswordInput: React.FC<PasswordInputProps> = ({
  id,
  label,
  value,
  onChange,
  placeholder = '••••••••',
  autocomplete = 'current-password',
  error,
  required = true,
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div style={{ marginBottom: '1.2rem' }}>
      <label
        htmlFor={id}
        style={{
          display: 'block',
          fontSize: '0.88rem',
          fontWeight: 700,
          color: 'var(--primary-dark)',
          marginBottom: '0.4rem',
        }}
      >
        {label} {required && <span style={{ color: '#ef4444' }}>*</span>}
      </label>
      <div style={{ position: 'relative' }}>
        <input
          id={id}
          type={showPassword ? 'text' : 'password'}
          className="form-input"
          style={{
            paddingRight: '2.75rem',
            borderColor: error ? '#ef4444' : undefined,
            width: '100%',
          }}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autocomplete}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          required={required}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          style={{
            position: 'absolute',
            right: '0.75rem',
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'none',
            border: 'none',
            color: '#64748b',
            cursor: 'pointer',
            padding: '0.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
          title={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
      {error && (
        <p id={`${id}-error`} style={{ color: '#ef4444', fontSize: '0.82rem', marginTop: '0.35rem', fontWeight: 500 }}>
          {error}
        </p>
      )}
    </div>
  );
};
