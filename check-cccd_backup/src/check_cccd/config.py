from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/check_cccd"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API Security
    api_key: Optional[str] = None
    secret_key: str = "your-secret-key-change-in-production"
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Scraping
    request_timeout: float = 15.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Cache
    cache_ttl_seconds: int = 3600  # 1 hour
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Monitoring
    enable_metrics: bool = True
    sentry_dsn: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()