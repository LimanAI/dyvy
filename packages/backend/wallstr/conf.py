from enum import Enum
from typing import Literal, cast

import tomllib
from pydantic import HttpUrl, SecretStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_version() -> str:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        return cast(str, data["tool"]["poetry"]["version"])


class Env(str, Enum):
    dev = "dev"
    prod = "prod"
    test = "test"


class JWTSettings(BaseSettings):
    issuer: str = "https://github.com/limanAI/wallstr"
    algorithm: Literal["HS512"] = "HS512"
    access_token_expire_minutes: int = 60
    access_token_renewal_leeway_days: int = 3
    refresh_token_expire_days: int = 7


class Settings(BaseSettings):
    VERSION: str = get_version()
    ENV: Env = Env.dev
    DEBUG: bool = False
    DEBUG_SQL: bool = False

    # Required
    SECRET_KEY: SecretStr
    DATABASE_URL: SecretStr
    RABBITMQ_URL: SecretStr
    REDIS_URL: SecretStr
    STORAGE_URL: HttpUrl
    STORAGE_BUCKET: str
    STORAGE_ACCESS_KEY: SecretStr
    STORAGE_SECRET_KEY: SecretStr
    OPENAI_API_KEY: SecretStr

    # Optional
    UNSTRUCTURED_API_KEY: SecretStr | None = None
    WEAVIATE_API_URL: SecretStr | None = None
    WEAVIATE_GRPC_URL: SecretStr | None = None

    CORS_ALLOW_ORIGINS: list[str] = []

    # JWT
    JWT: JWTSettings = JWTSettings()

    @field_validator(
        "SECRET_KEY",
        "DATABASE_URL",
        "RABBITMQ_URL",
        "REDIS_URL",
        "STORAGE_URL",
        "STORAGE_BUCKET",
        "STORAGE_ACCESS_KEY",
        "STORAGE_SECRET_KEY",
        "OPENAI_API_KEY",
        mode="before",
    )
    @classmethod
    def check_not_empty(cls, value: str, info: ValidationInfo) -> str:
        if not value.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return value

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


# https://github.com/pydantic/pydantic/issues/3753
settings = Settings.model_validate({})
