from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List

class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db: str = Field(default="portfolio_allocation", alias="MONGODB_DB")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")

    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    @field_validator('cors_origins')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',')]
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }

settings = Settings()