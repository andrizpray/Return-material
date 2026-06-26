from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    APP_NAME: str = "Return Material Manager"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # SQLite
    DB_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "return_material.db")

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///{self.DB_PATH}"

    # File uploads
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Pagination
    PAGE_SIZE: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
