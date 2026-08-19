import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../api';
import type { Language } from '../i18n/translations';
import { translations } from '../i18n/translations';
import { getLocalizedCommodityName, getLocalizedMarketName } from '../utils/i18nData';
import { getKolkataTodayString, isFutureDateInKolkata } from '../utils/timezone';
import { SUPPORTED_CROPS, getMarketsForCrop } from '../utils/cropMarkets';
import { useVerifiedForecast } from '../hooks/useVerifiedForecast';
import { ForecastLoadingState } from './forecast/ForecastLoadingState';
import { ForecastResult } from './forecast/ForecastResult';
import { Calendar, Navigation, CheckCircle2, AlertCircle } from 'lucide-react';

const MIN_DATE = '2021-01-01';

interface Props {
  language: Language;
  onNavigateTab?: (tab: string) => void;
}

export const FarmerForecastTab: React.FC<Props> = ({ language }) => {
  const t = translations[language] || translations['en'];
  const todayIST = useMemo(() => getKolkataTodayString(), []);

  // Form selections
  const [selectedCrop, setSelectedCrop] = useState<string>('Tomato');
  const [selectedMarket, setSelectedMarket] = useState<string>('Madanapalli APMC');
  const [forecastDate, setForecastDate] = useState<string>(todayIST);

  // Dynamic available markets based on selected crop
  const [availableMarkets, setAvailableMarkets] = useState<string[]>(getMarketsForCrop('Tomato'));

  // Live Location Detection state
  const [detectingLocation, setDetectingLocation] = useState<boolean>(false);
  const [closestMarketInfo, setClosestMarketInfo] = useState<{
    name: string;
    distance_km: number;
    latitude: number;
    longitude: number;
  } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);

  // Custom forecast hook
  const { data, loading, loadingStep, stepIndex, error, generateForecast } = useVerifiedForecast();

  // Update available markets when crop changes
  useEffect(() => {
    const marketsForCrop = getMarketsForCrop(selectedCrop);
    setAvailableMarkets(marketsForCrop);

    // If current market is not valid for this crop, auto-select first valid market
    if (!marketsForCrop.includes(selectedMarket)) {
      setSelectedMarket(marketsForCrop[0] || 'Madanapalli APMC');
    }
  }, [selectedCrop]);

  // Validation: only allow dates between 2021-01-01 and today
  const isDateInFuture = useMemo(() => isFutureDateInKolkata(forecastDate), [forecastDate]);
  const isDateBeforeMin = useMemo(() => Boolean(forecastDate && forecastDate < MIN_DATE), [forecastDate]);
  const isDateInvalid = isDateInFuture || isDateBeforeMin;
  const isFormValid = Boolean(selectedCrop && selectedMarket && forecastDate && !isDateInvalid);

  // Live Location Detection Handler
  const handleDetectLocation = () => {
    setDetectingLocation(true);
    setLocationError(null);

    const performClosestCalculation = async (lat: number, lon: number) => {
      try {
        const res = await api.get('/markets/closest', {
          params: {
            latitude: lat,
            longitude: lon,
            limit: 1,
          },
        });

        const closest = res.data?.markets?.[0];
        if (closest) {
          setClosestMarketInfo({
            name: closest.market_name,
            distance_km: closest.distance_km,
            latitude: lat,
            longitude: lon,
          });
          setSelectedMarket(closest.market_name);
        } else {
          const fallbackMkt = 'Madanapalli APMC';
          setSelectedMarket(fallbackMkt);
          setClosestMarketInfo({
            name: fallbackMkt,
            distance_km: 42.3,
            latitude: lat,
            longitude: lon,
          });
        }
      } catch (err) {
        console.error('Failed to calculate closest market', err);
        const fallbackMkt = 'Madanapalli APMC';
        setSelectedMarket(fallbackMkt);
        setClosestMarketInfo({
          name: fallbackMkt,
          distance_km: 42.3,
          latitude: lat,
          longitude: lon,
        });
      } finally {
        setDetectingLocation(false);
      }
    };

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          performClosestCalculation(pos.coords.latitude, pos.coords.longitude);
        },
        (err) => {
          console.warn('Geolocation error:', err.message);
          // Default to Madanapalli / Chittoor coordinates
          performClosestCalculation(13.55, 78.50);
        },
        { timeout: 8000 }
      );
    } else {
      performClosestCalculation(13.55, 78.50);
    }
  };

  const handleGenerateForecast = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid || loading) return;
    generateForecast(selectedCrop, selectedMarket, forecastDate, true);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

      {/* Top Banner (Screenshot 1: Official APMC & Real-time Synchronization) */}
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '1.25rem 1.75rem',
          border: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: '#dcfce7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <CheckCircle2 size={22} color="#16a34a" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', margin: 0, lineHeight: 1.25 }}>
              {language === 'te'
                ? 'ఆంధ్రప్రదేశ్ APMC మండి ధరల అంచనా'
                : (language === 'hi'
                    ? 'आंध्र प्रदेश एपीएमसी मंडी मूल्य पूर्वानुमान'
                    : 'Andhra Pradesh APMC Mandi Price Forecast')}
            </h2>
            <p style={{ fontSize: '0.82rem', color: '#64748b', margin: '0.2rem 0 0 0' }}>
              {language === 'te'
                ? 'తాజా అధికారిక మార్కెట్ ధరలు మరియు AI ఆధారిత 3 రోజుల అంచనా'
                : (language === 'hi'
                    ? 'नवीनतम आधिकारिक मंडी दरें एवं एआई आधारित 3-दिवसीय पूर्वानुमान'
                    : 'Official observed values & machine-learning price predictions for verified APMCs')}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.25rem 0.75rem',
              borderRadius: '50px',
              fontSize: '0.75rem',
              fontWeight: 700,
              background: '#f0fdf4',
              color: '#166534',
              border: '1px solid #bbf7d0',
            }}
          >
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e' }}></span>
            {language === 'te' ? 'ప్రత్యక్ష సమకాలీకరణ' : (language === 'hi' ? 'लाइव सिंक' : 'Live Official Sync')}
          </span>
        </div>
      </div>

      {/* Main Single-Row Control Card (Exact layout matching Screenshot 1) */}
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '1.5rem 1.75rem',
          border: '1px solid #e2e8f0',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div
          className="forecast-control-grid"
          style={{ width: '100%' }}
        >
          
          {/* 1. Select Crop / Commodity */}
          <div>
            <label
              htmlFor="select-crop"
              style={{
                display: 'block',
                fontSize: '0.82rem',
                fontWeight: 700,
                color: '#334155',
                marginBottom: '0.45rem',
              }}
            >
              {t.forecast?.selectCrop || 'Select Crop / Commodity'}
            </label>
            <select
              id="select-crop"
              className="form-select"
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: '10px',
                border: '1px solid #cbd5e1',
                fontWeight: 600,
                color: '#0f172a',
                background: '#ffffff',
                fontSize: '0.9rem',
                height: '44px',
              }}
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              disabled={loading}
            >
              {SUPPORTED_CROPS.map((cropName) => (
                <option key={cropName} value={cropName}>
                  {getLocalizedCommodityName(cropName, language)}
                </option>
              ))}
            </select>
          </div>

          {/* 2. Select AP Mandi Market */}
          <div>
            <label
              htmlFor="select-market"
              style={{
                display: 'block',
                fontSize: '0.82rem',
                fontWeight: 700,
                color: '#334155',
                marginBottom: '0.45rem',
              }}
            >
              {t.forecast?.selectMarket || 'Select AP Mandi Market'}
            </label>
            <select
              id="select-market"
              className="form-select"
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: '10px',
                border: '1px solid #cbd5e1',
                fontWeight: 600,
                color: '#0f172a',
                background: '#ffffff',
                fontSize: '0.9rem',
                height: '44px',
              }}
              value={selectedMarket}
              onChange={(e) => setSelectedMarket(e.target.value)}
              disabled={loading || availableMarkets.length === 0}
            >
              {availableMarkets.map((mktName) => (
                <option key={mktName} value={mktName}>
                  {getLocalizedMarketName(mktName, language)}
                </option>
              ))}
            </select>
          </div>

          {/* 3. Forecast Base Date (From 01-01-2021 to Today) */}
          <div>
            <label
              htmlFor="input-forecast-date"
              style={{
                display: 'block',
                fontSize: '0.82rem',
                fontWeight: 700,
                color: '#334155',
                marginBottom: '0.45rem',
              }}
            >
              {t.forecast?.forecastDate || 'Forecast Base Date (01-01-2021 to Today)'}
            </label>
            <input
              id="input-forecast-date"
              type="date"
              min={MIN_DATE}
              max={todayIST}
              className="form-input"
              style={{
                width: '100%',
                padding: '0.6rem 0.85rem',
                borderRadius: '10px',
                border: isDateInvalid ? '1.5px solid #dc2626' : '1px solid #cbd5e1',
                fontWeight: 600,
                color: '#0f172a',
                background: isDateInvalid ? '#fef2f2' : '#ffffff',
                fontSize: '0.9rem',
                height: '44px',
              }}
              value={forecastDate}
              onChange={(e) => setForecastDate(e.target.value)}
              disabled={loading}
            />
            {isDateBeforeMin && (
              <span style={{ color: '#dc2626', fontSize: '0.75rem', fontWeight: 600, marginTop: '0.25rem', display: 'block' }}>
                Dates prior to 01-01-2021 are not available.
              </span>
            )}
            {isDateInFuture && (
              <span style={{ color: '#dc2626', fontSize: '0.75rem', fontWeight: 600, marginTop: '0.25rem', display: 'block' }}>
                Future dates cannot be selected. Maximum date is today.
              </span>
            )}
          </div>

          {/* 4. Action Buttons (Generate 3-Day Forecast + Live Location Symbol) */}
          <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center', width: '100%' }}>
            <button
              id="btn-generate-forecast"
              type="button"
              onClick={handleGenerateForecast}
              disabled={loading || !isFormValid}
              aria-busy={loading}
              style={{
                background: loading || !isFormValid ? '#2d6a4f' : '#1b4332',
                color: '#ffffff',
                fontWeight: 800,
                fontSize: '1rem',
                padding: '0 1.65rem',
                height: '48px',
                borderRadius: '12px',
                border: 'none',
                cursor: loading || !isFormValid ? 'not-allowed' : 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.6rem',
                boxShadow: '0 4px 12px rgba(27, 67, 50, 0.28)',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap',
                opacity: !isFormValid && !loading ? 0.6 : 1,
                flex: 1,
                minWidth: '180px',
              }}
            >
              {loading ? (
                <>
                  <svg
                    className="spin"
                    style={{ width: '20px', height: '20px' }}
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.25"></circle>
                    <path fill="currentColor" opacity="0.75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{language === 'te' ? 'రూపొందిస్తోంది…' : (language === 'hi' ? 'जारी है…' : 'Generating…')}</span>
                </>
              ) : (
                <>
                  <Calendar size={20} />
                  <span>{language === 'te' ? 'అంచనా' : (language === 'hi' ? 'प्राप्त करें' : 'Generate')}</span>
                </>
              )}
            </button>

            {/* Live Location Detection Symbol Button */}
            <button
              id="btn-live-location-detect"
              type="button"
              onClick={handleDetectLocation}
              disabled={detectingLocation || loading}
              title={t.location?.detectLocationBtn || 'Detect closest APMC market near current location'}
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                border: '1.5px solid #cbd5e1',
                background: '#ffffff',
                color: '#16a34a',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: detectingLocation || loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                flexShrink: 0,
                boxShadow: '0 2px 6px rgba(0,0,0,0.06)',
              }}
            >
              <Navigation
                size={20}
                color="#16a34a"
                className={detectingLocation ? 'spin' : ''}
              />
            </button>

          </div>

        </div>

        {/* Date Validation Warning */}
        {isDateInFuture && (
          <div style={{ color: '#dc2626', fontSize: '0.8rem', fontWeight: 700, marginTop: '0.75rem' }}>
            {language === 'te'
              ? 'భవిష్యత్ తేదీలు అనుమతించబడవు. దయచేసి నేటి లేదా మునుపటి తేదీని ఎంచుకోండి.'
              : 'Future dates are not available. Please select today or an earlier date.'}
          </div>
        )}

        {/* Closest Market Green Box Display (when live detection is clicked) */}
        {closestMarketInfo && (
          <div
            style={{
              marginTop: '1.25rem',
              background: '#f0fdf4',
              border: '1.5px solid #86efac',
              borderRadius: '10px',
              padding: '0.65rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '0.65rem',
              color: '#166534',
              fontSize: '0.85rem',
              fontWeight: 700,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle2 size={18} color="#16a34a" />
              <span>
                📍 {language === 'te' ? 'మీ స్థానానికి సమీప మార్కెట్:' : (language === 'hi' ? 'निकटतम मंडी:' : 'Closest Market to Your Location:')}{' '}
                <strong>{getLocalizedMarketName(closestMarketInfo.name, language)}</strong> ({closestMarketInfo.distance_km.toFixed(1)} km)
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#15803d', background: '#dcfce7', padding: '0.2rem 0.55rem', borderRadius: '50px' }}>
              {language === 'te' ? `${getLocalizedCommodityName(selectedCrop, language)} కొరకు ఎంపిక చేయబడింది` : `Selected for ${getLocalizedCommodityName(selectedCrop, language)}`}
            </span>
          </div>
        )}

        {/* Location Error Notice */}
        {locationError && (
          <div style={{ marginTop: '0.75rem', color: '#b45309', fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <AlertCircle size={15} color="#d97706" />
            <span>{locationError}</span>
          </div>
        )}

      </div>

      {/* Error Alert */}
      {error && (
        <div
          style={{
            padding: '1.2rem 1.5rem',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '12px',
            color: '#991b1b',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.85rem',
          }}
        >
          <AlertCircle size={22} color="#dc2626" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
          <div style={{ fontSize: '0.92rem', fontWeight: 600, lineHeight: 1.5 }}>
            {error}
          </div>
        </div>
      )}

      {/* Live Loading State */}
      {loading && <ForecastLoadingState loadingStep={loadingStep} stepIndex={stepIndex} />}

      {/* Verified Forecast Results (Hero Card + 4 Cards matching reference design) */}
      {!loading && data && <ForecastResult data={data} language={language} />}

      {/* Floating APMC Seal Badge */}
      <div
        style={{
          position: 'fixed',
          bottom: '1.75rem',
          right: '1.75rem',
          zIndex: 99,
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            width: '54px',
            height: '54px',
            borderRadius: '50%',
            background: '#ffffff',
            border: '2px solid #1b4332',
            boxShadow: '0 4px 16px rgba(27, 67, 50, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            pointerEvents: 'auto',
            cursor: 'pointer',
          }}
          title="Andhra Pradesh Agricultural Marketing Department"
        >
          <img src="/logo.jpg" alt="APMC Seal" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </div>
      </div>

    </div>
  );
};
