from sqlalchemy import create_engine, Engine, text
from internal.settings import database_settings

class DatabaseManager:
    engine: Engine

    def initialise(self) -> None | Exception:
        self.engine = create_engine(
            f"postgresql+psycopg://{database_settings.username}:{database_settings.password}@{database_settings.host}:{database_settings.port}/{database_settings.database}",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=2600
        )
    
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            return Exception("Failed to initiate connection with database")

    def get_engine(self) -> Engine | Exception:
        if self.engine:
            return self.engine
        return Exception("No engine found")

    def cleanup(self):
        if self.engine:
            self.engine.dispose()

database_manager = DatabaseManager()
