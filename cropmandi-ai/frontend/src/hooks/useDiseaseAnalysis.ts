import { useState, useCallback, useRef } from 'react';
import type { DiseaseAnalysisResponse } from '../types/disease';
import { analyzeCrop, type AnalyzeCropRequest } from '../services/diseaseService';

export interface UseDiseaseAnalysisReturn {
  data: DiseaseAnalysisResponse | null;
  loading: boolean;
  loadingStep: string;
  error: string | null;
  submitAnalysis: (req: AnalyzeCropRequest) => Promise<DiseaseAnalysisResponse | null>;
  resetAnalysis: () => void;
}

export function useDiseaseAnalysis(): UseDiseaseAnalysisReturn {
  const [data, setData] = useState<DiseaseAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const resetAnalysis = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setData(null);
    setLoading(false);
    setLoadingStep('');
    setError(null);
  }, []);

  const submitAnalysis = useCallback(async (req: AnalyzeCropRequest): Promise<DiseaseAnalysisResponse | null> => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setData(null);
    setLoading(true);
    setError(null);
    setLoadingStep('Analyzing crop image…');

    try {
      const stepTimer = setTimeout(() => {
        setLoadingStep('Checking visible symptoms and preparing recommendations…');
      }, 1500);

      const response = await analyzeCrop(req, abortControllerRef.current.signal);
      clearTimeout(stepTimer);
      setData(response);
      return response;
    } catch (err: any) {
      if (err.name === 'AbortError' || err.code === 'ERR_CANCELED') {
        return null;
      }
      let msg = err.response?.data?.detail || err.message || 'An error occurred while analyzing the image.';
      if (typeof msg === 'object') {
        msg = JSON.stringify(msg);
      }
      setError(msg);
      return null;
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  }, []);

  return {
    data,
    loading,
    loadingStep,
    error,
    submitAnalysis,
    resetAnalysis,
  };
}
