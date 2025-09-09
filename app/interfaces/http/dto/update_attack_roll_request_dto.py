from pydantic import BaseModel, ConfigDict, Field

from app.application.commands import UpdateAttackRollCommand


class UpdateAttackRollRequestDTO(BaseModel):
    """DTO for update attack roll request"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "roll": 15,
            }
        },
    )

    roll: int = Field(..., description="Roll value to apply to the attack")

    def to_command(self, attack_id: str) -> UpdateAttackRollCommand:
        """Convert to command for use in application layer."""
        return UpdateAttackRollCommand(
            attack_id=attack_id,
            roll=self.roll,
        )
