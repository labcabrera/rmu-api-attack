"""
Critical web controller using hexagonal architecture.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.infrastructure.dependency_container import container
from app.infrastructure.adapters.web.critical_dtos import (
    CriticalCreateRequestDTO,
    CriticalUpdateRequestDTO, 
    CriticalResponseDTO,
    CriticalNotFoundDTO,
    critical_to_dto
)

router = APIRouter(prefix="/criticals", tags=["criticals"])


@router.post("/", response_model=CriticalResponseDTO, status_code=201)
async def create_critical(request: CriticalCreateRequestDTO):
    """Create a new critical"""
    try:
        create_use_case = container.get_create_critical_use_case()
        critical = await create_use_case.execute(
            critical_id=request.id,
            critical_type=request.type,
            roll=request.roll,
            result=request.result,
            status=request.status
        )
        return critical_to_dto(critical)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{critical_id}", response_model=CriticalResponseDTO, responses={404: {"model": CriticalNotFoundDTO}})
async def get_critical(critical_id: str):
    """Get critical by ID"""
    try:
        get_use_case = container.get_get_critical_use_case()
        critical = await get_use_case.execute(critical_id)
        
        if not critical:
            raise HTTPException(
                status_code=404, 
                detail={"detail": "Critical not found", "critical_id": critical_id}
            )
            
        return critical_to_dto(critical)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{critical_id}", response_model=CriticalResponseDTO, responses={404: {"model": CriticalNotFoundDTO}})
async def update_critical(critical_id: str, request: CriticalUpdateRequestDTO):
    """Update critical (partial update)"""
    try:
        update_use_case = container.get_update_critical_use_case()
        
        # Convert request to dict, excluding None values
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        critical = await update_use_case.execute(critical_id, update_data)
        
        if not critical:
            raise HTTPException(
                status_code=404, 
                detail={"detail": "Critical not found", "critical_id": critical_id}
            )
            
        return critical_to_dto(critical)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[CriticalResponseDTO])
async def list_criticals(
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(100, description="Maximum number of results", ge=1, le=1000),
    skip: int = Query(0, description="Number of results to skip", ge=0)
):
    """List criticals with optional filters"""
    try:
        list_use_case = container.get_list_criticals_use_case()
        criticals = await list_use_case.execute(
            status=status,
            critical_type=type,
            limit=limit,
            skip=skip
        )
        return [critical_to_dto(critical) for critical in criticals]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{critical_id}/apply", response_model=CriticalResponseDTO, responses={404: {"model": CriticalNotFoundDTO}})
async def apply_critical(critical_id: str):
    """Apply a critical (change status to 'applied')"""
    try:
        apply_use_case = container.get_apply_critical_use_case()
        critical = await apply_use_case.execute(critical_id)
        
        if not critical:
            raise HTTPException(
                status_code=404, 
                detail={"detail": "Critical not found", "critical_id": critical_id}
            )
            
        return critical_to_dto(critical)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
