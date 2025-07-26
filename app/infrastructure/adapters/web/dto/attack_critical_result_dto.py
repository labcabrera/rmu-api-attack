from pydantic import BaseModel, ConfigDict, Field

# TODO


class AttackCriticalResultDTO(BaseModel):
    """DTO for critical hit"""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Critical ID")
    status: str = Field(..., description="Critical status")
