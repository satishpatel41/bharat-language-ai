from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5-5"
    whisper_model: str = "small"

    max_image_bytes: int = 5 * 1024 * 1024
    max_audio_bytes: int = 25 * 1024 * 1024
    max_video_bytes: int = 100 * 1024 * 1024
    ffmpeg_timeout_seconds: int = 300

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
