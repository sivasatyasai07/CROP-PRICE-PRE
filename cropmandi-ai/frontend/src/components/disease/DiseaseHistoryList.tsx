import React, { useState } from 'react';
import type { DiseaseHistoryItem, DiseaseAnalysisResult } from '../../types/disease';
import type { Language } from '../../i18n/translations';
import { getDiseaseI18n } from '../../utils/i18nDisease';
import { DiseaseHistoryCard } from './DiseaseHistoryCard';
import { DeleteHistoryDialog } from './DeleteHistoryDialog';
import { DiseaseResultCard } from './DiseaseResultCard';
import { SUPPORTED_CROPS } from './CropSelector';
import { Filter, History, Loader2, X, RefreshCw, Sprout } from 'lucide-react';

export interface DiseaseHistoryListProps {
  items: DiseaseHistoryItem[];
  loading: boolean;
  onRefresh: () => void;
  onDeleteItem?: (analysisId: string) => Promise<boolean>;
  onDelete?: (analysisId: string) => Promise<boolean>;
  language?: Language;
}

export const DiseaseHistoryList: React.FC<DiseaseHistoryListProps> = ({
  items,
  loading,
  onRefresh,
  onDeleteItem,
  onDelete,
  language = 'en',
}) => {
  const dI18n = getDiseaseI18n(language);
  const [selectedCropFilter, setSelectedCropFilter] = useState<string>('');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('');
  const [activeDetailItem, setActiveDetailItem] = useState<DiseaseHistoryItem | null>(null);
  const [itemToDelete, setItemToDelete] = useState<DiseaseHistoryItem | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const deleteFunc = onDeleteItem || onDelete;

  // Apply in-memory filters
  const filteredItems = items.filter((item) => {
    const cropName = item.detected_crop || item.selected_crop || item.crop || '';
    if (selectedCropFilter && cropName.toLowerCase() !== selectedCropFilter.toLowerCase()) {
      return false;
    }
    if (selectedStatusFilter && item.health_status !== selectedStatusFilter) {
      return false;
    }
    return true;
  });

  const handleDeleteConfirm = async () => {
    if (!itemToDelete || !deleteFunc) return;
    setIsDeleting(true);
    const success = await deleteFunc(itemToDelete.analysis_id);
    setIsDeleting(false);
    if (success) {
      if (activeDetailItem?.analysis_id === itemToDelete.analysis_id) {
        setActiveDetailItem(null);
      }
      setItemToDelete(null);
    }
  };

  // Convert history item into a renderable DiseaseAnalysisResult for the detail modal
  const getDetailResult = (item: DiseaseHistoryItem): DiseaseAnalysisResult => {
    const cropName = item.detected_crop || item.selected_crop || item.crop || 'Crop Leaf';
    const cropProb = item.gemini_original_probability ?? item.original_confidence?.crop ?? null;
    return {
      analysis_status: 'success',
      image_quality: {
        status: 'acceptable',
        score: null,
        issues: []
      },
      plant_detected: true,
      crop_recognition: {
        identification_status: (item.identification_status as any) || 'probable',
        best_crop: {
          name: cropName,
          category: item.detected_crop_category || 'vegetable',
          crop_status: item.crop_status || 'recognized',
          gemini_original_probability: cropProb,
          classifier_probability: item.classifier_probability ?? null,
          combined_probability: item.combined_probability ?? null,
          final_selection_source: 'gemini_original_probability'
        },
        ranked_candidates: item.ranked_candidates || [
          {
            name: cropName,
            category: item.detected_crop_category || 'vegetable',
            crop_status: item.crop_status || 'recognized',
            gemini_original_probability: cropProb,
          }
        ],
        feature_analysis: item.feature_analysis,
        ambiguity: item.ambiguity,
        crop_name: cropName,
        confidence: cropProb
      },
      crop_comparison: {
        user_selected_crop: item.selected_crop,
        detected_best_crop: cropName,
        match_status: (item.crop_match_status as any) || 'not_provided',
        reason: `Diagnosed for ${cropName}`
      },
      next_image_request: item.next_image_request || { needed: false, suggested_images: [] },
      plant_part: {
        name: item.plant_part || 'Leaf',
        confidence: item.original_confidence?.plant_part ?? null
      },
      health_assessment: {
        status: item.health_status || 'disease',
        confidence: item.original_confidence?.health_status ?? null,
        visible_evidence: item.primary_diagnosis?.evidence || []
      },
      primary_diagnosis: {
        name: item.primary_diagnosis?.name || 'Diagnostic Record',
        category: item.primary_diagnosis?.category || item.health_status,
        confidence: item.original_confidence?.primary_diagnosis ?? item.primary_diagnosis?.confidence ?? null,
        evidence: item.primary_diagnosis?.evidence || []
      },
      alternative_diagnoses: [],
      symptoms: item.symptoms || [],
      possible_causes: item.possible_causes || [],
      immediate_actions: item.immediate_actions || [],
      prevention: item.prevention || [],
      chemical_control_guidance: {
        provided: false,
        message: dI18n.disclaimerText
      },
      limitations: [],
      model_disclaimer: item.disclaimer || dI18n.disclaimerText,
      disclaimer: item.disclaimer || dI18n.disclaimerText,
      language: item.language || 'en'
    };
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      
      {/* Top Filter & Toolbar Bar */}
      <div
        style={{
          background: '#ffffff',
          borderRadius: '14px',
          border: '1px solid #e2e8f0',
          padding: '1rem 1.25rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#64748b', fontSize: '0.84rem', fontWeight: 700 }}>
            <Filter size={16} />
            <span>Filter By:</span>
          </div>

          {/* Crop Filter Dropdown */}
          <select
            value={selectedCropFilter}
            onChange={(e) => setSelectedCropFilter(e.target.value)}
            style={{
              padding: '0.45rem 0.75rem',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              fontSize: '0.82rem',
              fontWeight: 600,
              color: '#0f172a',
              background: '#ffffff',
            }}
          >
            <option value="">All Crops</option>
            {SUPPORTED_CROPS.map((crop) => (
              <option key={crop} value={crop}>
                {crop}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatusFilter}
            onChange={(e) => setSelectedStatusFilter(e.target.value)}
            style={{
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              fontSize: '0.82rem',
              fontWeight: 600,
              color: '#334155',
              background: '#f8fafc',
            }}
          >
            <option value="">All Statuses</option>
            <option value="healthy">{dI18n.statusHealthy}</option>
            <option value="disease">{dI18n.statusDisease}</option>
            <option value="pest_damage">{dI18n.statusPest}</option>
            <option value="nutrient_deficiency">{dI18n.statusNutrient}</option>
          </select>

          {/* Reset Filters Button */}
          {(selectedCropFilter || selectedStatusFilter) && (
            <button
              type="button"
              onClick={() => {
                setSelectedCropFilter('');
                setSelectedStatusFilter('');
              }}
              style={{
                background: '#f1f5f9',
                border: 'none',
                borderRadius: '6px',
                padding: '0.35rem 0.65rem',
                fontSize: '0.78rem',
                fontWeight: 600,
                color: '#475569',
                cursor: 'pointer',
              }}
            >
              Clear Filters
            </button>
          )}
        </div>

        {/* Refresh History Button */}
        <button
          type="button"
          onClick={onRefresh}
          disabled={loading}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: '#ffffff',
            border: '1px solid #cbd5e1',
            padding: '0.45rem 0.85rem',
            borderRadius: '8px',
            fontSize: '0.82rem',
            fontWeight: 700,
            color: '#1e293b',
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* History Cards Grid */}
      {loading && items.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: '#ffffff', borderRadius: '14px', border: '1px solid #e2e8f0' }}>
          <Loader2 size={32} className="spin" color="#16a34a" style={{ margin: '0 auto 0.75rem auto' }} />
          <p style={{ fontSize: '0.9rem', color: '#64748b', margin: 0 }}>Loading your analysis history…</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3.5rem 1.5rem', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: '#f1f5f9',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
              color: '#94a3b8',
            }}
          >
            <History size={28} />
          </div>
          <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.35rem 0' }}>
            {dI18n.noHistory}
          </h4>
          <p style={{ fontSize: '0.88rem', color: '#64748b', margin: 0, maxWidth: '400px' }}>
            {selectedCropFilter || selectedStatusFilter
              ? 'No historical diagnoses match your selected filters.'
              : dI18n.noHistoryDesc}
          </p>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.25rem',
          }}
        >
          {filteredItems.map((item) => (
            <DiseaseHistoryCard
              key={item.analysis_id}
              item={item}
              onViewDetails={(it) => setActiveDetailItem(it)}
              onDeleteClick={(it) => setItemToDelete(it)}
            />
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {activeDetailItem && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(15, 23, 42, 0.65)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '1rem',
          }}
          onClick={() => setActiveDetailItem(null)}
        >
          <div
            style={{
              background: '#ffffff',
              borderRadius: '16px',
              maxWidth: '800px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sprout size={18} color="#16a34a" />
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                  Historical Diagnosis Detail
                </h3>
              </div>

              <button
                type="button"
                onClick={() => setActiveDetailItem(null)}
                style={{
                  border: 'none',
                  background: '#f1f5f9',
                  borderRadius: '50%',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  color: '#475569',
                }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.5rem' }}>
              <DiseaseResultCard
                result={getDetailResult(activeDetailItem)}
                createdAt={activeDetailItem.created_at}
                language={language}
              />
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <DeleteHistoryDialog
        isOpen={!!itemToDelete}
        onClose={() => setItemToDelete(null)}
        onConfirm={handleDeleteConfirm}
        cropName={itemToDelete?.detected_crop || itemToDelete?.selected_crop || itemToDelete?.crop || 'Crop'}
        isDeleting={isDeleting}
      />

    </div>
  );
};
