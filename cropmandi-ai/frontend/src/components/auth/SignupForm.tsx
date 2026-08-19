import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { PasswordInput } from './PasswordInput';
import { PasswordRequirements } from './PasswordRequirements';
import { UserPlus, AlertCircle, CheckCircle2 } from 'lucide-react';

interface SignupFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onSuccess, onSwitchToLogin }) => {
  const { signup } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const isPasswordValid =
    password.length >= 6 &&
    /[A-Z]/.test(password) &&
    /[^A-Za-z0-9\s]/.test(password) &&
    !/\s/.test(password);

  const isFormReady =
    email.trim().length > 0 &&
    isPasswordValid &&
    confirmPassword.length > 0 &&
    password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setEmailError(null);
    setPasswordError(null);
    setConfirmError(null);
    setSuccessMsg(null);

    let hasError = false;
    const cleanEmail = email.trim().toLowerCase();

    // Email check
    if (!cleanEmail) {
      setEmailError('Email is required.');
      hasError = true;
    } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(cleanEmail)) {
      setEmailError('Enter a valid email address.');
      hasError = true;
    }

    // Password check
    if (!password) {
      setPasswordError('Password is required.');
      hasError = true;
    } else if (password.length < 6) {
      setPasswordError('Password must contain at least 6 characters.');
      hasError = true;
    } else if (!/[A-Z]/.test(password)) {
      setPasswordError('Password must contain at least one capital letter.');
      hasError = true;
    } else if (!/[^A-Za-z0-9\s]/.test(password)) {
      setPasswordError('Password must contain at least one symbol.');
      hasError = true;
    } else if (/\s/.test(password)) {
      setPasswordError('Password must not contain spaces.');
      hasError = true;
    }

    // Confirm password check
    if (!confirmPassword) {
      setConfirmError('Please confirm your password.');
      hasError = true;
    } else if (password !== confirmPassword) {
      setConfirmError('Passwords do not match.');
      hasError = true;
    }

    if (hasError) return;

    setLoading(true);
    try {
      await signup({
        email: cleanEmail,
        password,
        confirm_password: confirmPassword,
      });
      setSuccessMsg('Account created successfully.');
      if (onSuccess) {
        setTimeout(onSuccess, 500);
      }
    } catch (err: any) {
      const responseData = err.response?.data;
      if (responseData?.errors?.email) {
        setEmailError(responseData.errors.email[0]);
      } else if (responseData?.errors?.password) {
        setPasswordError(responseData.errors.password[0]);
      } else if (responseData?.errors?.confirm_password) {
        setConfirmError(responseData.errors.confirm_password[0]);
      } else {
        setErrorMsg(responseData?.detail || 'An account with this email already exists.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate style={{ width: '100%' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.25rem' }}>
        Create CropMandi AI Account
      </h3>
      <p style={{ fontSize: '0.88rem', color: '#64748b', marginBottom: '1.25rem' }}>
        Register to get real-time price predictions & tailored market advice.
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
          htmlFor="signup-email"
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
          id="signup-email"
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
        id="signup-password"
        label="Password"
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          if (passwordError) setPasswordError(null);
        }}
        autocomplete="new-password"
        error={passwordError || undefined}
        required
      />

      {/* Confirm Password Field */}
      <PasswordInput
        id="signup-confirm-password"
        label="Confirm Password"
        value={confirmPassword}
        onChange={(e) => {
          setConfirmPassword(e.target.value);
          if (confirmError) setConfirmError(null);
        }}
        autocomplete="new-password"
        placeholder="Re-enter password"
        error={confirmError || undefined}
        required
      />

      {/* Password Requirements Checklist */}
      <PasswordRequirements
        password={password}
        confirmPassword={confirmPassword}
        showConfirmCheck
      />

      {/* Submit Button */}
      <button
        type="submit"
        className="btn btn-primary"
        disabled={loading || !isFormReady}
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
          opacity: isFormReady && !loading ? 1 : 0.7,
        }}
      >
        {loading ? (
          <span>Creating Account...</span>
        ) : (
          <>
            <UserPlus size={18} />
            <span>Create Account</span>
          </>
        )}
      </button>

      {/* Switch to Login */}
      {onSwitchToLogin && (
        <p style={{ textAlign: 'center', fontSize: '0.88rem', color: '#64748b', marginTop: '1.25rem' }}>
          Already have an account?{' '}
          <button
            type="button"
            onClick={onSwitchToLogin}
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
            Log In
          </button>
        </p>
      )}
    </form>
  );
};
