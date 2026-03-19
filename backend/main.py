"""Fastapi server entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import APIRouter, Depends, FastAPI
from internal.auth.security import log_request
from internal.block.management import block_management
from internal.database.manager import database_manager
from internal.logger.logger import logger
from internal.settings.config import badges_config
from internal.settings.env import host_settings
from routers.admins import router as admin_router
from routers.allergens import router as allergens_router
from routers.badges import router as badges_router
from routers.bundles import router as bundle_router
from routers.categories import router as categories_router
from routers.consumers import router as consumers_router
from routers.leaderboard import router as leaderboard_router
from routers.reports import router as reports_router
from routers.sellers import router as sellers_router
from routers.sessions import router as sessions_router
from routers.users import router as users_router
from uvicorn import run


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manages startup and shutdown."""
    badges_config.initialise()
    logger.info("Initialising database engine")
    await database_manager.initialise()
    logger.info("Database ready")
    logger.info("Initialising block storage")
    block_management.initialise()
    logger.info("Block storage ready")

    yield

    logger.info("Cleaning database engine")
    await database_manager.cleanup()


app = FastAPI(
    title=host_settings.name,
    version=version("rescue-marketplace"),
    root_path="/api",
    lifespan=lifespan,
)


def register_routers(app: FastAPI) -> None:
    """Registers api routers with the app."""
    routers: list[APIRouter] = [
        consumers_router,
        sellers_router,
        bundle_router,
        sessions_router,
        users_router,
        allergens_router,
        categories_router,
        badges_router,
        admin_router,
        reports_router,
        leaderboard_router,
    ]
    for router in routers:
        app.include_router(router, dependencies=[Depends(log_request)])


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
