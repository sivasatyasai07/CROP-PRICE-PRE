import React, { useState, useEffect } from 'react';
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
import { TrendingUp, BarChart2, Filter, ArrowRightLeft, CheckCircle, AlertCircle, Database, Calendar, ShieldCheck } from 'lucide-react';
import type { Language } from '../i18n/translations';
import { getLocalizedCommodityName, getLocalizedMarketName, getLocalizedDistrictName } from '../utils/i18nData';
import {
  fetchRecentCommodities,
  fetchRecentMarkets,
  fetchPriceTrends,
  fetchPriceComparison,
  type RecentCommodity,
  type RecentMarket,
  type TrendPoint,
  type CompareMarketItem,
  type ExcludedMarketItem
} from '../services/forecastService';

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
  const [commodities, setCommodities] = useState<RecentCommodity[]>([]);
  const [selectedCommodity, setSelectedCommodity] = useState<string>('Tomato');
  
  const [markets, setMarkets] = useState<RecentMarket[]>([]);
  const [primaryMarket, setPrimaryMarket] = useState<string>('');
  const [compareMarket, setCompareMarket] = useState<string>('');

  const [primaryTrends, setPrimaryTrends] = useState<TrendPoint[]>([]);
  const [compareTrends, setCompareTrends] = useState<TrendPoint[]>([]);

  const [comparisonMarkets, setComparisonMarkets] = useState<CompareMarketItem[]>([]);
  const [excludedMarkets, setExcludedMarkets] = useState<ExcludedMarketItem[]>([]);
  const [maxAgeDays, setMaxAgeDays] = useState<number>(7);

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load available recent commodities (strictly with >= 1 official record in last 30 days)
  useEffect(() => {
    loadRecentCommodities();
  }, []);

  const loadRecentCommodities = async () => {
    try {
      setLoading(true);
      setError(null);
      const commList = await fetchRecentCommodities(30, 3);
      setCommodities(commList);
      if (commList && commList.length > 0) {
        const initialCrop = commList[0].canonical_name;
        setSelectedCommodity(initialCrop);
        await loadRecentMarketsForCrop(initialCrop);
      }
    } catch (err: any) {
      console.error('Failed to load recent commodities', err);
      setError('Failed to load recent commodities with official records.');
    } finally {
      setLoading(false);
    }
  };

  const loadRecentMarketsForCrop = async (cropName: string) => {
    try {
      setLoading(true);
      const mktList = await fetchRecentMarkets(cropName, 30, 3);
      setMarkets(mktList);

      if (mktList && mktList.length > 0) {
        const m1 = mktList[0].canonical_name;
        const m2 = mktList.length > 1 ? mktList[1].canonical_name : '';
        setPrimaryMarket(m1);
        setCompareMarket(m2);
        await fetchAllData(cropName, m1, m2);
      } else {
        setPrimaryMarket('');
        setCompareMarket('');
        setPrimaryTrends([]);
        setCompareTrends([]);
        setComparisonMarkets([]);
        setExcludedMarkets([]);
      }
    } catch (err: any) {
      console.error('Failed to load recent markets for crop', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllData = async (cropName: string, m1Name: string, m2Name: string) => {
    if (!cropName || !m1Name) return;
    setLoading(true);
    setError(null);
    try {
      const promises: Promise<any>[] = [
        fetchPriceTrends({ commodity: cropName, market: m1Name, days: 30, force_refresh: true }),
        fetchPriceComparison({ commodity: cropName, max_age_days: 7, force_refresh: true })
      ];

      if (m2Name) {
        promises.push(
          fetchPriceTrends({ commodity: cropName, market: m2Name, days: 30, force_refresh: true })
        );
      }

      const results = await Promise.all(promises);
      setPrimaryTrends(results[0] || []);
      
      const compRes = results[1];
      if (compRes) {
        setComparisonMarkets(compRes.markets || []);
        setExcludedMarkets(compRes.excluded_markets || []);
        if (compRes.max_latest_value_age_days) {
          setMaxAgeDays(compRes.max_latest_value_age_days);
        }
      }

      if (m2Name && results[2]) {
        setCompareTrends(results[2] || []);
      } else {
        setCompareTrends([]);
      }
    } catch (err: any) {
      console.error('Error fetching trend/compare data', err);
      setError('Unable to fetch official observed data.');
    } finally {
      setLoading(false);
    }
  };

  const handleCommodityChange = async (cropName: string) => {
    setSelectedCommodity(cropName);
    await loadRecentMarketsForCrop(cropName);
  };

  const handlePrimaryMarketChange = async (m1Name: string) => {
    setPrimaryMarket(m1Name);
    await fetchAllData(selectedCommodity, m1Name, compareMarket);
  };

  const handleCompareMarketChange = async (m2Name: string) => {
    setCompareMarket(m2Name);
    await fetchAllData(selectedCommodity, primaryMarket, m2Name);
  };

  // Build continuous time series across the union of observed dates
  const dates1 = (primaryTrends || []).map(t => t.date);
  const dates2 = (compareTrends || []).map(t => t.date);
  const allDatesSet = Array.from(new Set([...dates1, ...dates2])).sort();

  const p1Map = new Map(primaryTrends.map(t => [t.date, t]));
  const p2Map = new Map(compareTrends.map(t => [t.date, t]));

  const chartData1 = allDatesSet.map(d => p1Map.get(d)?.modal_price ?? null);
  const chartData2 = allDatesSet.map(d => p2Map.get(d)?.modal_price ?? null);

  const formatDateLabel = (dateStr: string) => {
    try {
      const parts = dateStr.split('-');
      if (parts.length === 3) {
        const day = parts[2];
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthIndex = parseInt(parts[1], 10) - 1;
        return `${day} ${monthNames[monthIndex] || parts[1]}`;
      }
    } catch {
      // fallback
    }
    return dateStr;
  };

  const lineChartData = {
    labels: allDatesSet.map(formatDateLabel),
    datasets: [
      {
        label: `${getLocalizedMarketName(primaryMarket, language)} (₹/qtl)`,
        data: chartData1,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.15)',
        tension: 0.25,
        fill: false,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#10b981',
        borderWidth: 2.5,
        spanGaps: true,
      },
      ...(compareMarket ? [{
        label: `${getLocalizedMarketName(compareMarket, language)} (₹/qtl)`,
        data: chartData2,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.15)',
        tension: 0.25,
        fill: false,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#3b82f6',
        borderWidth: 2.5,
        spanGaps: true,
      }] : [])
    ]
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: '#334155', font: { family: 'Plus Jakarta Sans', weight: 700, size: 12 } }
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          title: (items: any) => {
            if (items && items[0]) {
              const idx = items[0].dataIndex;
              return allDatesSet[idx] ? `Observation Date: ${allDatesSet[idx]}` : items[0].label;
            }
            return '';
          },
          label: (context: any) => {
            const val = context.parsed.y;
            if (val === null || val === undefined) return '';
            const isP1 = context.datasetIndex === 0;
            const dateStr = allDatesSet[context.dataIndex];
            const pt = isP1 ? p1Map.get(dateStr) : p2Map.get(dateStr);
            const srcLabel = pt ? pt.source_label : 'Official Data';
            return `${context.dataset.label.split(' (')[0]}: ₹${val.toLocaleString('en-IN')}/qtl [${srcLabel}]`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
        ticks: {
          color: '#64748b',
          maxRotation: 45,
          minRotation: 0,
          autoSkip: true,
          maxTicksLimit: 15,
          font: { size: 11, weight: 600 }
        }
      },
      y: {
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
        ticks: { color: '#64748b' },
        title: { display: true, text: 'Official Modal Price (₹ per quintal)', color: '#475569', font: { weight: 700 } }
      }
    }
  };

  const barChartData = {
    labels: comparisonMarkets.map(c => getLocalizedMarketName(c.market, language)),
    datasets: [
      {
        label: 'Latest Official Modal Price (₹/qtl)',
        data: comparisonMarkets.map(c => c.modal_price),
        backgroundColor: comparisonMarkets.map(c =>
          c.market === primaryMarket ? '#10b981' :
          c.market === compareMarket ? '#3b82f6' : '#94a3b8'
        ),
        borderRadius: 6,
      }
    ]
  };

  const getSourceBadgeClass = (source: string) => {
    if (source === 'official_api') return 'badge-green';
    if (source === 'official_database') return 'badge-blue';
    return 'badge-amber';
  };

  const p1Latest = primaryTrends.length > 0 ? primaryTrends[primaryTrends.length - 1] : null;
  const p2Latest = compareTrends.length > 0 ? compareTrends[compareTrends.length - 1] : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Selector Control Panel */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', fontWeight: 700 }}>
          <Filter size={18} />
          <span>Official Data Filters:</span>
        </div>

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', flex: 1 }}>
          {/* Select Commodity */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>Crop / Commodity</label>
            <select
              className="form-select"
              style={{ minWidth: '200px' }}
              value={selectedCommodity}
              onChange={(e) => handleCommodityChange(e.target.value)}
              disabled={loading || commodities.length === 0}
            >
              {commodities.map(c => (
                <option key={c.canonical_name} value={c.canonical_name}>
                  {getLocalizedCommodityName(c.canonical_name, language)} ({c.record_count} obs)
                </option>
              ))}
            </select>
          </div>

          {/* Primary Market */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#059669' }}>Primary Market</label>
            <select
              className="form-select"
              style={{ minWidth: '240px', borderColor: '#10b981' }}
              value={primaryMarket}
              onChange={(e) => handlePrimaryMarketChange(e.target.value)}
              disabled={loading || markets.length === 0}
            >
              {markets.length === 0 ? (
                <option value="">No markets with recent data</option>
              ) : (
                markets.map(m => (
                  <option key={m.canonical_name} value={m.canonical_name}>
                    {getLocalizedMarketName(m.canonical_name, language)} ({getLocalizedDistrictName(m.district, language)})
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Compare Market */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563eb' }}>Compare Market (Optional)</label>
            <select
              className="form-select"
              style={{ minWidth: '240px', borderColor: '#3b82f6' }}
              value={compareMarket}
              onChange={(e) => handleCompareMarketChange(e.target.value)}
              disabled={loading || markets.length < 2}
            >
              <option value="">-- None (Single Market) --</option>
              {markets
                .filter(m => m.canonical_name !== primaryMarket)
                .map(m => (
                  <option key={m.canonical_name} value={m.canonical_name}>
                    {getLocalizedMarketName(m.canonical_name, language)} ({getLocalizedDistrictName(m.district, language)})
                  </option>
                ))}
            </select>
          </div>

        </div>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid #f87171', borderRadius: '8px', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Comparison Summary Card (If 2 markets selected) */}
      {compareMarket && p1Latest && p2Latest && (
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
                {getLocalizedMarketName(primaryMarket, language)} vs {getLocalizedMarketName(compareMarket, language)}
              </h4>
              <p style={{ margin: '0.1rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Latest Official Mandi Price Comparison for {getLocalizedCommodityName(selectedCommodity, language)}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 700, display: 'block' }}>{getLocalizedMarketName(primaryMarket, language)}</span>
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--primary-dark)' }}>₹{p1Latest.modal_price} / qtl</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>Observed: {p1Latest.date} ({p1Latest.data_age_days}d ago)</span>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: '#2563eb', fontWeight: 700, display: 'block' }}>{getLocalizedMarketName(compareMarket, language)}</span>
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--primary-dark)' }}>₹{p2Latest.modal_price} / qtl</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>Observed: {p2Latest.date} ({p2Latest.data_age_days}d ago)</span>
            </div>

            <div style={{ borderLeft: '2px solid #cbd5e1', paddingLeft: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, display: 'block' }}>Higher Realized Mandi</span>
              <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#059669', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <CheckCircle size={16} />
                {p1Latest.modal_price >= p2Latest.modal_price ? getLocalizedMarketName(primaryMarket, language) : getLocalizedMarketName(compareMarket, language)} (+₹{Math.abs(p1Latest.modal_price - p2Latest.modal_price)}/qtl)
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Historical 30-Day Trends Chart */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
              <TrendingUp size={20} color="var(--primary)" />
              {language === 'te' ? '30 రోజుల మార్కెట్ ధరల ట్రెండ్స్' : 'Historical Price Trends'}
            </h3>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
              Showing official observed mandi prices from the last 30 days.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
            {p1Latest && (
              <span className={`badge ${getSourceBadgeClass(p1Latest.price_source)}`} style={{ fontSize: '0.75rem' }}>
                <Database size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                {p1Latest.source_label} (Latest: {p1Latest.date})
              </span>
            )}
          </div>
        </div>

        {primaryTrends.length < 2 ? (
          <div style={{ height: '240px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px dashed #cbd5e1', color: '#64748b', textAlign: 'center', padding: '1.5rem' }}>
            <Calendar size={32} color="#94a3b8" style={{ marginBottom: '0.5rem' }} />
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>
              Not enough recent official mandi-price data is available to display a trend.
            </span>
            <span style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>
              Only valid observed APMC records from the last 30 days are displayed.
            </span>
          </div>
        ) : (
          <div style={{ height: '360px', width: '100%' }}>
            <Line data={lineChartData} options={lineOptions} />
          </div>
        )}
      </div>

      {/* Cross Market Comparison Grid & Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
              <BarChart2 size={20} color="#60a5fa" />
              Market Comparison Overview
            </h3>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
              Showing only markets with valid official observations within the last {maxAgeDays} days.
            </div>
          </div>

          <span className="badge badge-green" style={{ fontSize: '0.75rem' }}>
            <ShieldCheck size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
            {comparisonMarkets.length} Mandis Qualified (Age ≤ {maxAgeDays}d)
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          
          {/* Bar Chart Overview */}
          <div style={{ height: '300px' }}>
            <Bar
              data={barChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: '#64748b', font: { size: 10 } } },
                  y: { ticks: { color: '#64748b' }, title: { display: true, text: 'Modal Price (₹/qtl)' } }
                }
              }}
            />
          </div>

          {/* Qualified Markets Table */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.6rem' }}>Market</th>
                  <th style={{ padding: '0.6rem' }}>District</th>
                  <th style={{ padding: '0.6rem' }}>Modal Price</th>
                  <th style={{ padding: '0.6rem' }}>Min - Max</th>
                  <th style={{ padding: '0.6rem' }}>Arrivals</th>
                  <th style={{ padding: '0.6rem' }}>Observed Date</th>
                  <th style={{ padding: '0.6rem' }}>Data Age</th>
                  <th style={{ padding: '0.6rem' }}>Source</th>
                </tr>
              </thead>
              <tbody>
                {comparisonMarkets.map((c) => (
                  <tr
                    key={c.market}
                    style={{
                      borderBottom: '1px solid rgba(0, 0, 0, 0.04)',
                      backgroundColor: c.market === primaryMarket ? 'rgba(16, 185, 129, 0.08)' : c.market === compareMarket ? 'rgba(59, 130, 246, 0.08)' : 'transparent'
                    }}
                  >
                    <td style={{ padding: '0.65rem', fontWeight: 700 }}>
                      {getLocalizedMarketName(c.market, language)}
                      {c.market === primaryMarket && <span style={{ marginLeft: '0.4rem', fontSize: '0.7rem', color: '#059669', fontWeight: 800 }}>(M1)</span>}
                      {c.market === compareMarket && <span style={{ marginLeft: '0.4rem', fontSize: '0.7rem', color: '#2563eb', fontWeight: 800 }}>(M2)</span>}
                    </td>
                    <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{getLocalizedDistrictName(c.district, language)}</td>
                    <td style={{ padding: '0.65rem', fontWeight: 700, color: 'var(--primary-dark)' }}>₹{c.modal_price}</td>
                    <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>₹{c.min_price} - ₹{c.max_price}</td>
                    <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{c.arrival_quantity ? `${c.arrival_quantity} qtl` : '—'}</td>
                    <td style={{ padding: '0.65rem', fontWeight: 600 }}>{c.observation_date}</td>
                    <td style={{ padding: '0.65rem', color: c.data_age_days === 0 ? '#059669' : '#64748b' }}>
                      {c.data_age_days === 0 ? 'Today' : `${c.data_age_days}d ago`}
                    </td>
                    <td style={{ padding: '0.65rem' }}>
                      <span className={`badge ${getSourceBadgeClass(c.price_source)}`} style={{ fontSize: '0.7rem' }}>
                        {c.source_label}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>

        {/* Excluded Markets (Stale Data > 7 Days or No Observations) */}
        {excludedMarkets.length > 0 && (
          <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', fontWeight: 700, color: '#64748b' }}>
              Excluded Markets ({excludedMarkets.length} mandis with no observations in the last {maxAgeDays} days):
            </h5>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.8rem', color: '#64748b' }}>
              {excludedMarkets.map(ex => (
                <li key={ex.market} style={{ marginBottom: '0.2rem' }}>
                  <strong>{getLocalizedMarketName(ex.market, language)}</strong>: {ex.reason}
                </li>
              ))}
            </ul>
          </div>
        )}

      </div>

    </div>
  );
};
