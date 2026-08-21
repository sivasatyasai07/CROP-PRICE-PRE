import { api } from '../api';

export interface LookupTraceItem {
  source: string;
  searched: boolean;
  found: boolean;
  status?: string;
  reason?: string;
}

export interface ForecastRecord {
  date: string;
  target_date?: string;
  forecast_origin_date?: string;
  observation_date?: string | null;
  horizon?: number;
  
  modal_price: number | null;
  min_price: number | null;
  max_price: number | null;
  arrival_quantity: number | null;
  arrival_unit?: string;
  price_unit?: string;
  
  price_source: 'official_api' | 'official_csv' | 'predicted_model' | 'fallback_last_observed' | 'fallback_rolling_average' | 'unavailable' | 'predicted' | string;
  data_status: 'observed_live' | 'observed_csv' | 'predicted_model' | 'predicted_fallback' | 'fallback_last_observed' | 'unavailable' | string;
  prediction_status?: 'active' | 'superseded_by_newer_forecast' | 'superseded_by_official' | 'expired' | 'unavailable' | string;
  prediction_method?: 'official_observation' | 'trained_model' | 'fallback' | 'none' | string;
  model_predict_called?: boolean;
  prediction_executed?: boolean;
  model_error_code?: string | null;
  raw_model_output?: number | null;
  final_prediction?: number | null;
  
  is_observed: boolean;
  is_predicted: boolean;
  
  source_label: string;
  verification_status: string;
  source_name?: string | null;
  source_record_id?: string | null;
  fetched_at?: string | null;
  data_fetched_at?: string | null;
  generated_at?: string | null;
  model_name?: string | null;
  model_version?: string | null;
  feature_snapshot_id?: string | null;
  previous_forecast?: {
    forecast_origin_date: string;
    predicted_modal_price: number;
    model_version?: string;
  } | null;
  data_freshness?: string | null;
  
  confidence_level?: number | null;
  confidence_source?: string | null;
  interval_available?: boolean;
  interval_method?: string | null;
  lower_bound?: number | null;
  upper_bound?: number | null;
  confidence_interval?: {
    lower?: number | null;
    upper?: number | null;
  } | null;
  fallback_reason?: string | null;
  warning?: string | null;
  
  arrival_features_used?: boolean;
  weather_features_used?: boolean;
  seasonal_features_used?: boolean;
  arrival_missing?: boolean | null;
  weather_missing?: boolean | null;
  feature_row_date?: string | null;
  
  api_checked?: boolean;
  api_record_found?: boolean;
  master_csv_checked?: boolean;
  master_csv_record_found?: boolean;
  prediction_generated?: boolean;
  final_source?: string;
  lookup_trace?: LookupTraceItem[];
}

export interface VerifiedForecastRequest {
  commodity: string;
  market: string;
  district?: string;
  state?: string;
  selected_date: string;
  force_refresh?: boolean;
  request_id?: string;
}

export interface VerifiedForecastResponse {
  request_id: string;
  commodity: string;
  market: string;
  district?: string;
  state?: string;
  selected_date: string;
  forecast_origin_date?: string;
  date_range: {
    start: string;
    end: string;
  };
  fetched_at: string;
  api_checked: boolean;
  api_status: string;
  sync_performed: boolean;
  refresh_performed: boolean;
  latest_observed_price?: number;
  latest_observed_date?: string;
  latest_official_date?: string | null;
  latest_value_is_today?: boolean;
  trend_direction?: string;
  percentage_change_3d?: number;
  trend_source?: string;
  trend_start_date?: string;
  trend_end_date?: string;
  trend_start_price?: number;
  trend_end_price?: number;
  official_values_used?: number;
  predicted_values_used?: number;
  records: ForecastRecord[];
  summary: {
    official_api_count?: number;
    official_csv_count?: number;
    predicted_model_count?: number;
    fallback_last_observed_count?: number;
    predicted_count?: number;
    unavailable_count?: number;
    official_values?: number;
    predicted_values?: number;
    unavailable_values?: number;
  };
  warnings: string[];
  server_date?: string;
  server_today?: string;
  future_dates_disabled?: boolean;
  selected_date_valid?: boolean;
  api_checked_time?: string;
  closest_market_status?: string;
  model_version?: string;
  feature_snapshot_id?: string;
  feature_schema_match?: boolean;
  missing_features?: string[];
  unexpected_features?: string[];
  expected_feature_count?: number;
  feature_explanations?: string[];
  
  // Live API verification & data freshness
  api_refresh_performed?: boolean;
  api_latest_available_date?: string | null;
  database_latest_date?: string | null;
  feature_latest_date?: string | null;
  latest_official_api_date?: string | null;
  latest_stored_official_date?: string | null;
  latest_price_used_for_features?: number | null;
  latest_arrival_used_for_features?: number | null;
  data_refresh_status?: string;
  data_age_days?: number;
  stale_data_warning?: string | null;
  records_fetched_count?: number;
  records_used_in_features?: number;
}

export interface ForecastHistoryItem {
  id: number;
  commodity: string;
  market: string;
  forecast_origin_date: string;
  target_date: string;
  horizon: number;
  predicted_modal_price: number;
  lower_bound: number;
  upper_bound: number;
  price_source: string;
  prediction_status: string;
  model_version?: string;
  feature_snapshot_id?: string;
  generated_at?: string;
  superseded_by_official?: boolean;
}

export interface OfficialStatusResponse {
  commodity: string;
  market: string;
  target_date: string;
  official_api_checked: boolean;
  official_record_found: boolean;
  master_data_checked: boolean;
  master_record_found: boolean;
  active_prediction_exists: boolean;
  final_source: string;
  observed_price?: number;
}

export interface SyncStatusResponse {
  status: 'idle' | 'in_progress' | 'success' | 'failed';
  started_at: string;
  completed_at?: string;
  latest_api_date?: string;
  records_received: number;
  records_accepted: number;
  records_rejected: number;
  predictions_replaced: number;
  error?: string;
}

export const isValidPriceRecord = (rec: ForecastRecord): boolean => {
  if (rec.price_source === 'unavailable' || rec.data_status === 'unavailable') {
    return false;
  }
  if (rec.modal_price === null || rec.modal_price === undefined || rec.modal_price <= 0) {
    return false;
  }
  if (rec.min_price !== null && rec.min_price !== undefined && rec.min_price > rec.modal_price) {
    return false;
  }
  if (rec.max_price !== null && rec.max_price !== undefined && rec.max_price < rec.modal_price) {
    return false;
  }
  return true;
};

export const fetchVerifiedForecast = async (
  request: VerifiedForecastRequest,
  signal?: AbortSignal
): Promise<VerifiedForecastResponse> => {
  const response = await api.post<VerifiedForecastResponse>('/forecast/verified', request, { signal });
  return response.data;
};

export const fetchForecastHistory = async (
  commodity: string,
  market: string,
  target_date?: string,
  limit: number = 50
): Promise<ForecastHistoryItem[]> => {
  const params: Record<string, any> = { commodity, market, limit };
  if (target_date) params.target_date = target_date;
  const response = await api.get<ForecastHistoryItem[]>('/forecast/history', { params });
  return response.data;
};

export const fetchOfficialStatus = async (
  commodity: string,
  market: string,
  target_date: string
): Promise<OfficialStatusResponse> => {
  const response = await api.get<OfficialStatusResponse>('/forecast/official-status', {
    params: { commodity, market, target_date }
  });
  return response.data;
};

export const triggerLiveMarketSync = async (force: boolean = false): Promise<SyncStatusResponse> => {
  const response = await api.post<SyncStatusResponse>('/official/sync/live', { force });
  return response.data;
};

export const getLatestSyncStatus = async (): Promise<SyncStatusResponse> => {
  const response = await api.get<SyncStatusResponse>('/official/sync/status');
  return response.data;
};

export const getAvailableMarkets = async (): Promise<string[]> => {
  const response = await api.get<any[]>('/markets');
  return response.data.map((m: any) => m.canonical_name || m.name || m.original_name);
};

export const getAvailableCommodities = async (): Promise<string[]> => {
  const response = await api.get<any[]>('/commodities');
  return response.data.map((c: any) => c.canonical_name || c.name || c.original_name);
};

export interface DataSourceHealthResponse {
  resource_id: string;
  api_status: string;
  http_status: number;
  record_count: number;
  latest_available_date: string | null;
  actual_fields: string[];
  checked_at: string;
  message: string;
}

export const getDataSourceHealth = async (params?: {
  state?: string;
  district?: string;
  market?: string;
  commodity?: string;
}): Promise<DataSourceHealthResponse> => {
  const response = await api.get<DataSourceHealthResponse>('/data-source/health', { params });
  return response.data;
};

export interface TrendPoint {
  date: string;
  modal_price: number;
  min_price?: number | null;
  max_price?: number | null;
  arrival_quantity?: number | null;
  unit?: string;
  price_source: string;
  is_observed: boolean;
  is_predicted: boolean;
  data_age_days: number;
  source_label: string;
  observed_at: string;
}

export interface CompareMarketItem {
  market: string;
  district: string;
  state: string;
  modal_price: number;
  min_price?: number | null;
  max_price?: number | null;
  arrival_quantity?: number | null;
  observation_date: string;
  data_age_days: number;
  price_source: string;
  is_observed: boolean;
  is_predicted: boolean;
  source_label: string;
  is_latest_available_value: boolean;
  unit?: string;
  market_id?: number;
}

export interface ExcludedMarketItem {
  market: string;
  reason: string;
  latest_observation_date?: string;
  data_age_days?: number;
}

export interface CompareResponse {
  commodity: string;
  requested_date?: string | null;
  current_date: string;
  max_latest_value_age_days: number;
  markets: CompareMarketItem[];
  excluded_markets: ExcludedMarketItem[];
}

export interface RecentCommodity {
  id?: number;
  canonical_name: string;
  commodity_name: string;
  latest_official_observed_date?: string | null;
  record_count: number;
  availability_status: string;
  data_age_days?: number | null;
}

export interface RecentMarket {
  id?: number;
  canonical_name: string;
  market_name: string;
  district: string;
  state: string;
  latest_official_observed_date?: string | null;
  record_count: number;
  availability_status: string;
  data_age_days?: number | null;
}

export const fetchRecentCommodities = async (days: number = 30, minRecords: number = 3): Promise<RecentCommodity[]> => {
  const response = await api.get<RecentCommodity[]>('/commodities/recent', { params: { days, min_records: minRecords } });
  return response.data;
};

export const fetchRecentMarkets = async (commodity: string, days: number = 30, minRecords: number = 3): Promise<RecentMarket[]> => {
  const response = await api.get<RecentMarket[]>('/markets/recent', { params: { commodity, days, min_records: minRecords } });
  return response.data;
};

export const fetchPriceTrends = async (params: {
  commodity: string;
  market: string;
  state?: string;
  district?: string;
  days?: number;
  force_refresh?: boolean;
}): Promise<TrendPoint[]> => {
  const response = await api.get<TrendPoint[]>('/prices/trends', { params });
  return response.data;
};

export const fetchPriceComparison = async (params: {
  commodity: string;
  state?: string;
  district?: string;
  date?: string;
  max_age_days?: number;
  force_refresh?: boolean;
}): Promise<CompareResponse> => {
  const response = await api.get<CompareResponse>('/prices/compare', { params });
  return response.data;
};


