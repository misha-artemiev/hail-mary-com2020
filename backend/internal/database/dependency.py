"""Router database dependency."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import Connection

from .manager import database_manager

database_dependency = Annotated[Connection, Depends(database_manager.get_connection)]
