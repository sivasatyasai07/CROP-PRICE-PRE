import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { AuthModal } from './AuthModal';
import { UserProfileModal } from './UserProfileModal';
import { User, LogIn, LogOut, ShieldCheck, ChevronDown, Settings } from 'lucide-react';

export const AuthHeaderButton: React.FC = () => {
  const { user, profile, isAuthenticated, logout } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'login' | 'signup'>('login');
  const [profileModalOpen, setProfileModalOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const openLogin = () => {
    setModalMode('login');
    setModalOpen(true);
  };

  const openSignup = () => {
    setModalMode('signup');
    setModalOpen(true);
  };

  if (!isAuthenticated || !user) {
    return (
      <>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            type="button"
            onClick={openLogin}
            className="btn btn-outline"
            style={{
              padding: '0.4rem 0.85rem',
              fontSize: '0.88rem',
              fontWeight: 700,
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
            aria-label="Log in to account"
          >
            <LogIn size={16} />
            <span>Login</span>
          </button>

          <button
            type="button"
            onClick={openSignup}
            className="btn btn-primary"
            style={{
              padding: '0.4rem 0.85rem',
              fontSize: '0.88rem',
              fontWeight: 700,
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
            aria-label="Create a new account"
          >
            <span>Sign Up</span>
          </button>
        </div>

        <AuthModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          initialMode={modalMode}
        />
      </>
    );
  }

  const displayName = profile?.full_name || user.profile?.full_name || user.email.split('@')[0];
  const displayEmail = user.email.length > 22 ? `${user.email.slice(0, 19)}...` : user.email;

  return (
    <div style={{ position: 'relative' }} ref={menuRef}>
      <button
        type="button"
        onClick={() => setMenuOpen(!menuOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 0.75rem',
          borderRadius: '20px',
          border: '1px solid #e2e8f0',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          cursor: 'pointer',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          fontSize: '0.88rem',
          fontWeight: 600,
          color: 'var(--primary-dark)',
          transition: 'all 0.15s ease',
        }}
        aria-expanded={menuOpen}
        aria-label="User profile menu"
      >
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            backgroundColor: user.role === 'admin' ? '#7c3aed' : 'var(--primary)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.8rem',
            fontWeight: 700,
          }}
        >
          {user.role === 'admin' ? <ShieldCheck size={16} /> : <User size={16} />}
        </div>
        <span style={{ fontWeight: 700, maxWidth: '130px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {displayName}
        </span>
        <ChevronDown size={14} style={{ color: '#64748b' }} />
      </button>

      {/* Dropdown Menu */}
      {menuOpen && (
        <div
          style={{
            position: 'absolute',
            right: 0,
            top: '115%',
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.15)',
            border: '1px solid #e2e8f0',
            width: '240px',
            zIndex: 100,
            padding: '0.5rem',
          }}
        >
          <div
            style={{
              padding: '0.6rem 0.75rem',
              borderBottom: '1px solid #f1f5f9',
              marginBottom: '0.35rem',
            }}
          >
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#64748b' }}>Signed in as</p>
            <p style={{ margin: 0, fontSize: '0.88rem', fontWeight: 800, color: 'var(--primary-dark)', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {displayName}
            </p>
            <p style={{ margin: '0.15rem 0 0 0', fontSize: '0.75rem', color: '#64748b', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {displayEmail}
            </p>
            {profile?.preferred_language && (
              <span
                style={{
                  display: 'inline-block',
                  marginTop: '0.35rem',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  backgroundColor: 'var(--accent-gold-light)',
                  color: '#92400e',
                  padding: '0.1rem 0.4rem',
                  borderRadius: '4px',
                  textTransform: 'uppercase',
                }}
              >
                Lang: {profile.preferred_language}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={() => {
              setMenuOpen(false);
              setProfileModalOpen(true);
            }}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.55rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: 'transparent',
              color: 'var(--primary-dark)',
              fontSize: '0.88rem',
              fontWeight: 600,
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'background 0.15s ease',
            }}
          >
            <Settings size={16} color="var(--primary)" />
            <span>Edit Profile</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setMenuOpen(false);
              logout();
            }}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.55rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: 'transparent',
              color: '#dc2626',
              fontSize: '0.88rem',
              fontWeight: 600,
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'background 0.15s ease',
            }}
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      )}

      {/* Profile Edit Modal */}
      <UserProfileModal
        isOpen={profileModalOpen}
        onClose={() => setProfileModalOpen(false)}
      />
    </div>
  );
};
