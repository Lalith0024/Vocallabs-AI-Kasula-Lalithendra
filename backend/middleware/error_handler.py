"""Global exception handler middleware."""

from fastapi import Request
from fastapi.responses import JSONResponse
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                "Unhandled exception",
                error=str(e),
                path=request.url.path,
                method=request.method,
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred processing your request.",
                },
            )
