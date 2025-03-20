from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base Settings
    PROJECT_NAME: str = "Email Warmup System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB Settings
    MONGODB_URL: str
    DATABASE_NAME: str
    
    # JWT Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
