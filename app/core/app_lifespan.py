 # app_lifespan.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from app.core.logging import LoggerMixin
from app.infrastructure.postgres.session import check_async_database_connection

class AppLifecycle(LoggerMixin):
    """Application lifecycle manager with logging capabilities."""

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Async context manager for application lifespan.

        Args:
            app: FastAPI application instance

        Yields:
            Dict with application state (empty dict if no state needed)
        """
        # Startup
        self.log_info("� Application startup initiated")

        try:
            # Add your startup logic here
            await self._startup_events(app)
            self.log_info("✅ Application startup completed successfully")

            # Yield control to the application with empty state dict
            yield {}

        except Exception as e:
            self.log_error("❌ Application startup failed", error=e)
            # Still need to yield to prevent crash
            yield {}
        finally:
            # Shutdown
            self.log_info("🛑 Application shutdown initiated")
            try:
                await self._shutdown_events(app)
                self.log_info("✅ Application shutdown completed successfully")
            except Exception as e:
                self.log_error("❌ Application shutdown failed", error=e)

    async def _startup_events(self, app: FastAPI) -> None:
        """Handle application startup events."""
        try:
            # Database connection check
            self.log_info("🔍 Checking database connection...")

            db_ready = await check_async_database_connection()
            if db_ready:
                self.log_info("✅ Database connection successful")
            else:
                self.log_error("❌ Database connection failed")
                raise Exception("Database connection failed")

        except Exception as e:
            self.log_error("❌ Startup events failed", error=e)
            raise

    async def _shutdown_events(self, app: FastAPI) -> None:
        """Handle application shutdown events."""
        try:
            # Add cleanup logic here if needed
            self.log_info("🧹 Cleaning up resources...")
            # Example: Close database connections, cleanup caches, etc.

        except Exception as e:
            self.log_error("❌ Shutdown events failed", error=e)
            # Don't re-raise here to avoid blocking shutdown
 