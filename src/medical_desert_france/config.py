from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite+pysqlite:///:memory:"
    mlflow_tracking_uri: str = "http://localhost:5000"
    model_artifact_path: str = "local_models/model.joblib"
    model_version: str = "local"
    cors_origins: list[AnyHttpUrl | str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
