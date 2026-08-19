import { api } from '../api';
import type {
  DiseaseAnalysisResponse,
  DiseaseHistoryListResponse,
  DiseaseHistoryItem,
} from '../types/disease';

export interface AnalyzeCropRequest {
  imageFile?: File;
  imageFiles?: File[];
  crop?: string;
  plantPart?: string;
  symptoms?: string;
  notes?: string;
  location?: string;
  growthStage?: string;
  language?: string;
}

export interface DiseaseHistoryFilter {
  crop?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export async function analyzeCrop(
  req: AnalyzeCropRequest,
  signal?: AbortSignal
): Promise<DiseaseAnalysisResponse> {
  const formData = new FormData();
  
  // Single or multiple image append
  if (req.imageFiles && req.imageFiles.length > 0) {
    req.imageFiles.slice(0, 3).forEach((f) => {
      formData.append('files', f);
    });
    formData.append('file', req.imageFiles[0]);
  } else if (req.imageFile) {
    formData.append('file', req.imageFile);
    formData.append('files', req.imageFile);
  }

  if (req.crop) formData.append('crop', req.crop);
  if (req.plantPart) formData.append('plant_part', req.plantPart);
  if (req.symptoms) formData.append('symptoms', req.symptoms);
  if (req.notes) formData.append('notes', req.notes);
  if (req.location) formData.append('location', req.location);
  if (req.growthStage) formData.append('growth_stage', req.growthStage);
  if (req.language) formData.append('language', req.language);

  const res = await api.post<DiseaseAnalysisResponse>('/disease/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    signal,
  });
  return res.data;
}

export async function fetchDiseaseHistory(
  filter?: DiseaseHistoryFilter,
  signal?: AbortSignal
): Promise<DiseaseHistoryListResponse> {
  const res = await api.get<DiseaseHistoryListResponse>('/disease/history', {
    params: filter,
    signal,
  });
  return res.data;
}

export async function fetchDiseaseHistoryDetail(
  analysisId: string,
  signal?: AbortSignal
): Promise<DiseaseHistoryItem> {
  const res = await api.get<DiseaseHistoryItem>(`/disease/history/${analysisId}`, {
    signal,
  });
  return res.data;
}

export async function deleteDiseaseHistory(
  analysisId: string
): Promise<{ success: boolean; message: string }> {
  const res = await api.delete<{ success: boolean; message: string }>(
    `/disease/history/${analysisId}`
  );
  return res.data;
}

export function getDiseaseImageUrl(analysisId: string): string {
  const token = localStorage.getItem('cropmandi_auth_token');
  const rawBase = (import.meta as any).env?.VITE_API_BASE_URL;
  const baseUrl = rawBase
    ? `${rawBase.replace(/\/+$/, '')}/api/v1`
    : 'http://127.0.0.1:8000/api/v1';
  return token
    ? `${baseUrl}/disease/image/${analysisId}?token=${encodeURIComponent(token)}`
    : `${baseUrl}/disease/image/${analysisId}`;
}
