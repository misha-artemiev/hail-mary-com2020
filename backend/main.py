from fastapi import FastAPI
from uvicorn import run
from contextlib import asynccontextmanager
from internal.settings import host_settings
from internal.database import database_manager
from internal.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialising database engine")
    err = database_manager.initialise()
    if err:
        logger.error(err.args)
        raise
    logger.info("Database ready")

    yield


    logger.info("Cleaning database engine")
    database_manager.cleanup()

app = FastAPI(
    title = host_settings.name,
    version = host_settings.version,
    root_path="/api",
    lifespan=lifespan
)

if __name__ == "__main__":
    run(app, host=host_settings.host, forwarded_allow_ips=host_settings.forward_from, port=host_settings.port, log_level="info")
