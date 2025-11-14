"""Configuration management for the application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    
    # Google Gemini API
    gemini_api_key: str
    
    # Scraping Configuration
    scraping_delay_seconds: int = 2
    max_retries: int = 3
    
    # Railway Configuration
    railway_environment: Optional[str] = None
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

