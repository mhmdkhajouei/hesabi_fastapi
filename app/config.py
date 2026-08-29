from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.:3000",
        "http://localhost:8080",
    ]

    env: str = "development"
    log_level: str = "DEBUG"

    db_user: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_password: str
    db_name: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
