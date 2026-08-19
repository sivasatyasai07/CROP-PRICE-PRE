import React, { useState, useEffect } from 'react';
import { LoginForm } from './LoginForm';
import { SignupForm } from './SignupForm';
import { X, LogIn, UserPlus } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'signup';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialMode = 'login',
}) => {
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode, isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          width: '100%',
          maxWidth: '460px',
          maxHeight: '90vh',
          overflowY: 'auto',
          position: 'relative',
          padding: '2rem',
          animation: 'fadeInScale 0.25s ease-out',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'none',
            border: 'none',
            color: '#64748b',
            cursor: 'pointer',
            padding: '0.35rem',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background 0.15s ease',
          }}
          aria-label="Close dialog"
        >
          <X size={22} />
        </button>

        {/* Tab Header Toggle */}
        <div
          style={{
            display: 'flex',
            backgroundColor: '#f1f5f9',
            borderRadius: '10px',
            padding: '0.25rem',
            marginBottom: '1.5rem',
            marginTop: '0.5rem',
          }}
        >
          <button
            type="button"
            onClick={() => setMode('login')}
            style={{
              flex: 1,
              padding: '0.6rem 1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: mode === 'login' ? '#ffffff' : 'transparent',
              color: mode === 'login' ? 'var(--primary-dark)' : '#64748b',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: 'pointer',
              boxShadow: mode === 'login' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s ease',
            }}
          >
            <LogIn size={16} />
            <span>Log In</span>
          </button>

          <button
            type="button"
            onClick={() => setMode('signup')}
            style={{
              flex: 1,
              padding: '0.6rem 1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: mode === 'signup' ? '#ffffff' : 'transparent',
              color: mode === 'signup' ? 'var(--primary-dark)' : '#64748b',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: 'pointer',
              boxShadow: mode === 'signup' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s ease',
            }}
          >
            <UserPlus size={16} />
            <span>Sign Up</span>
          </button>
        </div>

        {/* Render Form */}
        {mode === 'login' ? (
          <LoginForm
            onSuccess={onClose}
            onSwitchToSignup={() => setMode('signup')}
          />
        ) : (
          <SignupForm
            onSuccess={onClose}
            onSwitchToLogin={() => setMode('login')}
          />
        )}
      </div>
    </div>
  );
};
