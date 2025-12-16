"""
Environment configuration for NFT Software Engine
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "NFT Software Engine"
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    
    # Server
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8501"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        "sqlite:///./nft_engine.db",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        "redis://localhost:6379",
        env="REDIS_URL"
    )
    
    # Blockchain
    WEB3_PROVIDER_URL: str = Field(
        "https://polygon-mumbai.g.alchemy.com/v2/",
        env="WEB3_PROVIDER_URL"
    )
    PRIVATE_KEY: Optional[str] = Field(None, env="PRIVATE_KEY")
    PUBLIC_KEY: Optional[str] = Field(None, env="PUBLIC_KEY")
    GAS_PRICE: str = Field("20", env="GAS_PRICE")
    GAS_LIMIT: int = Field(300000, env="GAS_LIMIT")
    
    # Smart Contracts
    CONTRACT_FACTORY_ADDRESS: Optional[str] = Field(None, env="CONTRACT_FACTORY_ADDRESS")
    NFT_BASE_URI: str = Field("https://api.nft-engine.com/metadata/", env="NFT_BASE_URI")
    
    # Authentication
    JWT_SECRET_KEY: str = Field(
        "your-secret-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(24, env="JWT_EXPIRATION_HOURS")
    
    # External Services
    AUTH_SERVICE_URL: str = Field(
        "http://localhost:8001",
        env="AUTH_SERVICE_URL"
    )
    
    # Payment Integration
    STRIPE_PUBLIC_KEY: Optional[str] = Field(None, env="STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY: Optional[str] = Field(None, env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(None, env="STRIPE_WEBHOOK_SECRET")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(3600, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Analytics
    ANALYTICS_RETENTION_DAYS: int = Field(365, env="ANALYTICS_RETENTION_DAYS")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
