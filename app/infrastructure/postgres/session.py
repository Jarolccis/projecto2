from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import LoggerMixin

Base = declarative_base()


class AsyncDatabaseManager(LoggerMixin):
    """Fully async database manager with session and engine setup."""

    def __init__(self):
        self.async_engine = self._setup_async_engine()
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    def _setup_async_engine(self):
        """Create async engine with SSL and connection pool configuration."""
        try:
            async_url = settings.database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

            if "?" in async_url:
                base_url, params = async_url.split("?", 1)
                filtered_params = [p for p in params.split("&") if not p.startswith("ssl")]
                async_url = base_url + ("?" + "&".join(filtered_params) if filtered_params else "")
            # Configurar SSL para asyncpg
            ssl_config = {}
            if settings.postgres_ssl_mode and settings.postgres_ssl_mode != "disable":
                ssl_config["ssl"] = "require" if settings.postgres_ssl_mode == "require" else True

            engine = create_async_engine(
                async_url,
                **settings.database_engine_kwargs,
                connect_args={
                    "server_settings": {
                        "application_name": f"{settings.app_name}_{settings.app_version}",
                    },
                    **ssl_config
                }
            )

            self.log_info("Async engine created successfully", database=settings.postgres_db)
            return engine

        except Exception as e:
            self.log_error("Failed to create async engine",
                error=e,
                host=settings.postgres_host,
                port=settings.postgres_port
            )
            raise 
 
    async def check_connection(self) -> bool:
        conn = None
        try:
            conn = await self.async_engine.connect()
            await conn.execute(text("SELECT 1"))
            self.log_info("Async DB connection successful")
            return True
        except Exception as e:
            self.log_error("Async DB connection failed", error=e)
            return False
        finally:
            if conn:
                await conn.close()


    async def init_database(self) -> None:
        """Create tables asynchronously."""
        try:
            from app.infrastructure.postgres.models import StoreORM  # noqa: F401
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self.log_info("Tables created successfully")
        except Exception as e:
            self.log_error("Failed to create tables", error=e)
            raise


# Instancia global
_db_manager = AsyncDatabaseManager()

# Funciones de conveniencia 
@asynccontextmanager 
async def get_db_session():
    async with _db_manager.AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

async def check_async_database_connection() -> bool:
    return await _db_manager.check_connection()

async def init_async_database() -> None:
    await _db_manager.init_database()

AsyncSessionLocal = _db_manager.AsyncSessionLocal
async_engine = _db_manager.async_engine 