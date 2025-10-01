"""Main FastAPI application entry point."""
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.logging import LoggerMixin, setup_logging
from app.core.middleware import (
    general_exception_handler,
    http_exception_handler,
    request_logging_middleware,
    validation_exception_handler,
    AuthMiddleware,
)
from app.core.app_lifespan import AppLifecycle
from app.interfaces.api.routers import create_api_router
from app.interfaces.api.controllers.healthy_controller  import router as healthy_router 

lifecycle = AppLifecycle()
class ApplicationManager(LoggerMixin):
    """Manager for FastAPI application with logging capabilities."""

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        # Setup logging first
        setup_logging()
        self.log_info("Starting application initialization")
        #region Create Instance
        app = FastAPI(
            title=settings.app_name,
            version=settings.app_version,
            debug=settings.debug,
            description="A secure CRUD API for managing stores built with clean architecture",
            docs_url="/docs" if settings.debug else None,  # Hide docs in production
            redoc_url="/redoc" if settings.debug else None,  # Hide redoc in production
            lifespan=lifecycle.lifespan  # Use modern lifespan handler
        )
        #endregion

        #region State
        # Store settings in app state for access in middleware
        app.state.settings = settings
        #endregion

        #region Middleware
        # Add CORS middleware with secure configuration
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,  # Dynamic CORS origins
            allow_credentials=settings.cors_allow_credentials,  # False by default
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Accept", "country"],
            expose_headers=[],
        )

        # Add authentication middleware
        app.add_middleware(
            AuthMiddleware,
            exclude_paths=["/docs", "/redoc", "/openapi.json", "/status/health", "/"]
        )

        # Add custom middleware in order
        app.middleware("http")(request_logging_middleware)  # Log all requests

        #endregion



        #region Router
        # # Include all routers using the centralized router system
        # # Each router now manages its own prefix (versioning)
        api_router = create_api_router()
        app.include_router(api_router)   

        #endregion

        #region Exception Handlers
        # Add exception handlers for standardized error responses
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        app.add_exception_handler(StarletteHTTPException, http_exception_handler)
        app.add_exception_handler(Exception, general_exception_handler)
        #endregion



        self.log_info("Application configuration completed")
        return app


# Create the application instance
app_manager = ApplicationManager() 

app =  app_manager.create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,  # Only enable reload in debug mode
        log_level=settings.log_level,
        access_log=True,
    )
