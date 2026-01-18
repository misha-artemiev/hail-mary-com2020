from fastapi import FastAPI
from internal.settings import Host_Settings

host_settings = Host_Settings()

app = FastAPI(
    title = host_settings.name,
    version = host_settings.version,
    root_path=f"/api/{host_settings.api_version}"
)

