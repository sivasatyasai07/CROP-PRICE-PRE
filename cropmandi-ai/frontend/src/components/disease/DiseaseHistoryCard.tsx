import React from 'react';
import type { DiseaseHistoryItem } from '../../types/disease';
import { getDiseaseImageUrl } from '../../services/diseaseService';
import { Calendar, Trash2, Eye } from 'lucide-react';

export interface DiseaseHistoryCardProps {
  item: DiseaseHistoryItem;
  onViewDetails: (item: DiseaseHistoryItem) => void;
  onDeleteClick: (item: DiseaseHistoryItem) => void;
}

export const DiseaseHistoryCard: React.FC<DiseaseHistoryCardProps> = ({
  item,
  onViewDetails,
  onDeleteClick,
}) => {
  const cropName = item.detected_crop || item.selected_crop || 'Identified Plant';
  const scientificName = item.detected_scientific_name || item.plantnet_results?.[0]?.scientific_name || '';
  const cropCategory = item.detected_crop_category || 'Cultivated Plant';
  const plantPart = item.plant_part || 'Leaf';

  const rawScore = item.plantnet_score ?? item.original_confidence?.plantnet_score ?? item.original_confidence?.crop;
  const scoreDisplay = rawScore !== null && rawScore !== undefined ? `${Math.round(rawScore * 100)}%` : '--';

  const formattedDate = new Date(item.created_at).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  const imageUrl = getDiseaseImageUrl(item.analysis_id);

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '14px',
        border: '1px solid #e2e8f0',
        padding: '1.15rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.85rem',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        transition: 'all 0.2s ease',
      }}
    >
      {/* Top row: Thumbnail + Details */}
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        {/* Leaf Thumbnail */}
        <div
          style={{
            width: '68px',
            height: '68px',
            borderRadius: '10px',
            background: '#f1f5f9',
            overflow: 'hidden',
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #cbd5e1',
          }}
        >
          <img
            src={imageUrl}
            alt={cropName}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
            onError={(e) => {
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
        </div>

        {/* Plant Info */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.2rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#15803d' }}>
              {cropName}
            </span>
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
              ({cropCategory.charAt(0).toUpperCase() + cropCategory.slice(1)})
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>•</span>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              {plantPart}
            </span>
          </div>

          <h4
            style={{
              fontSize: '0.92rem',
              fontWeight: 700,
              color: '#0f172a',
              margin: '0 0 0.35rem 0',
              fontStyle: 'italic',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {scientificName || 'Botanical Species'}
          </h4>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '0.15rem 0.5rem',
                borderRadius: '4px',
                background: '#dcfce7',
                color: '#166534',
              }}
            >
              PlantNet Score: {scoreDisplay}
            </span>

            <span style={{ fontSize: '0.72rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Calendar size={12} />
              {formattedDate}
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', borderTop: '1px solid #f1f5f9', paddingTop: '0.65rem' }}>
        <button
          type="button"
          onClick={() => onViewDetails(item)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.4rem 0.75rem',
            borderRadius: '6px',
            border: '1px solid #cbd5e1',
            background: '#ffffff',
            color: '#1e293b',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <Eye size={13} />
          <span>View Details</span>
        </button>

        <button
          type="button"
          onClick={() => onDeleteClick(item)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.4rem 0.65rem',
            borderRadius: '6px',
            border: '1px solid #fee2e2',
            background: '#fef2f2',
            color: '#dc2626',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <Trash2 size={13} />
          <span>Delete</span>
        </button>
      </div>
    </div>
  );
};
