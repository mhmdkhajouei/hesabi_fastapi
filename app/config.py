import os
from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

_raw_env = os.getenv("ENV", "development").lower()
ENV_FILE = f".env.{_raw_env}" if _raw_env != "development" else ".env"


class Settings(BaseSettings):
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]

    env: Literal["development", "test", "production"] = "development"
    log_level: str = "DEBUG"

    db_user: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_password: str
    db_name: str

    jwt_private_key_path: Path = Path("certs/private_key.pem")
    jwt_public_key_path: Path = Path("certs/public_key.pem")
    jwt_algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @cached_property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @cached_property
    def private_key(self) -> str:
        return self.jwt_private_key_path.read_text().strip()

    @cached_property
    def public_key(self) -> str:
        return self.jwt_public_key_path.read_text().strip()


settings = Settings()
