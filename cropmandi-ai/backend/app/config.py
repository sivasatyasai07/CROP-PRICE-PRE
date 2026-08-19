import os
from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    APP_NAME: str = "CropMandi AI"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_TIMEZONE: str = "Asia/Kolkata"
    SECRET_KEY: str = "cropmandi-secret-key-change-in-production"
    AUTH_SECRET_KEY: str = "cropmandi-super-secret-key-change-in-production-2026"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    USERS_JSON_PATH: str = "data/users.json"
    MASTER_DATA_PATH: str = "data/master-data.csv"
    DEMO_MODE: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./cropmandi.db"
    
    # Official Data API (data.gov.in)
    DATA_GOV_API_KEY: str = ""
    DATA_GOV_RESOURCE_ID: str = "/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"
    DATA_GOV_BASE_URL: str = "https://api.data.gov.in"
    DATA_GOV_TIMEOUT_SECONDS: int = 30
    DATA_GOV_MAX_RETRIES: int = 2
    DATA_GOV_RATE_LIMIT_DELAY: float = 0.5
    DATA_GOV_PAGE_SIZE: int = 1000
    DATA_GOV_MAX_SYNC_HOURS: int = 24
    DATA_GOV_MOCK_FALLBACK: bool = False
    
    # Official API Verification & Live Fetch
    DYNAMIC_DATA_GOV_FETCH: bool = True
    MAX_HISTORICAL_DAYS_FETCH: int = 3
    FORCE_REFRESH_ON_GENERATE: bool = True
    
    # Weather
    WEATHER_API_URL: str = "https://api.open-meteo.com/v1"
    WEATHER_HISTORICAL_API_URL: str = "https://archive-api.open-meteo.com/v1"
    
    # PlantNet API Configuration
    PLANTNET_API_KEY: str = ""
    PLANTNET_BASE_URL: str = "https://my-api.plantnet.org/v2/identify"
    PLANTNET_PROJECT: str = "all"
    PLANTNET_TIMEOUT_SECONDS: int = 60
    PLANTNET_MAX_RETRIES: int = 2
    PLANTNET_MIN_SCORE: float = 0.0
    PLANTNET_MAX_IMAGE_SIZE_MB: int = 10
    DISEASE_ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"
    DISEASE_IDENTIFICATION_PROVIDER: str = "plantnet"
    DISEASE_ANALYSIS_PROVIDER: str = "gemini"
    
    # Gemini AI & Disease Detection
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_TIMEOUT_SECONDS: int = 120
    GEMINI_MAX_RETRIES: int = 2
    GEMINI_TEMPERATURE: float = 0.0
    DISEASE_PROMPT_VERSION: str = "crop-disease-v2"
    DISEASE_HIGH_CONFIDENCE_THRESHOLD: float = 0.75
    DISEASE_MEDIUM_CONFIDENCE_THRESHOLD: float = 0.45
    DISEASE_MAX_IMAGES: int = 3
    
    DISEASE_MAX_ANALYSES_PER_USER_PER_HOUR: int = 20
    DISEASE_COOLDOWN_SECONDS: int = 10
    STORE_DISEASE_IMAGES: bool = True
    DELETE_IMAGE_AFTER_ANALYSIS: bool = False
    
    GEMINI_WEIGHT: float = 0.6
    CLASSIFIER_WEIGHT: float = 0.4
    
    DISEASE_HISTORY_DIR: str = "data/disease_history"
    DISEASE_IMAGES_DIR: str = "data/disease_images"
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

DATA_GOV_API_KEY = settings.DATA_GOV_API_KEY
DATA_GOV_RESOURCE_ID = settings.DATA_GOV_RESOURCE_ID
DATA_GOV_BASE_URL = settings.DATA_GOV_BASE_URL
