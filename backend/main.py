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
    
    warnings = []
    if not settings.OCEAN_IO_API_KEY:
        warnings.append("OCEAN_IO_API_KEY not set — Stage 1 will use mock data")
    if not settings.PROSPEO_API_KEY:
        warnings.append("PROSPEO_API_KEY not set — Stage 2 will use mock data")
    if not settings.EAZYREACH_API_KEY:
        warnings.append("EAZYREACH_API_KEY not set — Stage 3 will use mock data")
    if not settings.BREVO_API_KEY:
        warnings.append("BREVO_API_KEY not set — Stage 4 will use mock data")
    if settings.SENDER_EMAIL == "outreach@yourdomain.com":
        warnings.append("SENDER_EMAIL is still the placeholder value — Brevo will reject sends")

    for w in warnings:
        logger.warning(f"[CONFIG] {w}")

    if warnings:
        logger.info(f"[CONFIG] {len(warnings)} config warning(s). Running in partial mock mode.")
    else:
        logger.info("[CONFIG] All API keys configured. Running in LIVE mode.")
    
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
    live_mode = all([
        settings.OCEAN_IO_API_KEY,
        settings.PROSPEO_API_KEY,
        settings.BREVO_API_KEY,
    ])
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "live_mode": live_mode,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
