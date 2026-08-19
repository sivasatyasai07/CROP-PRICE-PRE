import React, { useState, useEffect } from 'react';
import { api } from '../../api';
import type { ClosestMarketItem, ClosestMarketsResponse, Market } from '../../api';
import type { Language } from '../../i18n/translations';
import { getLocalizedCommodityName, getLocalizedMarketName, getLocalizedDistrictName } from '../../utils/i18nData';
import { MapPin, Navigation, Compass, AlertCircle, CheckCircle2, ChevronRight, BarChart2 } from 'lucide-react';

export interface ClosestMarketsSectionProps {
  selectedCrop: string;
  selectedMarketName: string;
  onSelectMarket: (marketName: string) => void;
  onViewPrices?: (marketName: string) => void;
  language?: Language;
}

export const ClosestMarketsSection: React.FC<ClosestMarketsSectionProps> = ({
  selectedCrop,
  selectedMarketName,
  onSelectMarket,
  onViewPrices,
  language = 'en',
}) => {
  const [userLat, setUserLat] = useState<number | null>(null);
  const [userLon, setUserLon] = useState<number | null>(null);
  const [manualLatStr, setManualLatStr] = useState<string>('');
  const [manualLonStr, setManualLonStr] = useState<string>('');
  const [showManualInput, setShowManualInput] = useState<boolean>(false);

  const [closestMarkets, setClosestMarkets] = useState<ClosestMarketItem[]>([]);
  const [allMarkets, setAllMarkets] = useState<Market[]>([]);
  const [cropAvailableMarkets, setCropAvailableMarkets] = useState<Set<string>>(new Set());

  const [loading, setLoading] = useState<boolean>(false);
  const [permissionDenied, setPermissionDenied] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [locationSource, setLocationSource] = useState<'browser' | 'manual' | null>(null);

  // Load baseline markets and crop availability
  useEffect(() => {
    loadAllMarkets();
  }, []);

  useEffect(() => {
    if (selectedCrop) {
      checkCropAvailability(selectedCrop);
    }
  }, [selectedCrop]);

  const loadAllMarkets = async () => {
    try {
      const res = await api.get<Market[]>('/markets');
      setAllMarkets(res.data || []);
    } catch (e) {
      console.error('Failed to load all markets', e);
    }
  };

  const checkCropAvailability = async (crop: string) => {
    try {
      const res = await api.get<Market[]>('/markets', { params: { commodity_name: crop } });
      const names = new Set((res.data || []).map((m) => m.canonical_name));
      setCropAvailableMarkets(names);
    } catch (e) {
      console.error('Failed to check crop market availability', e);
    }
  };

  const fetchClosest = async (lat: number, lon: number, source: 'browser' | 'manual') => {
    setLoading(true);
    setErrorMessage(null);
    setPermissionDenied(false);

    try {
      const res = await api.get<ClosestMarketsResponse>('/markets/closest', {
        params: { latitude: lat, longitude: lon, limit: 12 },
      });
      setClosestMarkets(res.data.markets || []);
      setUserLat(lat);
      setUserLon(lon);
      setLocationSource(source);
    } catch (e: any) {
      const msg = e.response?.data?.detail || 'Could not calculate closest markets from server.';
      setErrorMessage(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setErrorMessage('Geolocation is not supported by your browser.');
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setPermissionDenied(false);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        setManualLatStr(lat.toFixed(4));
        setManualLonStr(lon.toFixed(4));
        fetchClosest(lat, lon, 'browser');
      },
      (err) => {
        console.warn('Geolocation error:', err.message);
        setLoading(false);
        if (err.code === err.PERMISSION_DENIED) {
          setPermissionDenied(true);
        } else {
          setErrorMessage('Could not determine your GPS location. Please enter coordinates manually.');
        }
      },
      { timeout: 8000 }
    );
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const lat = parseFloat(manualLatStr);
    const lon = parseFloat(manualLonStr);

    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      setErrorMessage('Please enter valid latitude (-90 to 90) and longitude (-180 to 180).');
      return;
    }

    fetchClosest(lat, lon, 'manual');
  };

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        padding: '1.5rem',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
      }}
    >
      {/* Section Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          marginBottom: '1.25rem',
          borderBottom: '1px solid #f1f5f9',
          paddingBottom: '1rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                background: '#dcfce7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Compass size={20} color="#16a34a" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                {language === 'te' ? 'సమీప మండి మార్కెట్లు' : (language === 'hi' ? 'निकटतम एपीएमसी मंडियां' : 'Closest Mandi Markets')}
              </h3>
              <p style={{ fontSize: '0.78rem', color: '#64748b', margin: '0.15rem 0 0 0' }}>
                {language === 'te'
                  ? 'మీ స్థానం ఆధారంగా ఆంధ్రప్రదేశ్ అంతటా ఉన్న అన్ని అధికారిక APMC మార్కెట్ల దూరం లెక్కించబడుతుంది'
                  : 'Calculates great-circle distance to all configured APMC yards irrespective of crop'}
              </p>
            </div>
          </div>
        </div>

        {/* Location Action Buttons */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={handleUseMyLocation}
            disabled={loading}
            style={{
              background: '#16a34a',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              padding: '0.5rem 0.95rem',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              transition: 'background 0.2s ease',
            }}
          >
            <Navigation size={14} className={loading ? 'spin' : ''} />
            <span>{loading ? (language === 'te' ? 'గణన చేస్తోంది…' : 'Locating…') : (language === 'te' ? 'నా స్థానాన్ని గుర్తించు' : 'Use My Location')}</span>
          </button>

          <button
            type="button"
            onClick={() => setShowManualInput(!showManualInput)}
            style={{
              background: '#f1f5f9',
              color: '#334155',
              border: '1px solid #cbd5e1',
              borderRadius: '8px',
              padding: '0.5rem 0.85rem',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <MapPin size={14} color="#64748b" />
            <span>{showManualInput ? (language === 'te' ? 'దాచండి' : 'Hide Manual') : (language === 'te' ? 'కోఆర్డినేట్లు' : 'Manual Coordinates')}</span>
          </button>
        </div>
      </div>

      {/* Manual Input Form */}
      {showManualInput && (
        <form
          onSubmit={handleManualSubmit}
          style={{
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '12px',
            padding: '1rem 1.25rem',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'flex-end',
            gap: '1rem',
            flexWrap: 'wrap',
          }}
        >
          <div style={{ flex: 1, minWidth: '140px' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#475569', marginBottom: '0.25rem' }}>
              Latitude
            </label>
            <input
              type="text"
              placeholder="e.g. 13.5500"
              value={manualLatStr}
              onChange={(e) => setManualLatStr(e.target.value)}
              style={{
                width: '100%',
                padding: '0.45rem 0.65rem',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                fontSize: '0.85rem',
                fontWeight: 600,
              }}
            />
          </div>

          <div style={{ flex: 1, minWidth: '140px' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#475569', marginBottom: '0.25rem' }}>
              Longitude
            </label>
            <input
              type="text"
              placeholder="e.g. 78.5000"
              value={manualLonStr}
              onChange={(e) => setManualLonStr(e.target.value)}
              style={{
                width: '100%',
                padding: '0.45rem 0.65rem',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                fontSize: '0.85rem',
                fontWeight: 600,
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              background: '#0f172a',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              padding: '0.5rem 1rem',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              height: '34px',
            }}
          >
            {language === 'te' ? 'దూరాన్ని లెక్కించండి' : 'Calculate Distance'}
          </button>
        </form>
      )}

      {/* Permission Denied Alert */}
      {permissionDenied && (
        <div
          style={{
            background: '#fffbeb',
            border: '1px solid #fef3c7',
            borderLeft: '4px solid #f59e0b',
            borderRadius: '10px',
            padding: '0.85rem 1rem',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            color: '#92400e',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          <AlertCircle size={18} color="#d97706" style={{ flexShrink: 0 }} />
          <span>{language === 'te' ? 'లొకేషన్ అనుమతి నిరాకరించబడింది. మాన్యువల్ కోఆర్డినేట్లను నమోదు చేయండి.' : 'Location permission was denied. Select a location manually to view the closest markets.'}</span>
        </div>
      )}

      {/* Error Message */}
      {errorMessage && (
        <div
          style={{
            background: '#fef2f2',
            border: '1px solid #fee2e2',
            borderLeft: '4px solid #ef4444',
            borderRadius: '10px',
            padding: '0.85rem 1rem',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            color: '#991b1b',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          <AlertCircle size={18} color="#dc2626" style={{ flexShrink: 0 }} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Active User Location Banner */}
      {userLat !== null && userLon !== null && closestMarkets.length > 0 && (
        <div
          style={{
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '10px',
            padding: '0.6rem 0.95rem',
            marginBottom: '1.25rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '0.8rem',
            color: '#166534',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <CheckCircle2 size={15} color="#16a34a" />
            <span>
              {language === 'te' ? 'కోఆర్డినేట్లు:' : 'Coordinates:'} <strong>{userLat.toFixed(4)}°N, {userLon.toFixed(4)}°E</strong> ({locationSource === 'browser' ? 'Browser GPS' : 'Manual'})
            </span>
          </div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#15803d' }}>
            {closestMarkets.length} {language === 'te' ? 'మార్కెట్లు లెక్కించబడ్డాయి' : 'Mandis Calculated'}
          </span>
        </div>
      )}

      {/* No Location State - Alphabetical Markets Display */}
      {closestMarkets.length === 0 && !loading && (
        <div>
          <div
            style={{
              background: '#f8fafc',
              border: '1px dashed #cbd5e1',
              borderRadius: '12px',
              padding: '1rem',
              textAlign: 'center',
              marginBottom: '1.25rem',
              color: '#64748b',
              fontSize: '0.88rem',
            }}
          >
            <Compass size={24} color="#94a3b8" style={{ display: 'block', margin: '0 auto 0.4rem auto' }} />
            <p style={{ margin: 0, fontWeight: 600 }}>
              {language === 'te' ? 'దూరం ప్రకారం మార్కెట్లను క్రమబద్ధీకరించడానికి మీ స్థానాన్ని ఎనేబుల్ చేయండి.' : 'Enable location to sort markets by distance.'}
            </p>
          </div>

          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.65rem' }}>
            {language === 'te' ? 'అందుబాటులో ఉన్న మార్కెట్లు (అక్షరక్రమం)' : 'Available Configured Markets (Alphabetical)'}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '0.75rem' }}>
            {allMarkets
              .slice()
              .sort((a, b) => a.canonical_name.localeCompare(b.canonical_name))
              .slice(0, 12)
              .map((m) => {
                const isSelected = m.canonical_name === selectedMarketName;
                const hasCrop = cropAvailableMarkets.has(m.canonical_name);

                return (
                  <div
                    key={m.id}
                    style={{
                      background: isSelected ? '#f0fdf4' : '#ffffff',
                      border: isSelected ? '1.5px solid #16a34a' : '1px solid #e2e8f0',
                      borderRadius: '10px',
                      padding: '0.85rem',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      gap: '0.6rem',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#0f172a' }}>
                        {getLocalizedMarketName(m.canonical_name, language)}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {getLocalizedDistrictName(m.district, language)}, {m.state}
                      </div>

                      {!hasCrop && selectedCrop && (
                        <div style={{ marginTop: '0.4rem' }}>
                          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#92400e', background: '#fef3c7', padding: '0.15rem 0.45rem', borderRadius: '4px' }}>
                            {language === 'te' ? 'ఎంచుకున్న పంటకు ధర అందుబాటులో లేదు' : 'Price unavailable for selected crop'}
                          </span>
                        </div>
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.2rem' }}>
                      <button
                        type="button"
                        onClick={() => onSelectMarket(m.canonical_name)}
                        style={{
                          flex: 1,
                          background: isSelected ? '#16a34a' : '#0f172a',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '0.4rem 0.6rem',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        {isSelected ? (language === 'te' ? '✓ ఎంపికైంది' : '✓ Selected') : (language === 'te' ? 'మార్కెట్ ఎంచుకోండి' : 'Select Market')}
                      </button>

                      {onViewPrices && (
                        <button
                          type="button"
                          onClick={() => onViewPrices(m.canonical_name)}
                          style={{
                            background: '#f1f5f9',
                            color: '#334155',
                            border: '1px solid #cbd5e1',
                            borderRadius: '6px',
                            padding: '0.4rem 0.6rem',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}
                          title="View price trends"
                        >
                          <BarChart2 size={13} />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Closest Markets Ranked Grid */}
      {closestMarkets.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
          {closestMarkets.map((m) => {
            const isSelected = m.market_name === selectedMarketName;
            const hasCrop = cropAvailableMarkets.has(m.market_name);

            return (
              <div
                key={m.market_id}
                style={{
                  background: isSelected ? '#f0fdf4' : '#ffffff',
                  border: isSelected ? '2px solid #16a34a' : '1px solid #e2e8f0',
                  borderRadius: '12px',
                  padding: '1rem 1.15rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.85rem',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.03)',
                  transition: 'border 0.2s ease',
                }}
              >
                <div>
                  {/* Top Rank + Distance Header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <span
                      style={{
                        background: m.rank === 1 ? '#dcfce7' : '#f1f5f9',
                        color: m.rank === 1 ? '#15803d' : '#475569',
                        fontSize: '0.72rem',
                        fontWeight: 800,
                        padding: '0.15rem 0.55rem',
                        borderRadius: '50px',
                      }}
                    >
                      #{m.rank} {language === 'te' ? 'సమీపం' : 'Closest'}
                    </span>

                    <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <MapPin size={13} color="#16a34a" />
                      {m.distance_km.toFixed(1)} km
                    </span>
                  </div>

                  {/* Market Details */}
                  <div style={{ fontSize: '0.96rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.3 }}>
                    {getLocalizedMarketName(m.market_name, language)}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.15rem' }}>
                    {getLocalizedDistrictName(m.district, language)}, {m.state}
                  </div>

                  {/* Availability Badge */}
                  <div style={{ marginTop: '0.5rem' }}>
                    {hasCrop ? (
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          background: '#f0fdf4',
                          color: '#166534',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.5rem',
                          borderRadius: '4px',
                          border: '1px solid #bbf7d0',
                        }}
                      >
                        <CheckCircle2 size={11} color="#16a34a" />
                        {language === 'te' ? `${getLocalizedCommodityName(selectedCrop, language)} అందుబాటులో ఉంది` : `${getLocalizedCommodityName(selectedCrop, language)} Available`}
                      </span>
                    ) : (
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          background: '#fef3c7',
                          color: '#92400e',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.5rem',
                          borderRadius: '4px',
                          border: '1px solid #fde68a',
                        }}
                      >
                        <AlertCircle size={11} color="#d97706" />
                        {language === 'te' ? 'ఈ పంటకు ధర రికార్డు లేదు' : 'No price records for selected crop'}
                      </span>
                    )}
                  </div>
                </div>

                {/* Card Actions */}
                <div style={{ display: 'flex', gap: '0.45rem', marginTop: '0.35rem' }}>
                  <button
                    type="button"
                    onClick={() => onSelectMarket(m.market_name)}
                    style={{
                      flex: 1,
                      background: isSelected ? '#16a34a' : '#0f172a',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '0.5rem 0.75rem',
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.35rem',
                      transition: 'background 0.2s ease',
                    }}
                  >
                    {isSelected ? (
                      <>
                        <CheckCircle2 size={13} />
                        <span>{language === 'te' ? 'ఎంపికైంది' : 'Selected'}</span>
                      </>
                    ) : (
                      <>
                        <span>{language === 'te' ? 'ఈ మార్కెట్‌ను ఎంచుకోండి' : 'Select This Market'}</span>
                        <ChevronRight size={13} />
                      </>
                    )}
                  </button>

                  {onViewPrices && (
                    <button
                      type="button"
                      onClick={() => onViewPrices(m.market_name)}
                      style={{
                        background: '#f8fafc',
                        color: '#334155',
                        border: '1px solid #cbd5e1',
                        borderRadius: '8px',
                        padding: '0.5rem 0.65rem',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                      title="View price trends"
                    >
                      <BarChart2 size={14} color="#64748b" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
