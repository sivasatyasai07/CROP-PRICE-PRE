import { useState, useCallback, useEffect } from 'react';
import type { DiseaseHistoryItem, DiseaseHistoryListResponse } from '../types/disease';
import { fetchDiseaseHistory, deleteDiseaseHistory, type DiseaseHistoryFilter } from '../services/diseaseService';

export interface UseDiseaseHistoryReturn {
  items: DiseaseHistoryItem[];
  totalCount: number;
  loading: boolean;
  error: string | null;
  loadHistory: (filter?: DiseaseHistoryFilter) => Promise<void>;
  removeItem: (analysisId: string) => Promise<boolean>;
}

export function useDiseaseHistory(autoLoad: boolean = true): UseDiseaseHistoryReturn {
  const [items, setItems] = useState<DiseaseHistoryItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = useCallback(async (filter?: DiseaseHistoryFilter) => {
    setLoading(true);
    setError(null);
    try {
      const resp: DiseaseHistoryListResponse = await fetchDiseaseHistory(filter);
      setItems(resp.analyses || []);
      setTotalCount(resp.total_count || 0);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Please log in to view your disease-analysis history.');
      } else {
        const msg = err.response?.data?.detail || err.message || 'Failed to load disease history.';
        setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const removeItem = useCallback(async (analysisId: string): Promise<boolean> => {
    try {
      await deleteDiseaseHistory(analysisId);
      setItems((prev) => prev.filter((item) => item.analysis_id !== analysisId));
      setTotalCount((prev) => Math.max(0, prev - 1));
      return true;
    } catch (err: any) {
      console.error('Failed to delete history item', err);
      return false;
    }
  }, []);

  useEffect(() => {
    if (autoLoad) {
      loadHistory();
    }
  }, [autoLoad, loadHistory]);

  return {
    items,
    totalCount,
    loading,
    error,
    loadHistory,
    removeItem,
  };
}
