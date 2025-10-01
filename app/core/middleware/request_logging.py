"""Request logging middleware for comprehensive request/response tracking."""

import time
from typing import Any, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import LoggerMixin


class RequestLoggingMiddleware(BaseHTTPMiddleware, LoggerMixin):
    """Middleware to log all requests and responses with detailed information."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with comprehensive logging."""
        start_time = time.time()
        
        # Extract request information
        request_info = self._extract_request_info(request)
        
        # Log request start
        self.log_info(
            "Request started",
            **request_info
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time in milliseconds
            process_time = round((time.time() - start_time) * 1000, 2)
            
            # Log successful response with clean fields
            self.log_info(
                "Request completed successfully",
                endpoint=request_info["endpoint"],
                method=request_info["method"],
                client_ip=request_info["client_ip"],
                status_code=response.status_code,
                process_time=process_time,
                country=request.headers.get("country")
            )
            
            return response
            
        except Exception as e:
            # Calculate processing time in milliseconds
            process_time = round((time.time() - start_time) * 1000, 2)
            
            # Log request failure with clean fields
            self.log_error(
                "Request failed",
                error=e,
                endpoint=request_info["endpoint"],
                method=request_info["method"],
                client_ip=request_info["client_ip"],
                process_time=process_time,
                country=request.headers.get("country")
            )
            raise
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract comprehensive request information."""
        try:
            # Basic request info
            info = {
                "endpoint": request.url.path,
                "method": request.method,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "Unknown"),
                "host": request.headers.get("host", "Unknown"),
                "scheme": request.url.scheme,
                "port": request.url.port
            }
            
            # Query parameters
            if request.query_params:
                info["query_params"] = dict(request.query_params)
            
            # Path parameters
            if request.path_params:
                info["path_params"] = dict(request.path_params)
            
            # Headers (filter sensitive ones)
            headers = dict(request.headers)
            sensitive_headers = ["authorization", "cookie", "x-api-key"]
            for header in sensitive_headers:
                if header in headers:
                    headers[header] = "[REDACTED]"
            info["headers"] = headers
            
            # Note: Body size estimation removed to avoid async complexity
            # In production, you might want to implement this differently
            
            return info
            
        except Exception as e:
            # Fallback if extraction fails
            return {
                "endpoint": str(request.url.path) if hasattr(request, 'url') else "unknown",
                "method": str(request.method) if hasattr(request, 'method') else "unknown",
                "client_ip": "unknown",
                "error": f"Failed to extract request info: {str(e)}"
            }
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        try:
            # Check for forwarded headers first
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip
            
            # Fallback to direct connection
            if hasattr(request, 'client') and request.client:
                return request.client.host
            
            return "unknown"
            
        except Exception:
            return "unknown"


# Factory function for creating request logging middleware
def create_request_logging_middleware(app) -> RequestLoggingMiddleware:
    """Create and configure request logging middleware."""
    return RequestLoggingMiddleware(app)


# Convenience function for direct usage
async def request_logging_middleware(request: Request, call_next):
    """Request logging middleware function for direct usage."""
    middleware = RequestLoggingMiddleware(None)
    return await middleware.dispatch(request, call_next)
