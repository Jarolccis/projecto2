"""Authentication middleware for FastAPI application."""

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.interfaces.dependencies.auth_dependencies import security
import logging
from starlette.responses import PlainTextResponse

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: list[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs", "/redoc", "/openapi.json", "/health", "/", "/favicon.ico"
            # Removed "/api/v1/clients" - let it authenticate normally
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        path = request.url.path
        logger.info(f"Processing path: {path}")

        # Bypass preflight OPTIONS
        if request.method == "OPTIONS" or "access-control-request-method" in request.headers:
            logger.info("Skipping auth for CORS preflight")
            # return PlainTextResponse("", status_code=204)
            return await call_next(request)
        
        # Check if path exactly matches excluded paths or is a health endpoint
        if path in self.exclude_paths:
            logger.info(f"Skipping authentication for excluded path: {path}")
            return await call_next(request)
        
        # Extract headers - try both standard and lowercase
        country = request.headers.get("country")
        authorization = request.headers.get("Authorization") or request.headers.get("authorization")
        
        logger.info(f"Country header: {country}, Authorization header present: {authorization is not None}")
        
        if not country:
            raise HTTPException(status_code=422, detail="Missing country header")
        
        try:
            # Use your existing security function
            logger.info("Calling security function...")
            user = await security(country, authorization)
            logger.info(f"User authenticated: {user.email if user else 'None'}")
            request.state.user = user
        except HTTPException as e:
            logger.error(f"HTTPException in security: {e.status_code}: {e.detail}")
            # Return a proper HTTP response instead of re-raising
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Exception in security: {str(e)}", exc_info=True)
            # Return a proper HTTP response for unexpected errors
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": f"Authentication failed: {str(e)}"}
            )
        
        return await call_next(request)
