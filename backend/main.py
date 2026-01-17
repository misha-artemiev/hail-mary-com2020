from uvicorn import run
from app import app
from internal.settings import Host_Settings


if __name__ == "__main__":
    host_settings = Host_Settings()
    run(app, host=host_settings.host, forwarded_allow_ips=host_settings.forward_from, port=host_settings.port)
