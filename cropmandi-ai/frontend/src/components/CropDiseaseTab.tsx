import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useDiseaseAnalysis } from '../hooks/useDiseaseAnalysis';
import { useDiseaseHistory } from '../hooks/useDiseaseHistory';
import { ImageUploader } from './disease/ImageUploader';
import { DiseaseAnalysisButton } from './disease/DiseaseAnalysisButton';
import { DiseaseLoadingState } from './disease/DiseaseLoadingState';
import { DiseaseResultCard } from './disease/DiseaseResultCard';
import { DiseaseHistoryList } from './disease/DiseaseHistoryList';
import { AuthModal } from './auth/AuthModal';
import type { Language } from '../i18n/translations';
import { getDiseaseI18n } from '../utils/i18nDisease';
import { Sparkles, History, Sprout, AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  language?: Language;
}

export const CropDiseaseTab: React.FC<Props> = ({ language = 'en' }) => {
  const { user } = useAuth();
  const dI18n = getDiseaseI18n(language);

  const [activeSubTab, setActiveSubTab] = useState<'detect' | 'history'>('detect');
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  // Multi-image selection state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [notes, setNotes] = useState<string>('');
  const [formValidationErr, setFormValidationErr] = useState<string | null>(null);

  // Analysis Hook
  const {
    data: analysisResponse,
    loading: isAnalyzing,
    loadingStep,
    error: analysisError,
    submitAnalysis,
    resetAnalysis,
  } = useDiseaseAnalysis();

  // History Hook
  const {
    items: historyItems,
    loading: isHistoryLoading,
    loadHistory,
    removeItem: deleteHistoryItem,
  } = useDiseaseHistory(!!user);

  const handleStartAnalysis = async () => {
    setFormValidationErr(null);

    const filesToSubmit = selectedFiles.length > 0 ? selectedFiles : (selectedFile ? [selectedFile] : []);
    if (filesToSubmit.length === 0) {
      setFormValidationErr(dI18n.uploadTitle);
      return;
    }

    const response = await submitAnalysis({
      imageFile: filesToSubmit[0],
      imageFiles: filesToSubmit,
      notes: notes.trim() || undefined,
      language: language,
    });

    if (response && user) {
      loadHistory();
    }
  };

  const handleResetForNewAnalysis = () => {
    resetAnalysis();
    setSelectedFile(null);
    setSelectedFiles([]);
    setFormValidationErr(null);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem 0', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Banner Header */}
      <div
        style={{
          background: 'linear-gradient(135deg, #064e3b 0%, #047857 50%, #059669 100%)',
          borderRadius: '16px',
          padding: '1.75rem 2rem',
          color: '#ffffff',
          boxShadow: '0 10px 25px -5px rgba(6, 78, 59, 0.3)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1.25rem',
        }}
      >
        <div style={{ maxWidth: '640px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(255, 255, 255, 0.15)', padding: '0.25rem 0.75rem', borderRadius: '50px', fontSize: '0.78rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            <Sparkles size={14} />
            <span>{dI18n.badge}</span>
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: 800, margin: '0 0 0.4rem 0', color: '#ffffff' }}>
            {dI18n.tabTitle}
          </h2>
          <p style={{ fontSize: '0.92rem', opacity: 0.9, margin: 0, lineHeight: 1.45 }}>
            {dI18n.tabSubtitle}
          </p>
        </div>

        {/* Sub-Tab Navigation Toggle */}
        <div style={{ display: 'flex', background: 'rgba(0, 0, 0, 0.2)', padding: '0.35rem', borderRadius: '12px', gap: '0.35rem' }}>
          <button
            type="button"
            onClick={() => setActiveSubTab('detect')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.6rem 1.25rem',
              borderRadius: '8px',
              border: 'none',
              fontSize: '0.88rem',
              fontWeight: 700,
              cursor: 'pointer',
              background: activeSubTab === 'detect' ? '#ffffff' : 'transparent',
              color: activeSubTab === 'detect' ? '#064e3b' : '#ffffff',
              transition: 'all 0.2s ease',
            }}
          >
            <Sprout size={16} />
            <span>{dI18n.newAnalysisBtn}</span>
          </button>

          <button
            type="button"
            onClick={() => {
              if (!user) {
                setAuthMode('login');
                setAuthModalOpen(true);
                return;
              }
              setActiveSubTab('history');
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.6rem 1.25rem',
              borderRadius: '8px',
              border: 'none',
              fontSize: '0.88rem',
              fontWeight: 700,
              cursor: 'pointer',
              background: activeSubTab === 'history' ? '#ffffff' : 'transparent',
              color: activeSubTab === 'history' ? '#064e3b' : '#ffffff',
              transition: 'all 0.2s ease',
            }}
          >
            <History size={16} />
            <span>{dI18n.historyTitle}</span>
            {user && historyItems.length > 0 && (
              <span
                style={{
                  background: activeSubTab === 'history' ? '#064e3b' : 'rgba(255,255,255,0.3)',
                  color: '#ffffff',
                  fontSize: '0.72rem',
                  padding: '0.1rem 0.45rem',
                  borderRadius: '50px',
                  marginLeft: '0.2rem',
                }}
              >
                {historyItems.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      {activeSubTab === 'detect' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Analysis View State: Input Form vs Result Display */}
          {!analysisResponse?.result ? (
            <div
              style={{
                background: '#ffffff',
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                padding: '2rem',
                boxShadow: '0 4px 15px rgba(0,0,0,0.04)',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem',
              }}
            >
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.35rem 0' }}>
                  {dI18n.uploadTitle}
                </h3>
                <p style={{ fontSize: '0.88rem', color: '#64748b', margin: 0 }}>
                  {dI18n.uploadSubtitle}
                </p>
              </div>

              {/* Image Upload Zone */}
              <ImageUploader
                selectedFile={selectedFile}
                selectedFiles={selectedFiles}
                language={language}
                onFileSelect={(f) => {
                  setSelectedFile(f);
                  setFormValidationErr(null);
                }}
                onFilesSelect={(files) => {
                  setSelectedFiles(files);
                  setFormValidationErr(null);
                }}
                disabled={isAnalyzing}
              />

              {/* Optional Field Notes */}
              <div>
                <label
                  htmlFor="crop-notes"
                  style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#475569', marginBottom: '0.35rem' }}
                >
                  {dI18n.fieldNotesLabel}
                </label>
                <textarea
                  id="crop-notes"
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder={dI18n.fieldNotesPlaceholder}
                  disabled={isAnalyzing}
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    borderRadius: '10px',
                    border: '1px solid #cbd5e1',
                    fontSize: '0.88rem',
                    resize: 'vertical',
                    fontFamily: 'inherit',
                  }}
                />
              </div>

              {/* Validation Warning Alert */}
              {formValidationErr && (
                <div
                  style={{
                    background: '#fee2e2',
                    border: '1px solid #fca5a5',
                    borderRadius: '10px',
                    padding: '0.75rem 1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#991b1b',
                    fontSize: '0.88rem',
                    fontWeight: 600,
                  }}
                >
                  <AlertCircle size={18} />
                  <span>{formValidationErr}</span>
                </div>
              )}

              {/* Server Error Alert */}
              {analysisError && (
                <div
                  style={{
                    background: '#fee2e2',
                    border: '1px solid #fca5a5',
                    borderRadius: '10px',
                    padding: '0.75rem 1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#991b1b',
                    fontSize: '0.88rem',
                    fontWeight: 600,
                  }}
                >
                  <AlertCircle size={18} />
                  <span>{analysisError}</span>
                </div>
              )}

              {/* Login to save history hint for guest users */}
              {!user && (
                <div
                  style={{
                    background: '#f8fafc',
                    border: '1px dashed #cbd5e1',
                    borderRadius: '10px',
                    padding: '0.65rem 0.95rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    fontSize: '0.82rem',
                    color: '#475569',
                  }}
                >
                  <span>💡 <strong>Tip:</strong> Log in to save your disease diagnoses and view history later.</span>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setAuthModalOpen(true);
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--primary)',
                      fontWeight: 700,
                      cursor: 'pointer',
                      fontSize: '0.82rem',
                      textDecoration: 'underline',
                      padding: 0,
                    }}
                  >
                    Log In
                  </button>
                </div>
              )}

              {/* Action Button & Disclaimer */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <DiseaseAnalysisButton
                  loading={isAnalyzing}
                  language={language}
                  onClick={handleStartAnalysis}
                  disabled={isAnalyzing || (!selectedFile && selectedFiles.length === 0)}
                />

                <p style={{ fontSize: '0.78rem', color: '#94a3b8', margin: 0, textAlign: 'center' }}>
                  {dI18n.disclaimerText}
                </p>
              </div>
            </div>
          ) : (
            /* Result Display View */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              
              {/* Back / New Analysis Action Bar */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={handleResetForNewAnalysis}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                    background: '#ffffff',
                    border: '1px solid #cbd5e1',
                    padding: '0.55rem 1.15rem',
                    borderRadius: '10px',
                    fontSize: '0.88rem',
                    fontWeight: 700,
                    color: '#1e293b',
                    cursor: 'pointer',
                  }}
                >
                  <RefreshCw size={15} />
                  <span>{dI18n.analyzeAnotherBtn}</span>
                </button>

                <span style={{ fontSize: '0.82rem', color: '#64748b' }}>
                  ID: <code style={{ color: '#0f172a', fontWeight: 700 }}>{analysisResponse.analysis_id.slice(0, 8)}</code>
                </span>
              </div>

              {/* Result Card */}
              <DiseaseResultCard
                result={analysisResponse.result}
                createdAt={analysisResponse.created_at}
                language={language}
              />
            </div>
          )}

          {/* Loading Indicator State */}
          {isAnalyzing && <DiseaseLoadingState loadingStep={loadingStep} language={language} />}

        </div>
      ) : (
        /* History Sub-Tab View */
        <DiseaseHistoryList
          items={historyItems}
          loading={isHistoryLoading}
          language={language}
          onDelete={deleteHistoryItem}
          onRefresh={loadHistory}
        />
      )}

      {/* Auth Modal Trigger */}
      <AuthModal
        isOpen={authModalOpen}
        initialMode={authMode}
        onClose={() => setAuthModalOpen(false)}
      />

    </div>
  );
};
