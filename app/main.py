from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import attacks
from app.config import settings
from app.services.attack_service import attack_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events
    """
    # Startup: Connect to MongoDB
    await attack_service.connect()
    print("Connected to MongoDB")
    
    yield
    
    # Shutdown: Disconnect from MongoDB
    await attack_service.disconnect()
    print("Disconnected from MongoDB")

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(attacks.router, prefix="/v1/attacks", tags=["attacks"])

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
        # Test database connectivity
        await attack_service.connect()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "version": settings.APP_VERSION,
        "database": db_status,
        "mongodb_url": settings.MONGODB_URL.replace(settings.MONGODB_URL.split('@')[-1] if '@' in settings.MONGODB_URL else '', "***") if '@' in settings.MONGODB_URL else settings.MONGODB_URL
    }
