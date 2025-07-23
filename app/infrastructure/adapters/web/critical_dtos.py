"""
Critical DTOs for web layer.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CriticalCreateRequestDTO(BaseModel):
    """DTO for critical creation request"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id: str = Field(..., description="Critical identifier", min_length=1)
    type: str = Field(..., description="Type of critical hit", min_length=1)
    roll: int = Field(..., description="Roll result for the critical", ge=1, le=100)
    result: str = Field(..., description="Critical result description", min_length=1)
    status: str = Field(default="pending", description="Critical status")


class CriticalUpdateRequestDTO(BaseModel):
    """DTO for critical update request (PATCH)"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    type: Optional[str] = Field(None, description="Type of critical hit", min_length=1)
    roll: Optional[int] = Field(None, description="Roll result for the critical", ge=1, le=100)
    result: Optional[str] = Field(None, description="Critical result description", min_length=1)
    status: Optional[str] = Field(None, description="Critical status")


class CriticalResponseDTO(BaseModel):
    """DTO for critical response"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "crit_001",
                "type": "Slash",
                "roll": 85,
                "result": "Light wound to arm",
                "status": "applied"
            }
        }
    )
    
    id: str = Field(..., description="Critical identifier")
    type: str = Field(..., description="Type of critical hit")
    roll: int = Field(..., description="Roll result for the critical")
    result: str = Field(..., description="Critical result description")
    status: str = Field(..., description="Critical status")


class CriticalNotFoundDTO(BaseModel):
    """DTO for critical not found error"""
    detail: str = Field(..., description="Error message")
    critical_id: str = Field(..., description="Critical ID that was not found")


# Conversion functions between DTOs and domain entities

def critical_to_dto(critical) -> CriticalResponseDTO:
    """Convert Critical entity to response DTO"""
    return CriticalResponseDTO(
        id=critical.id,
        type=critical.type,
        roll=critical.roll,
        result=critical.result,
        status=critical.status
    )


def create_request_to_domain(dto: CriticalCreateRequestDTO):
    """Convert CreateCriticalRequestDTO to domain Critical"""
    from app.domain.entities.critical import Critical
    return Critical(
        id=dto.id,
        type=dto.type,
        roll=dto.roll,
        result=dto.result,
        status=dto.status
    )
