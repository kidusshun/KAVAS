import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(".env")

class Settings(BaseModel):
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")