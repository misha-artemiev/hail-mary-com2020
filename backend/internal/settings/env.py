"""Loaded settings from environment."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class HostSettings(BaseSettings):
    """Settings for main server module."""

    host: str = "localhost"
    port: int = 8080
    name: str = "hail mary"
    forward_from: str = "*"

    model_config = SettingsConfigDict(
        env_prefix="HOST_",
        case_sensitive=False,
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class DatabaseSettings(BaseSettings):
    """Settings for database connection."""

    host: str = "localhost"
    port: int = 3306
    username: str = "hail-mary"
    password: str = ""
    database: str = "hail-mary"
    pool_size: int = 20
    max_overflow: int = 10

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        case_sensitive=False,
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class AuthSettings(BaseSettings):
    """Settings for authentication hardness."""

    token_exparation: int = 360

    model_config = SettingsConfigDict(
        env_prefix="AUTH",
        case_sensitive=False,
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


host_settings = HostSettings()
database_settings = DatabaseSettings()
auth_settings = AuthSettings()
