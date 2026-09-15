# Backend API

FastAPI service that loads the trained YOLOv8 safety detection model, runs inference on uploaded images and video, persists every detection to PostgreSQL, and exposes history and aggregate statistics for the dashboard.

## Endpoints

All routes are served under `/api/v1`.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check. |
| GET | `/health/ready` | Readiness check, verifies the database connection. |
| POST | `/inference/image` | Run detection on an uploaded image, persist and return the detections. |
| POST | `/inference/video` | Run detection on sampled frames of an uploaded video, persist and return the detections. |
| GET | `/detections` | List stored detections with filters (`class_name`, `is_violation`, `media_asset_id`, `start_date`, `end_date`) and pagination (`limit`, `offset`). |
| GET | `/detections/{id}` | Fetch a single detection. |
| GET | `/stats/summary` | Total counts, compliance rate and per class breakdown. |
| GET | `/stats/timeseries` | Detection counts bucketed by day. |

Interactive OpenAPI docs are available at `/docs` once the service is running.

## Project layout

```
app/
  main.py              FastAPI app, middleware, exception handlers, router registration
  core/config.py        Environment-based settings
  db/                   SQLAlchemy engine, session, ORM models, backend-agnostic UUID type
  schemas/               Pydantic request and response models
  services/
    model_service.py    Loads and runs the YOLOv8 model
    video_service.py     Frame sampling for video uploads
    storage_service.py   Saves uploads to disk and validates content type
  api/routes/            One module per resource (health, inference, detections, stats)
tests/                    Pytest suite using an in-memory SQLite database and a fake model service
scripts/init_db.py        Convenience script to create tables for local development
```

## Configuration

Copy the root [.env.example](../.env.example) to `.env` and adjust as needed. Key variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string, for example `postgresql+psycopg2://user:pass@host:5432/db`. |
| `MODEL_PATH` | Path to the trained checkpoint exported by `ml/src/export_model.py`. |
| `CONFIDENCE_THRESHOLD` | Minimum detection confidence to keep, default `0.35`. |
| `DEVICE` | `cpu` or a CUDA device id such as `0`. |
| `MEDIA_STORAGE_DIR` | Directory where uploaded files are saved. |
| `VIDEO_FRAME_SAMPLE_RATE` | Process every Nth frame of an uploaded video. |
| `CORS_ORIGINS` | Comma separated list of allowed frontend origins. |

## Running locally without Docker

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python scripts/init_db.py
uvicorn app.main:app --reload
```

The service expects PostgreSQL to be reachable at `DATABASE_URL`. For a quick local database without installing Postgres manually, start only the `db` service from the root compose file:

```
docker compose up -d db
```

## Running tests

```
pytest -v --cov=app
```

Tests never touch a real Postgres instance or the real model: `get_db` is overridden with an in-memory SQLite session and `get_model_service` is overridden with a deterministic fake, so the suite runs in seconds with no external dependencies. See [tests/conftest.py](tests/conftest.py).

## Linting

```
ruff check app tests
```
