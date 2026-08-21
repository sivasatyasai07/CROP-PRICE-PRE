import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { X, User, Mail, Phone, MapPin, Globe, CheckCircle2, AlertCircle, Save } from 'lucide-react';

interface UserProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const UserProfileModal: React.FC<UserProfileModalProps> = ({ isOpen, onClose }) => {
  const { user, profile, updateProfile } = useAuth();

  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [state, setState] = useState('');
  const [district, setDistrict] = useState('');
  const [preferredLang, setPreferredLang] = useState('en');

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || '');
      setPhone(profile.phone || '');
      setState(profile.state || '');
      setDistrict(profile.district || '');
      setPreferredLang(profile.preferred_language || 'en');
    } else if (user) {
      setFullName(user.profile?.full_name || user.email.split('@')[0]);
    }
  }, [profile, user, isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !user) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      await updateProfile({
        full_name: fullName.trim() || undefined,
        phone: phone.trim() || undefined,
        state: state.trim() || undefined,
        district: district.trim() || undefined,
        preferred_language: preferredLang,
      });
      setSuccessMsg('Profile updated successfully!');
      setTimeout(() => {
        setSuccessMsg(null);
      }, 2500);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

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
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
          width: '100%',
          maxWidth: '520px',
          maxHeight: '90vh',
          overflowY: 'auto',
          position: 'relative',
          padding: '2rem',
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
          }}
          aria-label="Close modal"
        >
          <X size={22} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: '50%',
              backgroundColor: 'var(--primary)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              fontSize: '1.1rem',
            }}
          >
            <User size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--primary-dark)', margin: 0 }}>
              Farmer Profile
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
              Manage your personal and regional farm details
            </p>
          </div>
        </div>

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

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Email (Read Only) */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.35rem' }}>
              <Mail size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.3rem' }} />
              Registered Email (Account Identity)
            </label>
            <input
              type="email"
              className="form-input"
              value={user.email}
              disabled
              style={{ width: '100%', backgroundColor: '#f1f5f9', color: '#64748b', cursor: 'not-allowed' }}
            />
          </div>

          {/* Full Name */}
          <div>
            <label htmlFor="prof-name" style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.35rem' }}>
              Full Name / Farm Owner
            </label>
            <input
              id="prof-name"
              type="text"
              className="form-input"
              style={{ width: '100%' }}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Ramesh Kumar"
            />
          </div>

          {/* Phone */}
          <div>
            <label htmlFor="prof-phone" style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.35rem' }}>
              <Phone size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.3rem' }} />
              Mobile Phone Number
            </label>
            <input
              id="prof-phone"
              type="tel"
              className="form-input"
              style={{ width: '100%' }}
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+91 9876543210"
            />
          </div>

          {/* State and District */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div>
              <label htmlFor="prof-state" style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.35rem' }}>
                <MapPin size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.3rem' }} />
                State
              </label>
              <input
                id="prof-state"
                type="text"
                className="form-input"
                style={{ width: '100%' }}
                value={state}
                onChange={(e) => setState(e.target.value)}
                placeholder="Andhra Pradesh"
              />
            </div>
            <div>
              <label htmlFor="prof-district" style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.35rem' }}>
                District
              </label>
              <input
                id="prof-district"
                type="text"
                className="form-input"
                style={{ width: '100%' }}
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                placeholder="Chittoor"
              />
            </div>
          </div>

          {/* Preferred Language */}
          <div>
            <label htmlFor="prof-lang" style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-dark)', marginBottom: '0.35rem' }}>
              <Globe size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.3rem' }} />
              Preferred Language
            </label>
            <select
              id="prof-lang"
              className="form-input"
              style={{ width: '100%', cursor: 'pointer' }}
              value={preferredLang}
              onChange={(e) => setPreferredLang(e.target.value)}
            >
              <option value="en">English</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="ml">മലയാളം (Malayalam)</option>
              <option value="ta">தமிழ் (Tamil)</option>
            </select>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
            <button
              type="button"
              onClick={onClose}
              className="btn btn-outline"
              style={{ flex: 1, padding: '0.75rem', fontWeight: 700 }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={saving}
              style={{ flex: 2, padding: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
            >
              {saving ? (
                <span>Saving...</span>
              ) : (
                <>
                  <Save size={18} />
                  <span>Save Profile</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
