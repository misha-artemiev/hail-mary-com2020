from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Host_Settings(BaseSettings):
    host: str = "localhost"
    port: int = 8080
    name: str = "hail mary"
    version: str = "0.0.1"
    forward_from: str = "*"

    model_config = SettingsConfigDict(env_prefix="HOST_", case_sensitive=False, env_file=BASE_DIR/".env")

class Database_Settings(BaseSettings):
    host: str = "localhost"
    port: int = 3306
    username: str = "hail-mary"
    password: str = ""
    database: str = "hail-mary"

    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False, env_file=BASE_DIR/".env")
