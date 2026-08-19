import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { PasswordInput } from './PasswordInput';
import { LogIn, AlertCircle, CheckCircle2 } from 'lucide-react';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToSignup?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onSwitchToSignup }) => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setEmailError(null);
    setPasswordError(null);
    setSuccessMsg(null);

    let hasError = false;
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanEmail) {
      setEmailError('Email is required.');
      hasError = true;
    } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(cleanEmail)) {
      setEmailError('Enter a valid email address.');
      hasError = true;
    }

    if (!password) {
      setPasswordError('Password is required.');
      hasError = true;
    }

    if (hasError) return;

    setLoading(true);
    try {
      await login({ email: cleanEmail, password });
      setSuccessMsg('Login successful.');
      if (onSuccess) {
        setTimeout(onSuccess, 500);
      }
    } catch (err: any) {
      const serverMsg = err.response?.data?.detail || 'Incorrect email or password.';
      setErrorMsg(serverMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate style={{ width: '100%' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.25rem' }}>
        Welcome Back to CropMandi AI
      </h3>
      <p style={{ fontSize: '0.88rem', color: '#64748b', marginBottom: '1.25rem' }}>
        Log in to access your farmer market insights & price forecasts.
      </p>

      {errorMsg && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid #fca5a5',
            color: '#dc2626',
            fontSize: '0.88rem',
            fontWeight: 600,
            marginBottom: '1.2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid #6ee7b7',
            color: '#059669',
            fontSize: '0.88rem',
            fontWeight: 600,
            marginBottom: '1.2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Email Field */}
      <div style={{ marginBottom: '1.2rem' }}>
        <label
          htmlFor="login-email"
          style={{
            display: 'block',
            fontSize: '0.88rem',
            fontWeight: 700,
            color: 'var(--primary-dark)',
            marginBottom: '0.4rem',
          }}
        >
          Email Address <span style={{ color: '#ef4444' }}>*</span>
        </label>
        <input
          id="login-email"
          type="email"
          className="form-input"
          style={{
            borderColor: emailError ? '#ef4444' : undefined,
            width: '100%',
          }}
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (emailError) setEmailError(null);
          }}
          placeholder="farmer@example.com"
          autoComplete="email"
          required
        />
        {emailError && (
          <p style={{ color: '#ef4444', fontSize: '0.82rem', marginTop: '0.35rem', fontWeight: 500 }}>
            {emailError}
          </p>
        )}
      </div>

      {/* Password Field */}
      <PasswordInput
        id="login-password"
        label="Password"
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          if (passwordError) setPasswordError(null);
        }}
        autocomplete="current-password"
        error={passwordError || undefined}
        required
      />

      {/* Submit Button */}
      <button
        type="submit"
        className="btn btn-primary"
        disabled={loading}
        style={{
          width: '100%',
          padding: '0.75rem',
          fontSize: '1rem',
          fontWeight: 700,
          marginTop: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem',
        }}
      >
        {loading ? (
          <span>Logging in...</span>
        ) : (
          <>
            <LogIn size={18} />
            <span>Login to Account</span>
          </>
        )}
      </button>

      {/* Switch to Signup */}
      {onSwitchToSignup && (
        <p style={{ textAlign: 'center', fontSize: '0.88rem', color: '#64748b', marginTop: '1.25rem' }}>
          Don't have an account?{' '}
          <button
            type="button"
            onClick={onSwitchToSignup}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--primary)',
              fontWeight: 700,
              cursor: 'pointer',
              textDecoration: 'underline',
              padding: 0,
            }}
          >
            Create an Account
          </button>
        </p>
      )}
    </form>
  );
};
