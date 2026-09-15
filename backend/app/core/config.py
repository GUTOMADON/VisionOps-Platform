"""Application configuration loaded from environment variables.

Uses pydantic-settings so every value has a validated type and a sane
default for local development, while still being fully overridable through
the environment in Docker Compose or a cloud deployment.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", protected_namespaces=("settings_",)
    )

    # General
    app_name: str = "VisionOps Platform API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+psycopg2://visionops:visionops@localhost:5432/visionops"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Model serving
    model_path: str = str(Path(__file__).resolve().parents[3] / "ml" / "models" / "visionops_ppe.pt")
    confidence_threshold: float = 0.35
    device: str = "cpu"

    # Media storage
    media_storage_dir: str = str(Path(__file__).resolve().parents[3] / "backend" / "media")
    max_upload_size_mb: int = 100
    video_frame_sample_rate: int = 5  # process every Nth frame for video uploads

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
