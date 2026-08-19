import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { WeatherObservation, Market } from '../api';
import type { Language } from '../i18n/translations';
import { translations } from '../i18n/translations';
import { getLocalizedMarketName, getLocalizedDistrictName } from '../utils/i18nData';
import { calculateHaversineDistance, reverseGeocode } from '../utils/location';
import { CloudSun, CloudRain, AlertTriangle, RefreshCw, MapPin, Navigation } from 'lucide-react';

interface Props {
  language: Language;
}

interface CurrentLocationWeather {
  city: string;
  state: string;
  latitude: number;
  longitude: number;
  temp: number;
  humidity: number;
  windSpeed: number;
  precipitation: number;
  dailyForecast: Array<{
    date: string;
    maxTemp: number;
    minTemp: number;
    rainSum: number;
    windMax: number;
  }>;
}

export const WeatherTab: React.FC<Props> = ({ language }) => {
  const t = translations[language].weather;
  const locT = translations[language].location;

  const [markets, setMarkets] = useState<Market[]>([]);
  const [selectedMarketId, setSelectedMarketId] = useState<number>(1);
  const [mandiForecast, setMandiForecast] = useState<WeatherObservation[]>([]);
  const [mandiHistory, setMandiHistory] = useState<WeatherObservation[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // User location state
  const [userWeather, setUserWeather] = useState<CurrentLocationWeather | null>(null);
  const [locationLoading, setLocationLoading] = useState<boolean>(false);
  const [, setLocationError] = useState<string | null>(null);

  useEffect(() => {
    loadMarkets();
    detectUserLocationAndFetchWeather();
  }, []);

  const loadMarkets = async () => {
    try {
      const res = await api.get<Market[]>('/markets');
      // Filter ONLY markets with valid geographical coordinates where data is available and fetchable
      const validMarkets = res.data.filter(
        (m) => m.latitude !== null && m.longitude !== null && m.latitude !== undefined && m.longitude !== undefined
      );
      setMarkets(validMarkets);
      if (validMarkets.length > 0) {
        setSelectedMarketId(validMarkets[0].id);
        fetchMandiWeather(validMarkets[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMandiWeather = async (mId: number) => {
    setLoading(true);
    try {
      const [fRes, hRes] = await Promise.all([
        api.get<WeatherObservation[]>('/weather/forecast', { params: { market_id: mId } }),
        api.get<WeatherObservation[]>('/weather/history', { params: { market_id: mId, days: 14 } })
      ]);
      setMandiForecast(fRes.data);
      setMandiHistory(hRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const detectUserLocationAndFetchWeather = () => {
    if (!navigator.geolocation) {
      setLocationError(locT.permissionDenied);
      return;
    }

    setLocationLoading(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        try {
          // Fetch reverse geocoded city name
          const geo = await reverseGeocode(lat, lon);

          // Fetch Open-Meteo Real Live Weather & 7-Day Forecast
          const openMeteoUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_max&timezone=auto`;
          const omRes = await fetch(openMeteoUrl);
          
          if (omRes.ok) {
            const omData = await omRes.json();
            const curr = omData.current_weather;
            const daily = omData.daily;

            const forecastDays = (daily.time || []).map((dateStr: string, idx: number) => ({
              date: dateStr,
              maxTemp: daily.temperature_2m_max?.[idx] ?? 30,
              minTemp: daily.temperature_2m_min?.[idx] ?? 22,
              rainSum: daily.precipitation_sum?.[idx] ?? 0,
              windMax: daily.windspeed_10m_max?.[idx] ?? 10,
            }));

            setUserWeather({
              city: geo.city,
              state: geo.state,
              latitude: lat,
              longitude: lon,
              temp: curr?.temperature ?? 28,
              humidity: daily.relative_humidity_2m_max?.[0] ?? 65,
              windSpeed: curr?.windspeed ?? 12,
              precipitation: daily.precipitation_sum?.[0] ?? 0,
              dailyForecast: forecastDays,
            });

            // Auto-select nearest available AP market if markets exist
            if (markets.length > 0) {
              let nearestId = markets[0].id;
              let minDist = Infinity;
              markets.forEach((m) => {
                if (m.latitude && m.longitude) {
                  const d = calculateHaversineDistance(lat, lon, m.latitude, m.longitude);
                  if (d < minDist) {
                    minDist = d;
                    nearestId = m.id;
                  }
                }
              });
              setSelectedMarketId(nearestId);
              fetchMandiWeather(nearestId);
            }
          }
        } catch (e) {
          console.error(e);
        } finally {
          setLocationLoading(false);
        }
      },
      (err) => {
        console.warn(err);
        setLocationError(locT.permissionDenied);
        setLocationLoading(false);
      }
    );
  };

  const selectedMandi = markets.find((m) => m.id === selectedMarketId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Top Controls & Geolocation Button */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <CloudSun size={28} color="var(--primary)" />
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>{t.title}</h3>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              {t.subtitle}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={detectUserLocationAndFetchWeather}
            className="btn-secondary"
            disabled={locationLoading}
          >
            <Navigation size={16} className={locationLoading ? 'spin' : ''} color="var(--primary)" />
            <span>{locationLoading ? t.detectingLocation : locT.detectLocationBtn}</span>
          </button>

          <select
            className="form-select"
            style={{ maxWidth: '320px' }}
            value={selectedMarketId}
            onChange={(e) => {
              const mId = Number(e.target.value);
              setSelectedMarketId(mId);
              fetchMandiWeather(mId);
            }}
          >
            {markets.map((m) => (
              <option key={m.id} value={m.id}>
                {getLocalizedMarketName(m.canonical_name, language)} ({getLocalizedDistrictName(m.district, language)})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 1. USER CURRENT LOCATION WEATHER BANNER */}
      {userWeather && (
        <div className="glass-panel" style={{ padding: '1.75rem', background: 'linear-gradient(135deg, #ffffff 0%, #fef3c7 100%)', borderLeft: '6px solid var(--accent-gold)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
            <div>
              <span className="badge badge-gold" style={{ marginBottom: '0.4rem' }}>
                <MapPin size={14} />
                {locT.locationDetected}
              </span>
              <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#78350f' }}>
                {userWeather.city}, {userWeather.state} ({userWeather.latitude.toFixed(2)}°N, {userWeather.longitude.toFixed(2)}°E)
              </h3>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <CloudSun size={38} color="#d97706" />
                <div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#78350f' }}>{userWeather.temp}°C</div>
                  <div style={{ fontSize: '0.8rem', color: '#92400e', fontWeight: 600 }}>{t.liveWeather}</div>
                </div>
              </div>
            </div>
          </div>

          {/* User Location 7-Day Mini Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.85rem' }}>
            {userWeather.dailyForecast.slice(0, 7).map((d) => (
              <div key={d.date} style={{ background: 'rgba(255,255,255,0.85)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(217,119,6,0.2)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#78350f' }}>{d.date}</div>
                <div style={{ margin: '0.4rem 0' }}>
                  {d.rainSum > 0 ? <CloudRain size={22} color="#2563eb" /> : <CloudSun size={22} color="#d97706" />}
                </div>
                <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#78350f' }}>{d.maxTemp}° / {d.minTemp}°C</div>
                <div style={{ fontSize: '0.72rem', color: '#92400e', marginTop: '0.2rem' }}>
                  🌧️ {d.rainSum} mm | 💨 {d.windMax} km/h
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 2. SELECTED AP MANDI WEATHER FORECAST */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              {t.mandiLocationWeather}: <span style={{ color: 'var(--primary)' }}>{getLocalizedMarketName(selectedMandi?.canonical_name || '', language)}</span>
            </h3>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Open-Meteo Satellite Weather API • {getLocalizedDistrictName(selectedMandi?.district || '', language)}
            </div>
          </div>

          {loading && <RefreshCw size={20} className="spin" color="var(--primary)" />}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
          {mandiForecast.map((w) => {
            const isExtremeHeat = w.temperature_max && w.temperature_max >= 40;
            const isHeavyRain = w.precipitation && w.precipitation >= 25;

            return (
              <div
                key={w.observation_date}
                className="agricultural-card"
                style={{
                  padding: '1.25rem',
                  border: isExtremeHeat || isHeavyRain ? '2px solid var(--accent-terracotta)' : '1px solid var(--border-color)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--primary-dark)' }}>{w.observation_date}</span>
                  {w.precipitation && w.precipitation > 0 ? <CloudRain size={22} color="#2563eb" /> : <CloudSun size={22} color="#d97706" />}
                </div>

                <div style={{ marginBottom: '0.85rem' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary-dark)' }}>
                    {w.temperature_max ? `${w.temperature_max}°C` : 'N/A'}
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500, marginLeft: '0.4rem' }}>
                      ({w.temperature_min}°C min)
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{t.rain}:</span>
                    <strong style={{ color: 'var(--text-main)' }}>{w.precipitation ?? 0} mm</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{t.humidity}:</span>
                    <strong style={{ color: 'var(--text-main)' }}>{w.humidity ?? 60}%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{t.wind}:</span>
                    <strong style={{ color: 'var(--text-main)' }}>{w.wind_speed ?? 10} km/h</strong>
                  </div>
                </div>

                {(isExtremeHeat || isHeavyRain) && (
                  <div style={{ marginTop: '0.85rem', padding: '0.4rem 0.6rem', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', color: '#991b1b', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <AlertTriangle size={14} color="#dc2626" />
                    <span>{isExtremeHeat ? t.extremeHeatAlert : t.heavyRainAlert}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. HISTORICAL WEATHER LOG */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--primary-dark)' }}>
          {t.historicalWeather} ({t.past14Days})
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                <th style={{ padding: '0.65rem' }}>{t.date}</th>
                <th style={{ padding: '0.65rem' }}>{t.maxTemp}</th>
                <th style={{ padding: '0.65rem' }}>{t.minTemp}</th>
                <th style={{ padding: '0.65rem' }}>{t.rain} (mm)</th>
                <th style={{ padding: '0.65rem' }}>{t.humidity} (%)</th>
                <th style={{ padding: '0.65rem' }}>{t.wind} (km/h)</th>
              </tr>
            </thead>
            <tbody>
              {mandiHistory.map((h) => (
                <tr key={h.observation_date} style={{ borderBottom: '1px solid rgba(45,106,79,0.08)' }}>
                  <td style={{ padding: '0.65rem', fontWeight: 600 }}>{h.observation_date}</td>
                  <td style={{ padding: '0.65rem', color: 'var(--primary-dark)', fontWeight: 700 }}>{h.temperature_max}°C</td>
                  <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{h.temperature_min}°C</td>
                  <td style={{ padding: '0.65rem', color: h.precipitation && h.precipitation > 5 ? '#2563eb' : 'var(--text-main)' }}>{h.precipitation ?? 0} mm</td>
                  <td style={{ padding: '0.65rem' }}>{h.humidity ?? 60}%</td>
                  <td style={{ padding: '0.65rem' }}>{h.wind_speed ?? 10} km/h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
