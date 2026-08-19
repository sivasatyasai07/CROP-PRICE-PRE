import React, { useState } from 'react';
import type { ReactNode } from 'react';
import { useAuth } from '../../context/AuthContext';
import { AuthModal } from './AuthModal';
import { Lock, LogIn } from 'lucide-react';

interface ProtectedRouteProps {
  children: ReactNode;
  fallbackMessage?: string;
  requireAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallbackMessage = 'Please log in to access this feature.',
  requireAdmin = false,
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);

  if (isLoading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
        <p style={{ fontSize: '0.95rem', fontWeight: 600 }}>Loading authentication state...</p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <div
        style={{
          padding: '3rem 2rem',
          textAlign: 'center',
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
          maxWidth: '480px',
          margin: '2rem auto',
          border: '1px solid #e2e8f0',
        }}
      >
        <div
          style={{
            width: 56,
            height: 56,
            borderRadius: '50%',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            color: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem auto',
          }}
        >
          <Lock size={28} />
        </div>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.5rem' }}>
          Authentication Required
        </h3>
        <p style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '1.5rem' }}>
          {fallbackMessage}
        </p>
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="btn btn-primary"
          style={{
            padding: '0.65rem 1.5rem',
            fontSize: '0.95rem',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <LogIn size={18} />
          <span>Log In / Sign Up</span>
        </button>

        <AuthModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          initialMode="login"
        />
      </div>
    );
  }

  if (requireAdmin && user.role !== 'admin') {
    return (
      <div
        style={{
          padding: '3rem 2rem',
          textAlign: 'center',
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
          maxWidth: '480px',
          margin: '2rem auto',
          border: '1px solid #fee2e2',
        }}
      >
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#dc2626', marginBottom: '0.5rem' }}>
          Access Denied
        </h3>
        <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
          Administrator privileges are required to view this panel.
        </p>
      </div>
    );
  }

  return <>{children}</>;
};
