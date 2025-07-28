from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.infrastructure.config.config import settings
from app.infrastructure.dependency_container import container
from app.infrastructure.logging import setup_logging, get_logger
from app.infrastructure.adapters.web.attack_controller import router as attack_router


setup_logging(
    log_level=getattr(settings, "LOG_LEVEL", "INFO"),
    enable_console=True,
    enable_file=False,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events
    """
    logger.info("Starting RMU Attack API...")
    await container.initialize()
    logger.info("Initialized  dependencies")
    logger.info("Connected to MongoDB")

    yield

    # Shutdown: Clean up dependencies
    logger.info("Shutting down RMU Attack API...")
    await container.cleanup()
    logger.info("Cleaned up dependencies")
    logger.info("Disconnected from MongoDB")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Include routers
app.include_router(attack_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "RMU API Attack - Attack management system",
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_PREFIX,
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API and database connectivity
    """
    try:
        # Test database connectivity through the repository
        attack_repository = container.get_attack_repository()
        if hasattr(attack_repository, "connect"):
            await attack_repository.connect()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "version": settings.APP_VERSION,
        "database": db_status,
        "mongodb_url": (
            settings.MONGODB_URL.replace(
                (
                    settings.MONGODB_URL.split("@")[-1]
                    if "@" in settings.MONGODB_URL
                    else ""
                ),
                "***",
            )
            if "@" in settings.MONGODB_URL
            else settings.MONGODB_URL
        ),
    }
