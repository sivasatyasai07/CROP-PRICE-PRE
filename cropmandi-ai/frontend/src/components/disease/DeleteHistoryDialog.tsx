import React from 'react';
import { AlertTriangle, Trash2, X } from 'lucide-react';

export interface DeleteHistoryDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  cropName?: string;
  isDeleting?: boolean;
}

export const DeleteHistoryDialog: React.FC<DeleteHistoryDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  cropName,
  isDeleting = false,
}) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '1.75rem',
          maxWidth: '440px',
          width: '100%',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={onClose}
          disabled={isDeleting}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            color: '#64748b',
          }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: '#fee2e2',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <AlertTriangle size={24} color="#dc2626" />
          </div>

          <div>
            <h3 style={{ margin: '0 0 0.4rem 0', fontSize: '1.1rem', fontWeight: 800, color: '#0f172a' }}>
              Delete Analysis Record?
            </h3>
            <p style={{ margin: '0 0 1.25rem 0', fontSize: '0.85rem', color: '#64748b', lineHeight: 1.5 }}>
              Are you sure you want to delete this {cropName ? `"${cropName}"` : ''} crop-disease analysis? This action cannot be undone.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button
                type="button"
                onClick={onClose}
                disabled={isDeleting}
                style={{
                  padding: '0.55rem 1rem',
                  borderRadius: '8px',
                  border: '1px solid #cbd5e1',
                  background: '#ffffff',
                  color: '#334155',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: isDeleting ? 'not-allowed' : 'pointer',
                }}
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={onConfirm}
                disabled={isDeleting}
                style={{
                  padding: '0.55rem 1.15rem',
                  borderRadius: '8px',
                  border: 'none',
                  background: '#dc2626',
                  color: '#ffffff',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  cursor: isDeleting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                }}
              >
                <Trash2 size={15} />
                <span>{isDeleting ? 'Deleting...' : 'Delete'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
