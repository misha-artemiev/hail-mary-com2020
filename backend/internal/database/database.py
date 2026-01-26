from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException
from internal.logging import logger
from internal.settings import database_settings
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.exc import IntegrityError, OperationalError


class DatabaseManager:
    engine: Engine

    def initialise(self) -> None | Exception:
        self.engine = create_engine(
            f"postgresql+psycopg://{database_settings.username}:{database_settings.password}@{database_settings.host}:{database_settings.port}/{database_settings.database}",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=2600,
        )

        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            return Exception("Failed to initiate connection with database")
        return None

    def cleanup(self) -> None:
        if self.engine:
            self.engine.dispose()

    def get_connection(self) -> Generator[Connection]:
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
        except Exception as err:
            logger.error(f"Internal Error: {err}")
            raise HTTPException(500, "Internal Error")


database_manager = DatabaseManager()
database_dependency = Annotated[Connection, Depends(database_manager.get_connection)]
