import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(".env")

class Settings(BaseModel):
    DB_USER: str = os.environ.get("DB_USER", "")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
    DB_HOST: str = os.environ.get("DB_HOST", "")
    DB_PORT: str = os.environ.get("DB_PORT", "")
    DB_NAME: str = os.environ.get("DB_NAME", "")
    DB_CONNECTION_TIMEOUT: int = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))
    DB_POOL_MIN_SIZE: int = int(os.getenv("DB_POOL_MIN_SIZE", "1"))
    DB_POOL_MAX_SIZE: int = int(os.getenv("DB_POOL_MAX_SIZE", "10"))
    
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

MySettings = Settings()