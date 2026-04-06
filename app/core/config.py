from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    development = "development"
    production = "production"
    test = "test"


class DefaultMode(str, Enum):
    local_first = "local_first"
    cloud_first = "cloud_first"
    cheapest = "cheapest"
    strongest = "strongest"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_env: AppEnv = AppEnv.development
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://jeeves:jeeves@localhost:5432/jeeves"

    # Security
    api_key: str = "dev-secret-key"

    # LLM Routing
    default_mode: DefaultMode = DefaultMode.local_first
    enable_cloud_fallback: bool = True
    mock_provider_enabled: bool = False

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_default: str = "llama3"
    ollama_timeout_seconds: int = 30

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model_default: str = "openai/gpt-4o-mini"
    openrouter_timeout_seconds: int = 60

    # Tools
    tool_shell_enabled: bool = False
    tool_filesystem_enabled: bool = False
    tool_http_enabled: bool = False

    # Safety
    self_modification_enabled: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
