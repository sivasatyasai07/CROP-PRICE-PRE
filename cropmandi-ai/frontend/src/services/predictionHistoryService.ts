import { supabase } from '../lib/supabase';
import type { PredictionResponse } from '../api';

export interface PredictionHistoryRecord {
  id: string;
  user_id: string;
  crop: string;
  state?: string;
  district?: string;
  market: string;
  current_price: number;
  predicted_price: number;
  min_price?: number;
  max_price?: number;
  trend: string;
  forecast_days: number;
  prediction_date: string;
  model_name: string;
  created_at: string;
}

export interface SavePredictionParams {
  crop: string;
  market: string;
  state?: string;
  district?: string;
  predictionDate: string;
  predictionResponse: PredictionResponse;
}

export const predictionHistoryService = {
  /**
   * Save a newly generated forecast to Supabase prediction_history table
   */
  async savePrediction(params: SavePredictionParams): Promise<PredictionHistoryRecord | null> {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      // Anonymous user — do not persist
      return null;
    }

    const { crop, market, state, district, predictionDate, predictionResponse } = params;
    
    // Calculate 7-day or horizon stats
    const currentPrice = predictionResponse.latest_observed_price || 0;
    const predictions = predictionResponse.predictions || [];
    const predictedPrices = predictions.map((p) => p.predicted_modal_price).filter((p) => typeof p === 'number');

    const firstPredicted = predictedPrices[0] ?? currentPrice;
    const minPrice = predictedPrices.length > 0 ? Math.min(...predictedPrices) : currentPrice;
    const maxPrice = predictedPrices.length > 0 ? Math.max(...predictedPrices) : currentPrice;

    const payload = {
      user_id: user.id,
      crop: crop,
      market: market,
      state: state || 'Andhra Pradesh',
      district: district || '',
      current_price: currentPrice,
      predicted_price: firstPredicted,
      min_price: minPrice,
      max_price: maxPrice,
      trend: predictionResponse.trend_direction || 'stable',
      forecast_days: predictions.length || 7,
      prediction_date: predictionDate || new Date().toISOString().split('T')[0],
      model_name: `${predictionResponse.model_name || 'CatBoost'} v${predictionResponse.model_version || '1.0'}`,
    };

    try {
      const { data, error } = await supabase
        .from('prediction_history')
        .insert(payload)
        .select()
        .single();

      if (error) {
        console.warn('Failed to save prediction to Supabase:', error.message);
        return null;
      }
      return data as PredictionHistoryRecord;
    } catch (e) {
      console.warn('Error inserting prediction history:', e);
      return null;
    }
  },

  /**
   * Fetch all price predictions for the authenticated user
   */
  async fetchHistory(limit: number = 50): Promise<PredictionHistoryRecord[]> {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return [];

    const { data, error } = await supabase
      .from('prediction_history')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Failed to fetch prediction history:', error.message);
      return [];
    }

    return (data || []) as PredictionHistoryRecord[];
  },

  /**
   * Delete a prediction record
   */
  async deleteRecord(id: string): Promise<boolean> {
    const { error } = await supabase
      .from('prediction_history')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Failed to delete prediction record:', error.message);
      return false;
    }
    return true;
  },
};
