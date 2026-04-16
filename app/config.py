"""Configuration management for the application."""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    
    # AI API keys
    # Keep gemini_api_key for backward compatibility with older deployments/env vars.
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Scraping Configuration
    scraping_delay_seconds: int = 2
    max_retries: int = 3
    
    # Railway Configuration
    railway_environment: Optional[str] = None
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @model_validator(mode="after")
    def validate_ai_keys(self):
        """Allow either OPENAI_API_KEY or legacy GEMINI_API_KEY."""
        if not self.openai_api_key and self.gemini_api_key:
            self.openai_api_key = self.gemini_api_key

        if not self.openai_api_key:
            raise ValueError("Either OPENAI_API_KEY or GEMINI_API_KEY must be set")

        return self


# Global settings instance
settings = Settings()

