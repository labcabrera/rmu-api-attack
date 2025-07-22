import os
from typing import Optional

class Settings:
    """Application settings and configuration"""
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "rmu-attack")
    
    # API Configuration
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    # Application Configuration
    APP_NAME: str = "RMU API Attack"
    APP_DESCRIPTION: str = "API for managing RMU (Role Master Unified) attack system"
    APP_VERSION: str = "1.0.0"
    
    # Development Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        case_sensitive = True

# Global settings instance
settings = Settings()
