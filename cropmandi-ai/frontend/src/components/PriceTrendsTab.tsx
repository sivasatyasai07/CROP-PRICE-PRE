import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { PriceHistoryItem, PriceCompareItem, Market, Commodity } from '../api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { TrendingUp, BarChart2, Filter, ArrowRightLeft, CheckCircle } from 'lucide-react';
import type { Language } from '../i18n/translations';
import { getLocalizedCommodityName, getLocalizedMarketName, getLocalizedDistrictName } from '../utils/i18nData';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface Props {
  language: Language;
}

export const PriceTrendsTab: React.FC<Props> = ({ language }) => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);

  const [selectedCommodityId, setSelectedCommodityId] = useState<number>(1);
  const [primaryMarketId, setPrimaryMarketId] = useState<number>(1);
  const [compareMarketId, setCompareMarketId] = useState<number | null>(null);

  const [primaryHistory, setPrimaryHistory] = useState<PriceHistoryItem[]>([]);
  const [compareHistory, setCompareHistory] = useState<PriceHistoryItem[]>([]);
  
  const [comparisons, setComparisons] = useState<PriceCompareItem[]>([]);
  const [_loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    loadMetaData();
  }, []);

const FALLBACK_COMMODITIES: Commodity[] = [
  { id: 1, canonical_name: 'Tomato', commodity_group: 'Vegetables', unit: 'Rs./Quintal' },
  { id: 2, canonical_name: 'Onion', commodity_group: 'Vegetables', unit: 'Rs./Quintal' },
  { id: 3, canonical_name: 'Potato', commodity_group: 'Vegetables', unit: 'Rs./Quintal' },
  { id: 4, canonical_name: 'Green Chilli', commodity_group: 'Vegetables', unit: 'Rs./Quintal' },
  { id: 5, canonical_name: 'Lemon', commodity_group: 'Fruits', unit: 'Rs./Quintal' },
  { id: 6, canonical_name: 'Paddy', commodity_group: 'Cereals', unit: 'Rs./Quintal' },
  { id: 7, canonical_name: 'Maize', commodity_group: 'Cereals', unit: 'Rs./Quintal' },
  { id: 8, canonical_name: 'Groundnut', commodity_group: 'Oilseeds', unit: 'Rs./Quintal' },
];

const FALLBACK_MARKETS: Market[] = [
  { id: 1, canonical_name: 'Madanapalle APMC', original_name: 'Madanapalle', district: 'Annamayya', state: 'Andhra Pradesh', latitude: 13.55, longitude: 78.50, is_active: true },
  { id: 2, canonical_name: 'Kurnool APMC', original_name: 'Kurnool', district: 'Kurnool', state: 'Andhra Pradesh', latitude: 15.8281, longitude: 78.0373, is_active: true },
  { id: 3, canonical_name: 'Tenali APMC', original_name: 'Tenali', district: 'Guntur', state: 'Andhra Pradesh', latitude: 16.2430, longitude: 80.6400, is_active: true },
  { id: 4, canonical_name: 'Rajahmundry APMC', original_name: 'Rajahmundry', district: 'East Godavari', state: 'Andhra Pradesh', latitude: 17.0005, longitude: 81.8040, is_active: true },
  { id: 5, canonical_name: 'Ananthapur APMC', original_name: 'Ananthapur', district: 'Anantapur', state: 'Andhra Pradesh', latitude: 14.6819, longitude: 77.6006, is_active: true },
  { id: 6, canonical_name: 'Pattikonda APMC', original_name: 'Pattikonda', district: 'Kurnool', state: 'Andhra Pradesh', latitude: 15.40, longitude: 77.5167, is_active: true },
];

  const loadMetaData = async () => {
    try {
      const cRes = await api.get<Commodity[]>('/commodities');
      let commList = cRes.data;
      if (!commList || commList.length === 0) {
        commList = FALLBACK_COMMODITIES;
      }
      setCommodities(commList);
      if (commList.length > 0) {
        const firstCommId = commList[0].id;
        setSelectedCommodityId(firstCommId);
        await handleCommodityChange(firstCommId);
      }
    } catch (e) {
      console.error(e);
      setCommodities(FALLBACK_COMMODITIES);
      setSelectedCommodityId(FALLBACK_COMMODITIES[0].id);
      await handleCommodityChange(FALLBACK_COMMODITIES[0].id);
    }
  };

  const handleCommodityChange = async (cId: number) => {
    setSelectedCommodityId(cId);
    try {
      const mRes = await api.get<Market[]>('/markets', { params: { commodity_id: cId } });
      let availableMarkets = mRes.data;
      if (!availableMarkets || availableMarkets.length === 0) {
        availableMarkets = FALLBACK_MARKETS;
      }
      setMarkets(availableMarkets);

      if (availableMarkets.length > 0) {
        const m1 = availableMarkets[0];
        setPrimaryMarketId(m1.id);
        const m2 = availableMarkets.length > 1 ? availableMarkets[1].id : null;
        setCompareMarketId(m2);
        fetchMarketData(m1.id, m2, cId);
      }
    } catch (e) {
      console.error(e);
      setMarkets(FALLBACK_MARKETS);
      const m1 = FALLBACK_MARKETS[0];
      setPrimaryMarketId(m1.id);
      setCompareMarketId(FALLBACK_MARKETS[1].id);
      fetchMarketData(m1.id, FALLBACK_MARKETS[1].id, cId);
    }
  };

  const fetchMarketData = async (
    m1Id: number,
    m2Id: number | null,
    cId: number
  ) => {
    setLoading(true);
    try {
      const promises: Promise<any>[] = [
        api.get<PriceHistoryItem[]>('/prices/history', { params: { market_id: m1Id, commodity_id: cId, limit: 10 } }),
        api.get<PriceCompareItem[]>('/prices/compare', { params: { commodity_id: cId } })
      ];

      if (m2Id) {
        promises.push(api.get<PriceHistoryItem[]>('/prices/history', { params: { market_id: m2Id, commodity_id: cId, limit: 10 } }));
      }

      const results = await Promise.all(promises);

      setPrimaryHistory(results[0].data);
      setComparisons(results[1].data);

      if (m2Id && results.length > 2) {
        setCompareHistory(results[2].data);
      } else {
        setCompareHistory([]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handlePrimaryMarketChange = (mId: number) => {
    setPrimaryMarketId(mId);
    fetchMarketData(mId, compareMarketId, selectedCommodityId);
  };

  const handleCompareMarketChange = (mIdStr: string) => {
    const mId = mIdStr ? Number(mIdStr) : null;
    setCompareMarketId(mId);
    fetchMarketData(primaryMarketId, mId, selectedCommodityId);
  };

  const p1Name = markets.find(m => m.id === primaryMarketId)?.canonical_name || 'Market 1';
  const p2Name = compareMarketId ? (markets.find(m => m.id === compareMarketId)?.canonical_name || 'Market 2') : null;

  const dates1 = (primaryHistory || []).map(h => h.observation_date);
  const dates2 = (compareHistory || []).map(h => h.observation_date);

  const allDatesSet = Array.from(new Set([...dates1, ...dates2])).sort();

  const p1Map = new Map(primaryHistory.map(h => [h.observation_date, h.modal_price]));
  const p2Map = new Map(compareHistory.map(h => [h.observation_date, h.modal_price]));

  const chartData1 = allDatesSet.map(d => p1Map.get(d) ?? null);
  const chartData2 = allDatesSet.map(d => p2Map.get(d) ?? null);

  const lineChartData = {
    labels: allDatesSet,
    datasets: [
      {
        label: `${getLocalizedMarketName(p1Name, language)} (Last 10 Days ₹/qtl)`,
        data: chartData1,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.15)',
        tension: 0.3,
        fill: false,
        pointRadius: 5,
        borderWidth: 3,
      },
      ...(p2Name ? [{
        label: `${getLocalizedMarketName(p2Name, language)} (Last 10 Days ₹/qtl)`,
        data: chartData2,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.15)',
        tension: 0.3,
        fill: false,
        pointRadius: 5,
        borderWidth: 3,
      }] : [])
    ]
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: '#475569', font: { family: 'Plus Jakarta Sans', weight: 700, size: 12 } }
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
        ticks: { color: '#64748b' }
      },
      y: {
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
        ticks: { color: '#64748b' },
        title: { display: true, text: 'Original Modal Price (₹ per quintal)', color: '#475569', font: { weight: 700 } }
      }
    }
  };

  const barChartData = {
    labels: comparisons.map(c => getLocalizedMarketName(c.market_name, language)),
    datasets: [
      {
        label: 'Original Modal Price (₹/qtl)',
        data: comparisons.map(c => c.latest_modal_price),
        backgroundColor: comparisons.map(c => 
          c.market_id === primaryMarketId ? '#10b981' : 
          c.market_id === compareMarketId ? '#3b82f6' : 'rgba(16, 185, 129, 0.5)'
        ),
        borderRadius: 6,
      }
    ]
  };

  const m1LatestPrice = primaryHistory.length > 0 ? primaryHistory[primaryHistory.length - 1].modal_price : 0;
  const m2LatestPrice = compareHistory.length > 0 ? compareHistory[compareHistory.length - 1].modal_price : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Selector Control Panel */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', fontWeight: 700 }}>
          <Filter size={18} />
          <span>Market Comparison Filters:</span>
        </div>

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', flex: 1 }}>
          {/* Select Commodity */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>Crop / Commodity</label>
            <select
              className="form-select"
              style={{ minWidth: '200px' }}
              value={selectedCommodityId}
              onChange={(e) => handleCommodityChange(Number(e.target.value))}
            >
              {commodities.map(c => (
                <option key={c.id} value={c.id}>
                  {getLocalizedCommodityName(c.canonical_name, language)}
                </option>
              ))}
            </select>
          </div>

          {/* Primary Market */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#059669' }}>Primary Market (Market 1)</label>
            <select
              className="form-select"
              style={{ minWidth: '220px', borderColor: '#10b981' }}
              value={primaryMarketId}
              onChange={(e) => handlePrimaryMarketChange(Number(e.target.value))}
              disabled={markets.length === 0}
            >
              {markets.length === 0 ? (
                <option value="">No markets available</option>
              ) : (
                markets.map(m => (
                  <option key={m.id} value={m.id}>
                    {getLocalizedMarketName(m.canonical_name, language)} ({getLocalizedDistrictName(m.district, language)})
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Compare Market */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563eb' }}>Compare Market (Market 2)</label>
            <select
              className="form-select"
              style={{ minWidth: '220px', borderColor: '#3b82f6' }}
              value={compareMarketId || ''}
              onChange={(e) => handleCompareMarketChange(e.target.value)}
              disabled={markets.length < 2}
            >
              <option value="">-- None (Single Market) --</option>
              {markets
                .filter(m => m.id !== primaryMarketId)
                .map(m => (
                  <option key={m.id} value={m.id}>
                    {getLocalizedMarketName(m.canonical_name, language)} ({getLocalizedDistrictName(m.district, language)})
                  </option>
                ))}
            </select>
          </div>

        </div>
      </div>

      {/* Comparison Summary Card (If 2 markets selected) */}
      {compareMarketId && (
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <ArrowRightLeft size={24} color="#2563eb" />
            <div>
              <h4 style={{ margin: 0, fontWeight: 800, fontSize: '1rem', color: 'var(--primary-dark)' }}>
                {getLocalizedMarketName(p1Name, language)} vs {getLocalizedMarketName(p2Name || '', language)}
              </h4>
              <p style={{ margin: '0.1rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Direct Mandi Price comparison for {getLocalizedCommodityName(commodities.find(c => c.id === selectedCommodityId)?.canonical_name || '', language)}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 700, display: 'block' }}>{getLocalizedMarketName(p1Name, language)}</span>
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--primary-dark)' }}>₹{m1LatestPrice} / qtl</span>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: '#2563eb', fontWeight: 700, display: 'block' }}>{getLocalizedMarketName(p2Name || '', language)}</span>
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--primary-dark)' }}>₹{m2LatestPrice} / qtl</span>
            </div>

            <div style={{ borderLeft: '2px solid #cbd5e1', paddingLeft: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, display: 'block' }}>Higher Price Mandi</span>
              <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#059669', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <CheckCircle size={16} />
                {m1LatestPrice >= m2LatestPrice ? getLocalizedMarketName(p1Name, language) : getLocalizedMarketName(p2Name || '', language)} (+₹{Math.abs(m1LatestPrice - m2LatestPrice)}/qtl)
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Historical 10-Day Comparison Chart */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp size={20} color="var(--primary)" />
              Original 10-Day Market Price Trend Comparison
            </h3>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Actual recorded APMC prices for the last 10 days (Daily API Data Updates)
            </div>
          </div>
        </div>

        <div style={{ height: '360px', width: '100%' }}>
          <Line data={lineChartData} options={lineOptions} />
        </div>
      </div>

      {/* Cross Market Comparison Grid */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart2 size={20} color="#60a5fa" />
            Cross-Mandi Price Overview across all available mandis
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          
          <div style={{ height: '280px' }}>
            <Bar data={barChartData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#64748b', font: { size: 10 } } }, y: { ticks: { color: '#64748b' } } } }} />
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.6rem' }}>Mandi Market</th>
                  <th style={{ padding: '0.6rem' }}>District</th>
                  <th style={{ padding: '0.6rem' }}>Modal Price</th>
                  <th style={{ padding: '0.6rem' }}>Arrivals</th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((c) => (
                  <tr
                    key={c.market_id}
                    style={{
                      borderBottom: '1px solid rgba(0, 0, 0, 0.04)',
                      backgroundColor: c.market_id === primaryMarketId ? 'rgba(16, 185, 129, 0.08)' : c.market_id === compareMarketId ? 'rgba(59, 130, 246, 0.08)' : 'transparent'
                    }}
                  >
                    <td style={{ padding: '0.65rem', fontWeight: 700 }}>
                      {getLocalizedMarketName(c.market_name, language)}
                      {c.market_id === primaryMarketId && <span style={{ marginLeft: '0.4rem', fontSize: '0.7rem', color: '#059669', fontWeight: 800 }}>(M1)</span>}
                      {c.market_id === compareMarketId && <span style={{ marginLeft: '0.4rem', fontSize: '0.7rem', color: '#2563eb', fontWeight: 800 }}>(M2)</span>}
                    </td>
                    <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{getLocalizedDistrictName(c.district, language)}</td>
                    <td style={{ padding: '0.65rem', fontWeight: 700, color: 'var(--primary)' }}>₹{c.latest_modal_price}</td>
                    <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{c.arrival_quantity ? `${c.arrival_quantity} qtl` : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      </div>

    </div>
  );
};
