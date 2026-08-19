import React from 'react';
import type { Language } from '../i18n/translations';
import { translations } from '../i18n/translations';
import { TrendingUp, Sprout, CloudSun, Globe, Landmark, Sparkles } from 'lucide-react';
import { AuthHeaderButton } from './auth/AuthHeaderButton';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  language: Language;
  setLanguage: (lang: Language) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  language,
  setLanguage,
}) => {
  const t = translations[language];

  const getDiseaseTabLabel = () => {
    switch (language) {
      case 'te': return 'పంట వ్యాధులు';
      case 'hi': return 'फसल रोग';
      case 'ta': return 'பயிர் நோய்';
      case 'ml': return 'വിള രോഗങ്ങൾ';
      default: return 'Crop Disease';
    }
  };

  return (
    <header style={{ borderBottom: '1px solid var(--border-color)', background: '#ffffff', boxShadow: 'var(--shadow-sm)', position: 'sticky', top: 0, zIndex: 100 }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0.85rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Brand Logo & Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <img
            src="/logo.jpg"
            alt="Mandi Price Prediction Logo"
            style={{
              width: '52px',
              height: '52px',
              borderRadius: '50%',
              objectFit: 'cover',
              border: '2px solid var(--primary)',
              boxShadow: 'var(--shadow-sm)'
            }}
          />
          <div>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--primary-dark)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span>{t.appTitle}</span>
              <span className="badge badge-green" style={{ fontSize: '0.7rem' }}>APMC AI</span>
            </h1>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              {t.appSubtitle}
            </div>
          </div>
        </div>

        {/* Right Navigation & 5-Language Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          
          {/* Navigation Tabs */}
          <nav style={{ display: 'flex', gap: '0.4rem', background: 'var(--bg-secondary)', padding: '0.35rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
            {[
              { id: 'forecast', label: t.tabs.forecast, icon: TrendingUp },
              { id: 'trends', label: t.tabs.trends, icon: Sprout },
              { id: 'disease', label: getDiseaseTabLabel(), icon: Sparkles },
              { id: 'weather', label: t.tabs.weather, icon: CloudSun },
              { id: 'schemes', label: t.tabs.schemes, icon: Landmark },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                    padding: '0.55rem 0.95rem',
                    borderRadius: 'var(--radius-sm)',
                    border: 'none',
                    background: isActive ? 'var(--primary)' : 'transparent',
                    color: isActive ? '#ffffff' : 'var(--text-main)',
                    fontWeight: isActive ? 700 : 600,
                    fontSize: '0.88rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <Icon size={16} color={isActive ? '#ffffff' : 'var(--primary)'} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* 5-Language Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--accent-gold-light)', padding: '0.35rem 0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(217,119,6,0.3)' }}>
            <Globe size={16} color="#92400e" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#92400e',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer',
                outline: 'none',
              }}
            >
              <option value="en">English</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="ml">മലയാളം (Malayalam)</option>
              <option value="ta">தமிழ் (Tamil)</option>
            </select>
          </div>

          {/* Top-Right Authentication Controls */}
          <AuthHeaderButton />

        </div>

      </div>
    </header>
  );
};
