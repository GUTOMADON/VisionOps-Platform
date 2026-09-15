-- VisionOps Platform - Database schema
-- PostgreSQL initialization script. Executed automatically by the postgres
-- Docker image on first container startup (files mounted in
-- /docker-entrypoint-initdb.d run in alphabetical order).

-- Enable UUID generation used for primary keys.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- media_assets stores every uploaded image or video processed by the API.
-- Detections always reference a media asset so the raw input can be traced
-- back for auditing or re-processing.
CREATE TABLE IF NOT EXISTS media_assets (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_type         VARCHAR(10) NOT NULL CHECK (media_type IN ('image', 'video')),
    original_filename  VARCHAR(255) NOT NULL,
    storage_path       VARCHAR(500) NOT NULL,
    content_type       VARCHAR(100),
    size_bytes         BIGINT,
    width              INTEGER,
    height             INTEGER,
    duration_seconds   NUMERIC(10, 3),
    uploaded_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- detections stores one row per object detected by the model in a given
-- media asset (or a given video frame). This is the core event table that
-- the dashboard and aggregate statistics are built on top of.
CREATE TABLE IF NOT EXISTS detections (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_asset_id   UUID NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,
    frame_index      INTEGER NOT NULL DEFAULT 0,
    frame_timestamp  NUMERIC(10, 3),
    class_name       VARCHAR(100) NOT NULL,
    class_id         INTEGER NOT NULL,
    confidence       NUMERIC(5, 4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    bbox_x_min       NUMERIC(10, 4) NOT NULL,
    bbox_y_min       NUMERIC(10, 4) NOT NULL,
    bbox_x_max       NUMERIC(10, 4) NOT NULL,
    bbox_y_max       NUMERIC(10, 4) NOT NULL,
    is_violation     BOOLEAN NOT NULL DEFAULT false,
    model_name       VARCHAR(100) NOT NULL,
    model_version    VARCHAR(50) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- inference_jobs tracks one API request (image or video). A video request
-- produces many detection rows but a single job row, which lets the API
-- report per request aggregate stats (processing time, frame count, etc).
CREATE TABLE IF NOT EXISTS inference_jobs (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_asset_id     UUID NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,
    status             VARCHAR(20) NOT NULL DEFAULT 'completed'
                       CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    total_frames       INTEGER NOT NULL DEFAULT 1,
    total_detections   INTEGER NOT NULL DEFAULT 0,
    total_violations   INTEGER NOT NULL DEFAULT 0,
    processing_time_ms INTEGER,
    error_message      TEXT,
    started_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_detections_media_asset_id ON detections(media_asset_id);
CREATE INDEX IF NOT EXISTS idx_detections_created_at ON detections(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_detections_class_name ON detections(class_name);
CREATE INDEX IF NOT EXISTS idx_detections_is_violation ON detections(is_violation);
CREATE INDEX IF NOT EXISTS idx_inference_jobs_media_asset_id ON inference_jobs(media_asset_id);
CREATE INDEX IF NOT EXISTS idx_inference_jobs_started_at ON inference_jobs(started_at DESC);

-- Convenience view used by the /stats endpoints to summarize detections
-- per class without repeating aggregation logic across the codebase.
CREATE OR REPLACE VIEW detection_class_summary AS
SELECT
    class_name,
    COUNT(*)                                   AS total_detections,
    COUNT(*) FILTER (WHERE is_violation)        AS total_violations,
    ROUND(AVG(confidence)::numeric, 4)          AS avg_confidence,
    MAX(created_at)                             AS last_seen_at
FROM detections
GROUP BY class_name;
