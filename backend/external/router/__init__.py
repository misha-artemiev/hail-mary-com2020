from fastapi import FastAPI
from .consumers import router as consumer_router
from .sellers import router as sellers_router

def register_routers(app: FastAPI):
    app.include_router(consumer_router)
    app.include_router(sellers_router)

__all__ = ["register_routers"]
