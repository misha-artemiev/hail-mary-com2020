"""Manages database connection for the entire server."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException
from internal.logger import logger
from internal.settings import database_settings
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError


class DatabaseManager:
    """Starts, keeps and serves connections."""

    engine: Engine

    def initialise(self) -> None:
        """Starts and checks connection pool.

        Raises:
          Exception: if failed to connect to the database
        """
        credentials: str = f"{database_settings.username}:{database_settings.password}"
        full_host: str = f"{database_settings.host}:{database_settings.port}"
        self.engine = create_engine(
            f"postgresql+psycopg://{credentials}@{full_host}/{database_settings.database}",
            pool_size=database_settings.pool_size,
            max_overflow=database_settings.max_overflow,
            pool_pre_ping=True,
            pool_recycle=2600,
        )

        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as err:
            raise Exception(f"Failed to initiate connection with database: {err}")

    def cleanup(self) -> None:
        """Closes database connection."""
        if self.engine:
            self.engine.dispose()

    def get_connection(self) -> Generator[Connection]:
        """Gets connection session and returns it for dependency use.

        Yields:
          connection session with auto close and auto commit

        Raises:
          HTTPException: user facing error if failed to process database request
        """
        try:
            with self.engine.begin() as conn:
                yield conn
        except OperationalError:
            raise HTTPException(503, "Service unavailable")
        except IntegrityError:
            raise HTTPException(409, "Conflict")
        except ValueError as err:
            logger.error(f"Validation Error: {err}")
            raise HTTPException(400, "Validation Error")


database_manager = DatabaseManager()
database_dependency = Annotated[Connection, Depends(database_manager.get_connection)]
