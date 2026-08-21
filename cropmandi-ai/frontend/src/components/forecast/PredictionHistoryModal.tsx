import React, { useState, useEffect } from 'react';
import { predictionHistoryService, type PredictionHistoryRecord } from '../../services/predictionHistoryService';
import { X, TrendingUp, TrendingDown, Minus, Trash2, Calendar, MapPin, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';

const formatPrice = (val?: number | null) => (val != null ? `₹${Number(val).toLocaleString('en-IN')}` : '--');

interface PredictionHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PredictionHistoryModal: React.FC<PredictionHistoryModalProps> = ({ isOpen, onClose }) => {
  const [history, setHistory] = useState<PredictionHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filterCrop, setFilterCrop] = useState<string>('all');

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const records = await predictionHistoryService.fetchHistory(50);
      setHistory(records);
    } catch (err: any) {
      setError(err.message || 'Failed to load prediction history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleDelete = async (id: string) => {
    const success = await predictionHistoryService.deleteRecord(id);
    if (success) {
      setHistory((prev) => prev.filter((item) => item.id !== id));
    }
  };

  const crops = Array.from(new Set(history.map((h) => h.crop)));
  const filteredHistory = filterCrop === 'all' ? history : history.filter((h) => h.crop === filterCrop);

  const renderTrendBadge = (trend: string) => {
    const t = (trend || '').toLowerCase();
    if (t.includes('up')) {
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '50px',
            fontSize: '0.75rem',
            fontWeight: 700,
            backgroundColor: '#dcfce7',
            color: '#15803d',
          }}
        >
          <TrendingUp size={13} />
          <span>Bullish / Rising</span>
        </span>
      );
    }
    if (t.includes('down')) {
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '50px',
            fontSize: '0.75rem',
            fontWeight: 700,
            backgroundColor: '#fee2e2',
            color: '#b91c1c',
          }}
        >
          <TrendingDown size={13} />
          <span>Bearish / Falling</span>
        </span>
      );
    }
    return (
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.3rem',
          padding: '0.2rem 0.55rem',
          borderRadius: '50px',
          fontSize: '0.75rem',
          fontWeight: 700,
          backgroundColor: '#f1f5f9',
          color: '#475569',
        }}
      >
        <Minus size={13} />
        <span>Stable</span>
      </span>
    );
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
          maxWidth: '760px',
          maxHeight: '88vh',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: '1.25rem 1.75rem',
            borderBottom: '1px solid #e2e8f0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)',
            color: '#ffffff',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: '8px',
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <TrendingUp size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800 }}>My Prediction History</h3>
              <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.85 }}>
                Saved APMC forecasts & price trend estimates
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button
              type="button"
              onClick={loadHistory}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                color: '#ffffff',
                borderRadius: '8px',
                padding: '0.4rem 0.65rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 700,
              }}
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
              <span>Refresh</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                color: '#ffffff',
                cursor: 'pointer',
                padding: '0.35rem',
                borderRadius: '50%',
              }}
              aria-label="Close dialog"
            >
              <X size={22} />
            </button>
          </div>
        </div>

        {/* Filter Bar */}
        {crops.length > 1 && (
          <div
            style={{
              padding: '0.65rem 1.75rem',
              backgroundColor: '#f8fafc',
              borderBottom: '1px solid #e2e8f0',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              overflowX: 'auto',
            }}
          >
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#64748b' }}>Filter Crop:</span>
            <button
              type="button"
              onClick={() => setFilterCrop('all')}
              style={{
                padding: '0.25rem 0.65rem',
                borderRadius: '50px',
                border: 'none',
                fontSize: '0.78rem',
                fontWeight: 700,
                cursor: 'pointer',
                background: filterCrop === 'all' ? '#2563eb' : '#e2e8f0',
                color: filterCrop === 'all' ? '#ffffff' : '#475569',
              }}
            >
              All ({history.length})
            </button>
            {crops.map((crop) => (
              <button
                key={crop}
                type="button"
                onClick={() => setFilterCrop(crop)}
                style={{
                  padding: '0.25rem 0.65rem',
                  borderRadius: '50px',
                  border: 'none',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  background: filterCrop === crop ? '#2563eb' : '#e2e8f0',
                  color: filterCrop === crop ? '#ffffff' : '#475569',
                }}
              >
                {crop}
              </button>
            ))}
          </div>
        )}

        {/* Content Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem 1.75rem' }}>
          {error && (
            <div
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                backgroundColor: '#fee2e2',
                color: '#991b1b',
                fontSize: '0.88rem',
                fontWeight: 600,
                marginBottom: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          {loading && history.length === 0 ? (
            <div style={{ padding: '3rem 0', textAlign: 'center', color: '#64748b' }}>
              <RefreshCw size={28} className="animate-spin" style={{ margin: '0 auto 0.75rem auto', color: '#2563eb' }} />
              <p style={{ margin: 0, fontWeight: 600 }}>Loading your prediction history...</p>
            </div>
          ) : filteredHistory.length === 0 ? (
            <div style={{ padding: '3.5rem 1rem', textAlign: 'center', color: '#64748b' }}>
              <Sparkles size={36} style={{ margin: '0 auto 0.75rem auto', color: '#cbd5e1' }} />
              <h4 style={{ margin: '0 0 0.35rem 0', color: '#1e293b', fontWeight: 700 }}>No Predictions Found</h4>
              <p style={{ margin: 0, fontSize: '0.88rem' }}>
                {filterCrop === 'all'
                  ? 'Predictions you run while logged in will automatically appear here.'
                  : `No saved predictions for ${filterCrop}.`}
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {filteredHistory.map((item) => (
                <div
                  key={item.id}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '1rem 1.25rem',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.75rem',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                        <span style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--primary-dark)' }}>
                          {item.crop}
                        </span>
                        {renderTrendBadge(item.trend)}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', color: '#64748b' }}>
                        <MapPin size={13} />
                        <span>{item.market} {item.district ? `(${item.district})` : ''}</span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', color: '#64748b' }}>
                        <Calendar size={13} />
                        <span>{item.prediction_date}</span>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleDelete(item.id)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#94a3b8',
                          cursor: 'pointer',
                          padding: '0.25rem',
                          borderRadius: '4px',
                        }}
                        title="Delete prediction"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>

                  {/* Price Chips */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                      gap: '0.65rem',
                      background: '#f8fafc',
                      padding: '0.65rem 0.85rem',
                      borderRadius: '8px',
                      border: '1px solid #f1f5f9',
                    }}
                  >
                    <div>
                      <span style={{ fontSize: '0.72rem', color: '#64748b', display: 'block', fontWeight: 600 }}>Observed / Base</span>
                      <span style={{ fontSize: '0.95rem', fontWeight: 800, color: '#334155' }}>
                        {formatPrice(item.current_price)}
                      </span>
                    </div>

                    <div>
                      <span style={{ fontSize: '0.72rem', color: '#2563eb', display: 'block', fontWeight: 700 }}>Predicted Modal</span>
                      <span style={{ fontSize: '0.95rem', fontWeight: 800, color: '#1d4ed8' }}>
                        {formatPrice(item.predicted_price)}
                      </span>
                    </div>

                    {item.min_price !== undefined && item.max_price !== undefined && (
                      <div>
                        <span style={{ fontSize: '0.72rem', color: '#64748b', display: 'block', fontWeight: 600 }}>Expected Range</span>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#475569' }}>
                          {formatPrice(item.min_price)} – {formatPrice(item.max_price)}
                        </span>
                      </div>
                    )}

                    <div>
                      <span style={{ fontSize: '0.72rem', color: '#64748b', display: 'block', fontWeight: 600 }}>AI Model</span>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#475569' }}>
                        {item.model_name || 'CatBoost v1.0'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
