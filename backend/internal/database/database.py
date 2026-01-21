from sqlalchemy import create_engine, Engine, text
from internal.settings import database_settings
import logging

logger = logging.getLogger("uvicorn.error")

class DatabaseManager:
    engine: Engine

    def initialise(self) -> None | str:
        self.engine = create_engine(
            f"mysql+mysqlconnector://{database_settings.username}:{database_settings.password}@{database_settings.host}:{database_settings.port}/{database_settings.database}",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=2600
        )
    
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            return "Failed to initiate connection with database"

    def get_engine(self) -> Engine | None:
        if self.engine:
            return self.engine

    def cleanup(self):
        if self.engine:
            self.engine.dispose()
