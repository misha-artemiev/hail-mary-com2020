"""Manages database connection for the entire server."""

from collections.abc import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from internal.logger.logger import logger
from internal.settings.env import database_settings


class DatabaseManager:
    """Starts, keeps and serves connections."""

    engine: AsyncEngine

    async def initialise(self) -> None:
        """Starts and checks connection pool.

        Raises:
          Exception: if failed to connect to the database
        """
        credentials: str = f"{database_settings.username}:{database_settings.password}"
        full_host: str = f"{database_settings.host}:{database_settings.port}"
        self.engine = create_async_engine(
            f"postgresql+psycopg://{credentials}@{full_host}/"
            f"{database_settings.database}",
            pool_size=database_settings.pool_size,
            max_overflow=database_settings.max_overflow,
            pool_pre_ping=True,
            pool_recycle=2600,
        )

        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except SQLAlchemyError as err:
            raise Exception(f"Failed to initiate connection with database: {err}")

    async def cleanup(self) -> None:
        """Closes database connection."""
        if self.engine:
            await self.engine.dispose()

    async def get_connection(self) -> AsyncGenerator[AsyncConnection]:
        """Gets connection session and returns it for dependency use.

        Yields:
          connection session with auto close and auto commit

        Raises:
          HTTPException: user facing error if failed to process database request
        """
        try:
            async with self.engine.begin() as conn:
                yield conn
        except OperationalError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable",
            )
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict")
        except ValueError as err:
            logger.error(f"Validation Error: {err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Validation error"
            )


database_manager = DatabaseManager()
