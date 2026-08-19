import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { RecommendationResponse, Commodity } from '../api';
import { Compass, Calculator, MapPin, Award, Info } from 'lucide-react';

import type { Language } from '../i18n/translations';
import { getLocalizedCommodityName, getLocalizedMarketName } from '../utils/i18nData';

interface Props {
  language: Language;
}

export const MarketRecommendationTab: React.FC<Props> = ({ language }) => {
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [selectedCommodity, setSelectedCommodity] = useState<string>('Tomato');
  
  // Cost calculator inputs
  const [quantityQtl, setQuantityQtl] = useState<number | ''>(50);
  const [transportCostPerKm, setTransportCostPerKm] = useState<number | ''>(15);
  const [commissionPct, setCommissionPct] = useState<number | ''>(4);
  const [wastagePct, setWastagePct] = useState<number | ''>(2);
  const [farmerLat] = useState<number>(13.60); // Default Annamayya farmer location
  const [farmerLon] = useState<number>(78.50);

  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchCommodities();
  }, []);

  const fetchCommodities = async () => {
    try {
      const res = await api.get<Commodity[]>('/commodities');
      setCommodities(res.data);
      const initialComm = res.data.length > 0 ? res.data[0].canonical_name : 'Tomato';
      setSelectedCommodity(initialComm);
      fetchRecommendations(initialComm, quantityQtl, transportCostPerKm, commissionPct, wastagePct);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchRecommendations = async (
    comm: string,
    qtl: number | '',
    trans: number | '',
    commPct: number | '',
    wastePct: number | ''
  ) => {
    setLoading(true);
    try {
      const res = await api.get<RecommendationResponse>('/recommendations/best-market', {
        params: {
          commodity: comm,
          crop_quantity_qtl: qtl !== '' ? qtl : undefined,
          transport_cost_per_km: trans !== '' ? trans : undefined,
          commission_pct: commPct !== '' ? commPct : undefined,
          wastage_pct: wastePct !== '' ? wastePct : undefined,
          farmer_location_lat: farmerLat,
          farmer_location_lon: farmerLon
        }
      });
      setRecommendations(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRecommendations(selectedCommodity, quantityQtl, transportCostPerKm, commissionPct, wastagePct);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Header & Net Realization Calculator Form */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Compass size={22} color="var(--primary)" />
            {language === 'en' ? 'Mandi Recommendation & Net Realization Engine' : 'ఉత్తమ మండి సిఫార్సు వ్యవస్థ'}
          </h3>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Compare predicted prices and compute your net profit after deducting transport, mandi commission, and transit wastage
          </div>
        </div>

        <form onSubmit={handleCalculate} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem', alignItems: 'end' }}>
          
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Crop Commodity
            </label>
            <select
              className="form-select"
              value={selectedCommodity}
              onChange={(e) => setSelectedCommodity(e.target.value)}
            >
              {commodities.map((c) => <option key={c.id} value={c.canonical_name}>{getLocalizedCommodityName(c.canonical_name, language)}</option>)}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Quantity to Sell (Quintals)
            </label>
            <input
              type="number"
              className="form-input"
              value={quantityQtl}
              onChange={(e) => setQuantityQtl(e.target.value !== '' ? Number(e.target.value) : '')}
              placeholder="e.g. 50"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Transport Cost (₹ / km)
            </label>
            <input
              type="number"
              className="form-input"
              value={transportCostPerKm}
              onChange={(e) => setTransportCostPerKm(e.target.value !== '' ? Number(e.target.value) : '')}
              placeholder="e.g. 15"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Mandi Commission (%)
            </label>
            <input
              type="number"
              className="form-input"
              value={commissionPct}
              onChange={(e) => setCommissionPct(e.target.value !== '' ? Number(e.target.value) : '')}
              placeholder="e.g. 4"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Est. Transit Wastage (%)
            </label>
            <input
              type="number"
              className="form-input"
              value={wastagePct}
              onChange={(e) => setWastagePct(e.target.value !== '' ? Number(e.target.value) : '')}
              placeholder="e.g. 2"
            />
          </div>

          <div>
            <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
              <Calculator size={18} />
              Calculate Best Mandi
            </button>
          </div>

        </form>
      </div>

      {/* Notice Banner */}
      {recommendations && (
        <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: '12px', padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Info size={18} color="#60a5fa" />
          <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
            <strong>Ranking Mode:</strong> {recommendations.ranking_mode}. <em>{recommendations.notice}</em>
          </span>
        </div>
      )}

      {/* Rankings List */}
      {recommendations && recommendations.markets.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {recommendations.markets.map((m, idx) => {
            const isTop = idx === 0;
            return (
              <div
                key={m.market_id}
                className={isTop ? 'glass-panel-glow' : 'glass-panel'}
                style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '50%',
                      background: isTop ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' : 'rgba(255, 255, 255, 0.08)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 800,
                      fontSize: '1.1rem',
                      color: isTop ? '#ffffff' : 'var(--text-muted)'
                    }}>
                      #{idx + 1}
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <h4 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{getLocalizedMarketName(m.market_name, language)}</h4>
                        {isTop && <span className="badge badge-amber"><Award size={12} /> Recommended Best Mandi</span>}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.2rem' }}>
                        <span>District: {m.district}</span>
                        {m.distance_km && <span>• <MapPin size={12} style={{ display: 'inline' }} /> {m.distance_km} km away</span>}
                      </div>
                    </div>
                  </div>

                  {/* Financial Summary Pill */}
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {m.net_realization ? 'Est. Net Realization' : 'Day 1 Predicted Modal Price'}
                    </div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: isTop ? '#34d399' : '#ffffff' }}>
                      ₹{Math.round(m.net_realization || m.day1_predicted_price)}
                      {m.net_realization ? '' : <span style={{ fontSize: '0.85rem', fontWeight: 400, color: 'var(--text-muted)' }}> / qtl</span>}
                    </div>
                  </div>

                </div>

                {/* Cost Breakdown Accordion Grid */}
                {m.cost_breakdown && (
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem', fontSize: '0.85rem' }}>
                    <div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Gross Sales Revenue</div>
                      <div style={{ fontWeight: 700, color: '#e2e8f0', marginTop: '0.1rem' }}>₹{m.cost_breakdown.gross_revenue}</div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Transport Cost</div>
                      <div style={{ fontWeight: 600, color: '#f87171', marginTop: '0.1rem' }}>-₹{m.cost_breakdown.transport_cost}</div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Mandi Commission</div>
                      <div style={{ fontWeight: 600, color: '#f87171', marginTop: '0.1rem' }}>-₹{m.cost_breakdown.commission_cost}</div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Transit Wastage</div>
                      <div style={{ fontWeight: 600, color: '#f87171', marginTop: '0.1rem' }}>-₹{m.cost_breakdown.wastage_cost}</div>
                    </div>
                    <div>
                      <div style={{ color: '#34d399', fontSize: '0.75rem', fontWeight: 600 }}>Net Take-Home</div>
                      <div style={{ fontWeight: 800, color: '#34d399', marginTop: '0.1rem' }}>₹{m.cost_breakdown.net_realization}</div>
                    </div>
                  </div>
                )}

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
