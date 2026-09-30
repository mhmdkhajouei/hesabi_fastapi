from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class EnvironmentSettings(BaseSettings):
    env: Literal["development", "test", "production"] = "development"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


active_env = EnvironmentSettings().env

ENV_FILES = {
    "development": ".env",
    "test": ".env.test",
    "production": ".env.production",
}


class Settings(BaseSettings):
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]

    env: str = active_env
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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
