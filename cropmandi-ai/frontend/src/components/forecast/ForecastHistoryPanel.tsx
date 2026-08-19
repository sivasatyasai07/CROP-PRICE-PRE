import React, { useEffect, useState } from 'react';
import { History, Clock, CheckCircle, RefreshCw } from 'lucide-react';
import type { ForecastHistoryItem } from '../../services/forecastService';
import { fetchForecastHistory } from '../../services/forecastService';
import { formatKolkataDate } from '../../utils/timezone';
import { getLocalizedCommodityName, getLocalizedMarketName } from '../../utils/i18nData';
import type { Language } from '../../i18n/translations';

interface ForecastHistoryPanelProps {
  commodity: string;
  market: string;
  language?: Language;
}

export const ForecastHistoryPanel: React.FC<ForecastHistoryPanelProps> = ({
  commodity,
  market,
  language = 'en'
}) => {
  const [history, setHistory] = useState<ForecastHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const loadHistory = async () => {
    if (!commodity || !market) return;
    setLoading(true);
    try {
      const items = await fetchForecastHistory(commodity, market, undefined, 25);
      setHistory(items);
    } catch (e) {
      console.error('Failed to load forecast history', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [commodity, market, isOpen]);

  const getStatusBadge = (status: string, supersededOfficial?: boolean) => {
    if (supersededOfficial || status === 'superseded_by_official') {
      return (
        <span style={{
          fontSize: '0.72rem',
          fontWeight: 700,
          padding: '0.2rem 0.5rem',
          borderRadius: '9999px',
          background: '#dcfce7',
          color: '#166534',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.25rem'
        }}>
          <CheckCircle size={11} /> {language === 'te' ? 'అధికారిక డేటా ద్వారా భర్తీ చేయబడింది' : 'Superseded by Official'}
        </span>
      );
    }
    if (status === 'active') {
      return (
        <span style={{
          fontSize: '0.72rem',
          fontWeight: 700,
          padding: '0.2rem 0.5rem',
          borderRadius: '9999px',
          background: '#eff6ff',
          color: '#1d4ed8',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.25rem'
        }}>
          <Clock size={11} /> {language === 'te' ? 'ప్రస్తుత క్రియాశీల అంచనా' : 'Active Forecast'}
        </span>
      );
    }
    return (
      <span style={{
        fontSize: '0.72rem',
        fontWeight: 600,
        padding: '0.2rem 0.5rem',
        borderRadius: '9999px',
        background: '#f1f5f9',
        color: '#64748b'
      }}>
        {language === 'te' ? 'కొత్త అంచనా ద్వారా భర్తీ చేయబడింది' : 'Superseded by Newer'}
      </span>
    );
  };

  return (
    <div style={{
      marginTop: '1.25rem',
      background: '#ffffff',
      borderRadius: '1rem',
      border: '1px solid #e2e8f0',
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      overflow: 'hidden'
    }}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: '0.85rem 1.25rem',
          background: '#f8fafc',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          borderBottom: isOpen ? '1px solid #e2e8f0' : 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <History size={18} color="#0284c7" />
          <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#0f172a' }}>
            {language === 'te' ? 'అంచనాల చరిత్ర మరియు వెర్షన్ ట్రాకింగ్' : (language === 'hi' ? 'पूर्वानुमान इतिहास और संस्करण ट्रैकिंग' : 'Forecast Version History & Audit Log')}
          </span>
          <span style={{ fontSize: '0.75rem', background: '#e0f2fe', color: '#0369a1', padding: '0.15rem 0.5rem', borderRadius: '0.375rem', fontWeight: 600 }}>
            {getLocalizedCommodityName(commodity, language)} • {getLocalizedMarketName(market, language)}
          </span>
        </div>
        <button
          type="button"
          style={{
            background: 'none',
            border: 'none',
            color: '#0284c7',
            fontSize: '0.82rem',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          {isOpen ? (language === 'te' ? 'దాచు' : 'Hide History') : (language === 'te' ? 'చూపించు' : 'View History')}
        </button>
      </div>

      {isOpen && (
        <div style={{ padding: '1rem 1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#64748b' }}>
              {language === 'te' 
                ? 'వివిధ బేస్ తేదీల నుండి రూపొందించబడిన గత అంచనాల వివరాలు. కొత్త సమాచారం వచ్చినప్పుడు మునుపటి అంచనా చరిత్రలో భద్రపరచబడుతుంది.'
                : 'Complete version history of forecasts generated from different base dates. Prior predictions are preserved in history when new data becomes available.'}
            </p>
            <button
              onClick={loadHistory}
              disabled={loading}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.3rem',
                padding: '0.3rem 0.65rem',
                background: '#f1f5f9',
                border: '1px solid #cbd5e1',
                borderRadius: '0.375rem',
                fontSize: '0.75rem',
                color: '#334155',
                cursor: 'pointer'
              }}
            >
              <RefreshCw size={12} className={loading ? 'animate-spin' : ''} /> {language === 'te' ? 'రిఫ్రెష్' : 'Refresh'}
            </button>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b', fontSize: '0.85rem' }}>
              Loading forecast history...
            </div>
          ) : history.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '1.5rem', color: '#94a3b8', fontSize: '0.85rem' }}>
              {language === 'te' ? 'ఈ మార్కెట్ కోసం గత అంచనాలు ఏవీ నమోదు కాలేదు.' : 'No forecast versions recorded yet for this pair.'}
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0', color: '#475569' }}>
                    <th style={{ padding: '0.6rem 0.75rem' }}>{language === 'te' ? 'లక్ష్య తేదీ' : 'Target Date'}</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>{language === 'te' ? 'అంచనా వేసిన ధర' : 'Predicted Price'}</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>{language === 'te' ? 'అంచనా మూల తేదీ' : 'Forecast Origin'}</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>{language === 'te' ? 'పరిధి' : 'Confidence Band'}</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>{language === 'te' ? 'మోడల్' : 'Model'}</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>{language === 'te' ? 'స్థితి' : 'Status'}</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={`history-${item.id}-${item.target_date}-${item.forecast_origin_date}`} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 700, color: '#0f172a' }}>
                        {formatKolkataDate(item.target_date)}
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 800, color: '#16a34a' }}>
                        ₹{item.predicted_modal_price.toLocaleString('en-IN')}
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', color: '#475569' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                          <Clock size={12} color="#64748b" /> {formatKolkataDate(item.forecast_origin_date)}
                        </span>
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', color: '#64748b' }}>
                        ₹{item.lower_bound} - ₹{item.upper_bound}
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', color: '#64748b', fontSize: '0.72rem' }}>
                        {item.model_version || 'catboost-v2'}
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>
                        {getStatusBadge(item.prediction_status, item.superseded_by_official)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
