"""Router database dependency."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from .manager import database_manager

database_dependency = Annotated[
    AsyncConnection, Depends(database_manager.get_connection)
]
