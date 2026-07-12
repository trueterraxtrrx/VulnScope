from pydantic import AnyHttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+psycopg://vulnscope:vulnscope@postgres:5432/vulnscope"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 8
    cors_origins: list[AnyHttpUrl | str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def validate_production_security(self):
        if self.environment.lower() in {"production", "prod"}:
            if self.secret_key in {"change-me", "change-me-in-production", "secret"}:
                raise ValueError("secret_key must be replaced before production deployment")
            if "*" in self.cors_origins:
                raise ValueError("Wildcard CORS origins are not allowed in production")
        return self


settings = Settings()
# Project version: VulnScope V1.5

