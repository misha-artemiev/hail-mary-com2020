"""Fastapi server entrypoint."""

from asyncio import to_thread
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import FastAPI
from internal.database.manager import database_manager
from internal.logger.logger import logger
from internal.settings.env import host_settings
from routers.consumers import router as consumers_router
from routers.sellers import router as sellers_router
from routers.sessions import router as sessions_router
from routers.bundles import router as bundle_router
from uvicorn import run


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manages startup and shutdown."""
    logger.info("Initialising database engine")
    await to_thread(database_manager.initialise)
    logger.info("Database ready")

    yield

    logger.info("Cleaning database engine")
    database_manager.cleanup()


app = FastAPI(
    title=host_settings.name,
    version=version("rescue-marketplace"),
    root_path="/api",
    lifespan=lifespan,
)


def register_routers(app: FastAPI) -> None:
    """Registers api routers with the app."""
    app.include_router(consumers_router)
    app.include_router(sellers_router)
    app.include_router(sessions_router)
    app.include_router(bundle_router)


register_routers(app)

if __name__ == "__main__":
    run(
        app,
        host=host_settings.host,
        forwarded_allow_ips=host_settings.forward_from,
        port=host_settings.port,
        log_level="info",
        loop="uvloop",
    )
