// Types mirroring the backend Pydantic schemas in backend/app/schemas/detection.py.
// Kept in sync manually since this project does not generate a client from
// the OpenAPI schema, to keep the frontend build independent of the backend.

export interface MediaAsset {
  id: string;
  media_type: "image" | "video";
  original_filename: string;
  content_type: string | null;
  size_bytes: number | null;
  width: number | null;
  height: number | null;
  duration_seconds: number | null;
  uploaded_at: string;
}

export interface Detection {
  id: string;
  media_asset_id: string;
  frame_index: number;
  frame_timestamp: number | null;
  class_name: string;
  class_id: number;
  confidence: number;
  bbox_x_min: number;
  bbox_y_min: number;
  bbox_x_max: number;
  bbox_y_max: number;
  is_violation: boolean;
  model_name: string;
  model_version: string;
  created_at: string;
}

export interface DetectionListResponse {
  total: number;
  limit: number;
  offset: number;
  items: Detection[];
}

export interface InferenceResponse {
  job_id: string;
  media_asset: MediaAsset;
  status: string;
  total_frames: number;
  total_detections: number;
  total_violations: number;
  processing_time_ms: number;
  detections: Detection[];
}

export interface ClassSummary {
  class_name: string;
  total_detections: number;
  total_violations: number;
  avg_confidence: number | null;
  last_seen_at: string | null;
}

export interface StatsSummaryResponse {
  total_media_assets: number;
  total_detections: number;
  total_violations: number;
  compliance_rate: number;
  by_class: ClassSummary[];
}

export interface TimeseriesPoint {
  bucket_start: string;
  total_detections: number;
  total_violations: number;
}

export interface StatsTimeseriesResponse {
  interval: string;
  points: TimeseriesPoint[];
}

export interface DetectionFilters {
  class_name?: string;
  is_violation?: boolean;
  limit?: number;
  offset?: number;
}
