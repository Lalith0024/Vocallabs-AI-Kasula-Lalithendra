"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from config import get_settings
from database import init_db
from middleware.error_handler import ErrorHandlerMiddleware
from routes.campaigns import router as campaigns_router
from routes.webhooks import router as webhooks_router

settings = get_settings()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    logger.info("Starting up FastAPI application", app_name=settings.APP_NAME)
    
    # Import all models to ensure they are registered with Base.metadata
    import models 
    
    # For development, auto-create tables
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    logger.info("Shutting down FastAPI application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
