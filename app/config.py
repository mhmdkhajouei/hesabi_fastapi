from functools import cached_property
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]

    env: str = "development"
    log_level: str = "DEBUG"

    db_user: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_password: str
    db_name: str

    jwt_private_key_path: Path = Path("certs/jwt_private.pem")
    jwt_public_key_path: Path = Path("certs/jwt_public.pem")
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
