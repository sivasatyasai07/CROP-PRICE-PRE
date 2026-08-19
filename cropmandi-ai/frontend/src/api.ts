import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('cropmandi_auth_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

export interface Market {
  id: number;
  canonical_name: string;
  original_name: string;
  district: string;
  state: string;
  latitude?: number;
  longitude?: number;
  is_active: boolean;
}

export interface ClosestMarketItem {
  market_id: number;
  market_name: string;
  district: string;
  state: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  rank: number;
}

export interface ClosestMarketsResponse {
  user_location: {
    latitude: number;
    longitude: number;
  };
  markets: ClosestMarketItem[];
  total_markets_considered: number;
  markets_without_coordinates: number;
}

export interface Commodity {
  id: number;
  canonical_name: string;
  commodity_group: string;
  unit: string;
}

export interface PredictionHorizon {
  target_date: string;
  horizon: number;
  predicted_modal_price: number;
  lower_bound: number;
  upper_bound: number;
  confidence_level: number;
  is_actual?: boolean;
}

export interface PredictionResponse {
  commodity: string;
  market: string;
  unit: string;
  prediction_date: string;
  latest_observed_price: number;
  latest_observed_date: string;
  trend_direction: 'upward' | 'downward' | 'stable';
  percentage_change_3d: number;
  advisory_text?: string;
  predictions: PredictionHorizon[];
  warning: string;
  model_name: string;
  model_version: string;
  data_freshness: string;
  weather_available: boolean;
  fallback_used: boolean;
  fallback_reason?: string;
}

export interface PriceHistoryItem {
  observation_date: string;
  modal_price: number;
  min_price?: number;
  max_price?: number;
  arrival_quantity?: number;
  quality_status: string;
}

export interface PriceCompareItem {
  market_id: number;
  market_name: string;
  district: string;
  latest_date: string;
  latest_modal_price: number;
  min_price?: number;
  max_price?: number;
  arrival_quantity?: number;
  unit: string;
}

export interface RecommendationMarket {
  market_id: number;
  market_name: string;
  district: string;
  day1_predicted_price: number;
  day3_predicted_price: number;
  latest_observed_price: number;
  latest_date: string;
  distance_km?: number;
  trend_direction: string;
  confidence_level: number;
  net_realization?: number;
  cost_breakdown?: {
    gross_revenue: number;
    commission_cost: number;
    wastage_cost: number;
    transport_cost: number;
    net_realization: number;
  };
}

export interface RecommendationResponse {
  commodity: string;
  prediction_date: string;
  ranking_mode: string;
  notice: string;
  markets: RecommendationMarket[];
}

export interface WeatherObservation {
  market_id: number;
  observation_date: string;
  temperature_max?: number;
  temperature_min?: number;
  precipitation?: number;
  humidity?: number;
  wind_speed?: number;
  weather_code?: number;
  is_historical: boolean;
}

export interface AdminStatus {
  last_successful_ingestion?: string;
  last_successful_cleaning?: string;
  last_successful_weather_sync?: string;
  last_successful_training?: string;
  active_model_version: string;
  total_raw_records: number;
  total_cleaned_records: number;
  status: string;
}
