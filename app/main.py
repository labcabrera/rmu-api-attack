from fastapi import FastAPI
from app.api.v1 import attacks

app = FastAPI(
    title="RMU API Attack",
    description="API REST para gestión de ataques en el sistema RMU",
    version="1.0.0"
)

# Incluir routers
app.include_router(attacks.router, prefix="/attacks/v1", tags=["attacks"])

@app.get("/")
async def root():
    return {"message": "RMU API Attack - Sistema de gestión de ataques"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
