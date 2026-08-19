import { useState, useCallback, useRef } from 'react';
import { fetchVerifiedForecast, type VerifiedForecastResponse } from '../services/forecastService';

export interface UseVerifiedForecastReturn {
  data: VerifiedForecastResponse | null;
  loading: boolean;
  loadingStep: string;
  stepIndex: number;
  error: string | null;
  generateForecast: (commodity: string, market: string, selectedDate: string, forceRefresh?: boolean, district?: string, state?: string) => Promise<void>;
  cancelRequest: () => void;
}

export function useVerifiedForecast(): UseVerifiedForecastReturn {
  const [data, setData] = useState<VerifiedForecastResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [stepIndex, setStepIndex] = useState<number>(1);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const activeRequestIdRef = useRef<number>(0);
  const stepTimerRef = useRef<number | null>(null);

  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (stepTimerRef.current) {
      window.clearTimeout(stepTimerRef.current);
      stepTimerRef.current = null;
    }
    setLoading(false);
    setLoadingStep('');
    setStepIndex(1);
  }, []);

  const generateForecast = useCallback(async (
    commodity: string,
    market: string,
    selectedDate: string,
    forceRefresh: boolean = true,
    district?: string,
    state?: string
  ) => {
    // 1. Generate unique request ID and store it
    activeRequestIdRef.current += 1;
    const thisRequestId = activeRequestIdRef.current;
    const reqUuid = `req_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;

    // 2. Cancel in-flight request if present
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    if (stepTimerRef.current) {
      window.clearTimeout(stepTimerRef.current);
    }

    // 3. Clear previous forecast result and set loading state
    setData(null);
    setLoading(true);
    setError(null);
    setStepIndex(1);
    setLoadingStep('Stage 1 of 5: Querying official data.gov.in API records with filters...');

    // Progress animation timers paced realistically to match backend processing duration
    stepTimerRef.current = window.setTimeout(() => {
      if (thisRequestId === activeRequestIdRef.current) {
        setStepIndex(2);
        setLoadingStep('Stage 2 of 5: Checking verified official records across 4-date horizon...');
        stepTimerRef.current = window.setTimeout(() => {
          if (thisRequestId === activeRequestIdRef.current) {
            setStepIndex(3);
            setLoadingStep('Stage 3 of 5: Checking master-data.csv & building feature vectors...');
            stepTimerRef.current = window.setTimeout(() => {
              if (thisRequestId === activeRequestIdRef.current) {
                setStepIndex(4);
                setLoadingStep('Stage 4 of 5: Executing CatBoost ML model inference for missing dates...');
                stepTimerRef.current = window.setTimeout(() => {
                  if (thisRequestId === activeRequestIdRef.current) {
                    setStepIndex(5);
                    setLoadingStep('Stage 5 of 5: Finalizing verified predictions & conformal intervals...');
                  }
                }, 1300);
              }
            }, 1200);
          }
        }, 1100);
      }
    }, 1100);

    try {
      const res = await fetchVerifiedForecast(
        {
          commodity,
          market,
          district,
          state,
          selected_date: selectedDate,
          force_refresh: forceRefresh,
          request_id: reqUuid,
        },
        abortControllerRef.current.signal
      );

      // 4. Ignore responses from older requests
      if (thisRequestId !== activeRequestIdRef.current) {
        return;
      }

      setData(res);
    } catch (err: any) {
      if (err.name === 'AbortError' || thisRequestId !== activeRequestIdRef.current) {
        return;
      }

      let errMsg = err.message || 'An error occurred while generating forecast';
      try {
        if (typeof errMsg === 'string' && errMsg.includes('{')) {
          const jsonStart = errMsg.indexOf('{');
          const parsed = JSON.parse(errMsg.slice(jsonStart));
          if (parsed.detail) {
            errMsg = typeof parsed.detail === 'object' ? parsed.detail.detail || parsed.detail.code : parsed.detail;
          }
        }
      } catch {
        // use raw message
      }

      setError(errMsg);
    } finally {
      if (thisRequestId === activeRequestIdRef.current) {
        if (stepTimerRef.current) {
          window.clearTimeout(stepTimerRef.current);
          stepTimerRef.current = null;
        }
        setLoading(false);
        setLoadingStep('');
        setStepIndex(1);
      }
    }
  }, []);

  return {
    data,
    loading,
    loadingStep,
    stepIndex,
    error,
    generateForecast,
    cancelRequest,
  };
}
