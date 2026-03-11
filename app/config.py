from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # LLM API Keys (use one of these)
    gemini_api_key: Optional[str] = None  # Google Gemini (free tier available)
    openrouter_api_key: Optional[str] = None  # OpenRouter (paid)
    
    # Database
    database_url: str = "sqlite:///./counterparty_engine.db"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
