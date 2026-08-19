import { useState } from 'react';
import type { Language } from './i18n/translations';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { FarmerForecastTab } from './components/FarmerForecastTab';
import { PriceTrendsTab } from './components/PriceTrendsTab';
import { CropDiseaseTab } from './components/CropDiseaseTab';
import { WeatherTab } from './components/WeatherTab';
import { GovernmentSchemesTab } from './components/GovernmentSchemesTab';
import { MandiMitraChatbot } from './components/MandiMitraChatbot';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('forecast');
  const [language, setLanguage] = useState<Language>('en');

  return (
    <AuthProvider>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        
        {/* Header Bar with Logo & Title */}
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          language={language}
          setLanguage={setLanguage}
        />

        {/* Main Container */}
        <main style={{ flex: 1, maxWidth: '1280px', width: '100%', margin: '0 auto', padding: '2rem 1.5rem' }}>
          {activeTab === 'forecast' && <FarmerForecastTab language={language} onNavigateTab={setActiveTab} />}
          {activeTab === 'trends' && <PriceTrendsTab language={language} />}
          {activeTab === 'disease' && <CropDiseaseTab language={language} />}
          {activeTab === 'weather' && <WeatherTab language={language} />}
          {activeTab === 'schemes' && <GovernmentSchemesTab language={language} />}
        </main>

        {/* Floating Mandi Mitra AI Chatbot */}
        <MandiMitraChatbot language={language} />

        {/* Agricultural Footer */}
        <footer style={{ borderTop: '1px solid var(--border-color)', background: '#ffffff', padding: '1.75rem 1.5rem', marginTop: '3rem' }}>
          <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <img src="/logo.jpg" alt="Logo" style={{ width: '28px', height: '28px', borderRadius: '50%', objectFit: 'cover' }} />
              <span style={{ fontWeight: 700, color: 'var(--primary-dark)' }}>
                Mandi Price Prediction • 3-Day Farmer Mandi Price Forecast & Advisory System
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
              <span>Official APMC Mandi Data Source: data.gov.in</span>
              <span>Open-Meteo Weather API</span>
              <span className="badge badge-green" style={{ fontSize: '0.75rem' }}>
                CatBoost ML v1.0
              </span>
            </div>
          </div>
        </footer>

      </div>
    </AuthProvider>
  );
}

export default App;
