from pydantic import BaseModel, ConfigDict, Field

from app.application.commands import UpdateCriticalRollCommand


class UpdateCriticalRollRequestDTO(BaseModel):
    """DTO for update critical roll request"""

    criticalKey: str = Field(..., description="Key of the critical to update")
    roll: int = Field(..., description="Roll value to apply to the critical")

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "criticalKey": "crit_001",
                "roll": 85,
            }
        },
    )

    def to_command(self, attack_id: str) -> UpdateCriticalRollCommand:
        """Convert to command for use in application layer."""
        return UpdateCriticalRollCommand(
            attack_id=attack_id,
            critical_key=self.criticalKey,
            roll=self.roll,
        )
