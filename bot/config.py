import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    ADMIN_ID: int = 0
    WEBHOOK_SECRET: str = "anilo_uz_secret"
    APP_URL: str = ""
    
    # Chunk size for broadcast
    BROADCAST_CHUNK_SIZE: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

config = Settings()
