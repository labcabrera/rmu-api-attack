from pydantic import BaseModel, ConfigDict, Field

from app.application.commands import UpdateFumbleRollCommand


class UpdateFumbleRollRequestDTO(BaseModel):
    """DTO for update critical roll request"""

    roll: int = Field(..., description="Roll value to apply to the critical")

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "roll": 85,
            }
        },
    )

    def to_command(self, attack_id: str) -> UpdateFumbleRollCommand:
        """Convert to command for use in application layer."""
        return UpdateFumbleRollCommand(
            attack_id=attack_id,
            roll=self.roll,
        )
