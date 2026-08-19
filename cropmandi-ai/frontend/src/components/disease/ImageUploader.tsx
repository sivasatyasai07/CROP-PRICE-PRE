import React, { useState, useRef, useCallback } from 'react';
import { Upload, Camera, AlertCircle, Plus, X } from 'lucide-react';
import type { Language } from '../../i18n/translations';
import { getDiseaseI18n } from '../../utils/i18nDisease';

export interface ImageUploaderProps {
  selectedFile: File | null;
  selectedFiles?: File[];
  language?: Language;
  onFileSelect: (file: File | null) => void;
  onFilesSelect?: (files: File[]) => void;
  disabled?: boolean;
}

export const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB
export const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  selectedFile,
  selectedFiles = [],
  language = 'en',
  onFileSelect,
  onFilesSelect,
  disabled = false,
}) => {
  const dI18n = getDiseaseI18n(language);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);

  const allFiles = selectedFiles.length > 0 ? selectedFiles : (selectedFile ? [selectedFile] : []);

  const validateAndAddFiles = useCallback((incomingFiles: FileList | File[]) => {
    setErrorMessage(null);
    const valid: File[] = [...allFiles];

    for (let i = 0; i < incomingFiles.length; i++) {
      const file = incomingFiles[i];
      if (valid.length >= 3) {
        setErrorMessage(dI18n.maxFilesWarning);
        break;
      }

      if (!ALLOWED_MIME_TYPES.includes(file.type.toLowerCase())) {
        setErrorMessage('Only JPG, PNG, and WEBP images are supported.');
        continue;
      }

      if (file.size > MAX_IMAGE_SIZE_BYTES) {
        setErrorMessage('Image size must not exceed 10 MB.');
        continue;
      }

      valid.push(file);
    }

    if (valid.length > 0) {
      onFileSelect(valid[0]);
      if (onFilesSelect) onFilesSelect(valid);
    }
  }, [allFiles, onFileSelect, onFilesSelect, dI18n.maxFilesWarning]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndAddFiles(e.dataTransfer.files);
    }
  }, [disabled, validateAndAddFiles]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndAddFiles(e.target.files);
    }
  };

  const handleRemoveIndex = (index: number) => {
    const updated = allFiles.filter((_, i) => i !== index);
    if (updated.length > 0) {
      onFileSelect(updated[0]);
      if (onFilesSelect) onFilesSelect(updated);
    } else {
      onFileSelect(null);
      if (onFilesSelect) onFilesSelect([]);
    }
    setErrorMessage(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      
      {/* Hidden File & Camera Inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        style={{ display: 'none' }}
        onChange={handleFileChange}
        disabled={disabled}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        capture="environment"
        style={{ display: 'none' }}
        onChange={handleFileChange}
        disabled={disabled}
      />

      {/* Main Upload Dropzone */}
      {allFiles.length === 0 ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${dragActive ? '#10b981' : '#cbd5e1'}`,
            borderRadius: '16px',
            background: dragActive ? '#ecfdf5' : '#f8fafc',
            padding: '2.5rem 1.5rem',
            textAlign: 'center',
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
          }}
          onClick={() => {
            if (!disabled && fileInputRef.current) fileInputRef.current.click();
          }}
        >
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: '#dcfce7',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
              color: '#16a34a',
            }}
          >
            <Upload size={30} strokeWidth={2.2} />
          </div>

          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.35rem 0' }}>
            {dI18n.uploadTitle}
          </h3>

          <p style={{ fontSize: '0.88rem', color: '#64748b', margin: '0 0 1.25rem 0' }}>
            {dI18n.dragDropText}
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }} onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="btn btn-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                padding: '0.65rem 1.25rem',
                borderRadius: '10px',
                fontSize: '0.88rem',
                fontWeight: 700,
                background: '#16a34a',
                color: '#ffffff',
                border: 'none',
                cursor: 'pointer',
              }}
              onClick={() => {
                if (fileInputRef.current) fileInputRef.current.click();
              }}
              disabled={disabled}
            >
              <Upload size={17} />
              <span>{dI18n.browseFiles}</span>
            </button>

            <button
              type="button"
              className="btn btn-outline"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                padding: '0.65rem 1.25rem',
                borderRadius: '10px',
                fontSize: '0.88rem',
                fontWeight: 700,
                background: '#ffffff',
                color: '#334155',
                border: '1px solid #cbd5e1',
                cursor: 'pointer',
              }}
              onClick={() => {
                if (cameraInputRef.current) cameraInputRef.current.click();
              }}
              disabled={disabled}
            >
              <Camera size={17} />
              <span>{dI18n.takePhoto}</span>
            </button>
          </div>

          <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '1rem' }}>
            {dI18n.supportedFormatsText}
          </div>
        </div>
      ) : (
        /* Image Preview Gallery */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            {allFiles.map((file, idx) => {
              const url = URL.createObjectURL(file);
              return (
                <div
                  key={idx}
                  style={{
                    position: 'relative',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    border: '1px solid #e2e8f0',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.06)',
                    background: '#f8fafc',
                    aspectRatio: '4/3',
                  }}
                >
                  <img
                    src={url}
                    alt={`Crop preview ${idx + 1}`}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                  <div
                    style={{
                      position: 'absolute',
                      top: '8px',
                      left: '8px',
                      background: 'rgba(15, 23, 42, 0.75)',
                      color: '#ffffff',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '0.15rem 0.5rem',
                      borderRadius: '50px',
                    }}
                  >
                    Image {idx + 1}
                  </div>
                  {!disabled && (
                    <button
                      type="button"
                      onClick={() => handleRemoveIndex(idx)}
                      style={{
                        position: 'absolute',
                        top: '8px',
                        right: '8px',
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: 'rgba(239, 68, 68, 0.9)',
                        color: '#ffffff',
                        border: 'none',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                      }}
                      title="Remove image"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              );
            })}

            {allFiles.length < 3 && !disabled && (
              <div
                onClick={() => {
                  if (fileInputRef.current) fileInputRef.current.click();
                }}
                style={{
                  border: '2px dashed #cbd5e1',
                  borderRadius: '12px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  aspectRatio: '4/3',
                  background: '#f8fafc',
                  color: '#64748b',
                  padding: '1rem',
                  textAlign: 'center',
                }}
              >
                <Plus size={24} color="#16a34a" />
                <span style={{ fontSize: '0.82rem', fontWeight: 700, marginTop: '0.35rem' }}>Add Another Angle</span>
                <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Max 3 photos</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Validation / Format Error Banner */}
      {errorMessage && (
        <div
          style={{
            background: '#fee2e2',
            border: '1px solid #fca5a5',
            borderRadius: '10px',
            padding: '0.65rem 1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: '#991b1b',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          <AlertCircle size={17} />
          <span>{errorMessage}</span>
        </div>
      )}

    </div>
  );
};
