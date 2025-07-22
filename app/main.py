from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.infrastructure.dependency_container import container

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events
    """
    # Startup: Initialize dependencies
    await container.initialize()
    print("Initialized hexagonal architecture dependencies")
    print("Connected to MongoDB")
    
    yield
    
    # Shutdown: Clean up dependencies
    await container.cleanup()
    print("Cleaned up dependencies")
    print("Disconnected from MongoDB")

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Get the attack controller from the container and include its router
attack_controller = container.get_attack_controller()
app.include_router(attack_controller.router, prefix="/v1/attacks", tags=["attacks"])

@app.get("/")
async def root():
    return {
        "message": "RMU API Attack - Attack management system",
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_PREFIX
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API and database connectivity
    """
    try:
        # Test database connectivity through the repository
        attack_repository = container.get_attack_repository()
        if hasattr(attack_repository, 'connect'):
            await attack_repository.connect()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "version": settings.APP_VERSION,
        "database": db_status,
        "mongodb_url": settings.MONGODB_URL.replace(settings.MONGODB_URL.split('@')[-1] if '@' in settings.MONGODB_URL else '', "***") if '@' in settings.MONGODB_URL else settings.MONGODB_URL,
        "architecture": "hexagonal"
    }
