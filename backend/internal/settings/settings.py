from pydantic_settings import BaseSettings, SettingsConfigDict

class Host_Settings(BaseSettings):
    host: str = "localhost"
    port: int = 8080
    name: str = "hail mary"
    version: str = "0.0.1"
    forward_from: str = "*"
    api_version: str = "v1"

    model_config = SettingsConfigDict(env_prefix="HOST_", case_sensitive=False)
