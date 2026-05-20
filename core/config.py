import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    GOOGLE_MAPS_API_KEY: str

    # Location Configuration
    CENTER_LAT: float = -23.3522
    CENTER_LNG: float = -46.9185
    CITY_NAME: str = "Carapicuíba"
    STATE: str = "SP"
    COUNTRY: str = "Brazil"

    # App Configuration
    APP_NAME: str = "CloudLeads Finder"
    VERSION: str = "1.0.0"

    # Scoring Weights
    WEIGHT_NO_WEBSITE: int = 50
    WEIGHT_NO_SOCIAL: int = 20
    WEIGHT_LOW_PHOTOS: int = 10
    WEIGHT_LOW_REVIEWS: int = 10
    WEIGHT_HIGH_RATING_NO_SITE: int = 20

    class Config:
        env_file = ".env"

settings = Settings()
