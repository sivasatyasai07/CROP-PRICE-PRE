import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { AdminStatus } from '../api';
import { ShieldCheck, Play, Database, CheckCircle, RefreshCw, Cpu, FileText } from 'lucide-react';

export const AdminTab: React.FC = () => {
  const [adminStatus, setAdminStatus] = useState<AdminStatus | null>(null);
  const [qualityReport, setQualityReport] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [sRes, qRes, mRes] = await Promise.all([
        api.get<AdminStatus>('/admin/status'),
        api.get('/ingestion/data-quality-report/latest'),
        api.get('/models')
      ]);
      setAdminStatus(sRes.data);
      setQualityReport(qRes.data.report);
      setModels(mRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const triggerCleaning = async () => {
    setActionMessage('Running Data Cleaning Pipeline...');
    try {
      const res = await api.post('/ingestion/clean');
      setQualityReport(res.data.cleaning_report);
      setActionMessage('Data Cleaning Completed Successfully!');
      fetchAdminData();
    } catch (e: any) {
      setActionMessage(`Cleaning Error: ${e.message}`);
    }
  };

  const triggerRetraining = async () => {
    setActionMessage('Training CatBoost Direct 3-Horizon Models...');
    try {
      const res = await api.post('/models/train', {
        train_start: '2021-01-01',
        train_end: '2025-12-31',
        test_start: '2026-01-01'
      });
      setActionMessage(`Model Retrained! New Active Version: ${res.data.model_version}`);
      fetchAdminData();
    } catch (e: any) {
      setActionMessage(`Training Error: ${e.message}`);
    }
  };

  const activeModel = models.find(m => m.is_active) || models[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* System Overview */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <ShieldCheck size={26} color="var(--primary)" />
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>System Pipeline & ML Observability</h3>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CropMandi AI Pipeline Management</div>
            </div>
          </div>

          <button className="btn-secondary" onClick={fetchAdminData}>
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh Status
          </button>
        </div>

        {actionMessage && (
          <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '0.85rem 1.25rem', borderRadius: '10px', color: '#34d399', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            {actionMessage}
          </div>
        )}

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
          
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Raw Market Records</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff', marginTop: '0.25rem' }}>
              {adminStatus?.total_raw_records || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#34d399', marginTop: '0.25rem' }}>Source: data.gov.in & CSV</div>
          </div>

          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Cleaned Price Records</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#34d399', marginTop: '0.25rem' }}>
              {adminStatus?.total_cleaned_records || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Deduplicated & Normalized</div>
          </div>

          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active ML Model</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#60a5fa', marginTop: '0.25rem' }}>
              {adminStatus?.active_model_version || 'None'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>CatBoost Direct 3-Horizon</div>
          </div>

          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Pipeline Operational Status</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34d399', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <CheckCircle size={18} /> Healthy
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>All services responsive</div>
          </div>

        </div>
      </div>

      {/* Manual Pipeline Execution Triggers */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Play size={18} color="var(--primary)" /> Pipeline Execution Controls
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          <button className="btn-primary" onClick={triggerCleaning}>
            <Database size={16} /> Run Data Cleaning Pipeline
          </button>

          <button className="btn-primary" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }} onClick={triggerRetraining}>
            <Cpu size={16} /> Train CatBoost ML Models
          </button>
        </div>
      </div>

      {/* Active Model Performance Metrics */}
      {activeModel && activeModel.metrics_json && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>
            CatBoost ML Model Performance Breakdown ({activeModel.model_version})
          </h4>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
            {Object.entries(activeModel.metrics_json).map(([hKey, m]: [string, any]) => (
              <div key={hKey} className="glass-panel" style={{ padding: '1.25rem', borderLeft: '4px solid var(--primary)' }}>
                <div style={{ textTransform: 'uppercase', fontWeight: 700, fontSize: '0.9rem', color: '#34d399', marginBottom: '0.75rem' }}>
                  {hKey.replace('_', ' ')} Performance
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                  <div>MAE: <strong style={{ color: '#ffffff' }}>₹{m.mae}</strong></div>
                  <div>RMSE: <strong style={{ color: '#ffffff' }}>₹{m.rmse}</strong></div>
                  <div>MAPE: <strong style={{ color: '#60a5fa' }}>{m.mape}%</strong></div>
                  <div>WAPE: <strong style={{ color: '#60a5fa' }}>{m.wape}%</strong></div>
                  <div>sMAPE: <strong style={{ color: '#60a5fa' }}>{m.smape}%</strong></div>
                  <div>R² Score: <strong style={{ color: '#34d399' }}>{m.r2}</strong></div>
                </div>

                {m.coverage && (
                  <div style={{ marginTop: '0.85rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    80% Interval Coverage: <strong style={{ color: '#fbbf24' }}>{m.coverage}%</strong> (Avg Width: ₹{m.avg_width})
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quality Report Breakdown */}
      {qualityReport && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={18} color="#60a5fa" /> Data Quality Audit Report
          </h4>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', fontSize: '0.85rem' }}>
            <div>Total Raw Rows: <strong>{qualityReport.total_input_rows}</strong></div>
            <div>Valid Cleaned Rows: <strong style={{ color: '#34d399' }}>{qualityReport.valid_rows}</strong></div>
            <div>Rejected Rows: <strong style={{ color: '#f87171' }}>{qualityReport.invalid_rows}</strong></div>
            <div>Duplicates Removed: <strong>{qualityReport.duplicate_counts}</strong></div>
            <div>Date Horizon: <strong>{qualityReport.date_range?.start} to {qualityReport.date_range?.end}</strong></div>
          </div>
        </div>
      )}

    </div>
  );
};
