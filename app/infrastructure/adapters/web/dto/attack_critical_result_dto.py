from pydantic import BaseModel, ConfigDict, Field

# TODO


class AttackCriticalResultDTO(BaseModel):
    """DTO for critical hit"""

    id: str = Field(..., description="Critical ID")
    status: str = Field(..., description="Critical status")

    model_config = ConfigDict(
        json_schema_extra={"example": {"id": "critical_001", "status": "success"}}
    )
