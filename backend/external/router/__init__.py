from fastapi import FastAPI
from .consumers import router as consumer_router
from .sellers import router as sellers_router
from .session import router as session_router

def register_routers(app: FastAPI):
    app.include_router(consumer_router)
    app.include_router(sellers_router)
    app.include_router(session_router)

__all__ = ["register_routers"]
