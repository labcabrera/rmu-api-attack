from pydantic import BaseModel, ConfigDict, Field
from app.application.commands import UpdateAttackParryCommand


class UpdateParryRequestDTO(BaseModel):
    """DTO for update parry request"""

    parry: int = Field(..., description="Parry value to apply to the attack")

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "parry": 85,
            }
        },
    )

    def to_command(self, attack_id: str) -> UpdateAttackParryCommand:
        """Convert to command for use in application layer."""
        return UpdateAttackParryCommand(
            attack_id=attack_id,
            parry=self.parry,
        )
