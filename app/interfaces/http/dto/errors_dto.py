import code
from pydantic import BaseModel, Field, ConfigDict


class AttackNotFoundDTO(BaseModel):
    """DTO for attack not found error"""

    model_config = ConfigDict(use_enum_values=True)

    message: str = Field(..., description="Error message")
    attack_id: str = Field(..., description="Attack ID that was not found")
