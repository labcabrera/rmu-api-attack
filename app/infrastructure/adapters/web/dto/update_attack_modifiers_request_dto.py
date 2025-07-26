from pydantic import BaseModel, ConfigDict, Field

from app.application.commands import CreateAttackCommand

from app.infrastructure.adapters.web.dto import AttackModifiersDTO
from app.application.commands import UpdateAttackModifiersCommand


class UpdateAttackModifiersRequestDTO(BaseModel):
    """DTO for update attack modifiers request"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "modifiers": {
                    "attackType": "ranged",
                    "rollModifiers": {"bo": 90, "bd": -10},
                }
            }
        },
    )

    modifiers: AttackModifiersDTO = Field(
        ..., description="Updated attack modifiers including type and bonuses"
    )

    def to_command(self, attack_id: str) -> UpdateAttackModifiersCommand:
        """Convert to command for use in application layer."""
        return UpdateAttackModifiersCommand(
            attack_id=attack_id,
            modifiers=self.modifiers.to_entity(),
        )
