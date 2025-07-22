from fastapi import FastAPI
from app.api.v1 import attacks

app = FastAPI(
    title="RMU API Attack",
    description="REST API for attack management in the RMU system",
    version="1.0.0"
)

app.include_router(attacks.router, prefix="/v1/attacks", tags=["attacks"])

@app.get("/")
async def root():
    return {"message": "RMU API Attack - Attack management system"}

@app.get("/health")
async def health_check():
    return {"status": "healthy (TODO)", "version": "1.0.0"}
