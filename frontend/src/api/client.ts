// Thin wrapper around axios for every backend call the dashboard needs.
// Centralizing requests here keeps components free of URL strings and
// makes the base URL configurable per environment through VITE_API_BASE_URL.

import axios, { AxiosError } from "axios";

import type {
  DetectionFilters,
  DetectionListResponse,
  InferenceResponse,
  StatsSummaryResponse,
  StatsTimeseriesResponse,
} from "../types/detection";

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const apiClient = axios.create({ baseURL });

export class ApiError extends Error {
  status: number | null;

  constructor(message: string, status: number | null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function toApiError(error: unknown): ApiError {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail as string | undefined;
    return new ApiError(detail || error.message, error.response?.status ?? null);
  }
  return new ApiError("Unexpected error contacting the API.", null);
}

export async function uploadImage(file: File): Promise<InferenceResponse> {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await apiClient.post<InferenceResponse>("/inference/image", formData);
    return response.data;
  } catch (error) {
    throw toApiError(error);
  }
}

export async function uploadVideo(file: File): Promise<InferenceResponse> {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await apiClient.post<InferenceResponse>("/inference/video", formData);
    return response.data;
  } catch (error) {
    throw toApiError(error);
  }
}

export async function listDetections(filters: DetectionFilters): Promise<DetectionListResponse> {
  try {
    const response = await apiClient.get<DetectionListResponse>("/detections", { params: filters });
    return response.data;
  } catch (error) {
    throw toApiError(error);
  }
}

export async function getStatsSummary(): Promise<StatsSummaryResponse> {
  try {
    const response = await apiClient.get<StatsSummaryResponse>("/stats/summary");
    return response.data;
  } catch (error) {
    throw toApiError(error);
  }
}

export async function getStatsTimeseries(): Promise<StatsTimeseriesResponse> {
  try {
    const response = await apiClient.get<StatsTimeseriesResponse>("/stats/timeseries");
    return response.data;
  } catch (error) {
    throw toApiError(error);
  }
}
