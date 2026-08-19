import React from 'react';
import { Trash2, RefreshCw } from 'lucide-react';

export interface ImagePreviewProps {
  imagePreviewUrl: string;
  fileName?: string;
  fileSizeMb?: number;
  onRemove: () => void;
  onReplace: () => void;
  disabled?: boolean;
}

export const ImagePreview: React.FC<ImagePreviewProps> = ({
  imagePreviewUrl,
  fileName,
  fileSizeMb,
  onRemove,
  onReplace,
  disabled = false,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        background: '#f8fafc',
        borderRadius: '14px',
        border: '1px solid #e2e8f0',
        padding: '1.25rem',
        gap: '1rem',
      }}
    >
      <div
        style={{
          width: '100%',
          maxHeight: '320px',
          borderRadius: '10px',
          overflow: 'hidden',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: '#0f172a',
        }}
      >
        <img
          src={imagePreviewUrl}
          alt="Crop Leaf Preview"
          style={{
            maxWidth: '100%',
            maxHeight: '320px',
            objectFit: 'contain',
            borderRadius: '10px',
          }}
        />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          {fileName && (
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#1e293b' }}>
              {fileName}
            </div>
          )}
          {fileSizeMb !== undefined && (
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
              Size: {fileSizeMb.toFixed(2)} MB
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            onClick={onReplace}
            disabled={disabled}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              background: '#ffffff',
              color: '#334155',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: disabled ? 'not-allowed' : 'pointer',
            }}
          >
            <RefreshCw size={14} />
            <span>Replace</span>
          </button>

          <button
            type="button"
            onClick={onRemove}
            disabled={disabled}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              border: '1px solid #fecaca',
              background: '#fef2f2',
              color: '#dc2626',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: disabled ? 'not-allowed' : 'pointer',
            }}
          >
            <Trash2 size={14} />
            <span>Remove</span>
          </button>
        </div>
      </div>
    </div>
  );
};
