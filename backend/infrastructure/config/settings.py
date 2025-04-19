from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Web Analysis System"
    API_V1_STR: str = "/api/v1"

    # Database Config (Asíncrona con asyncpg)
    # Ejemplo: postgresql+asyncpg://user:password@host:port/db
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    class Config:
        case_sensitive = True


settings = Settings()
