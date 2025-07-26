from pydantic import BaseModel, ConfigDict, Field

from app.application.commands import CreateAttackCommand
from app.infrastructure.adapters.web.dto import AttackModifiersDTO


class CreateAttackRequestDTO(BaseModel):
    """DTO for create attack request"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "actionId": "action_001",
                "sourceId": "character_001",
                "targetId": "character_002",
                "modifiers": {
                    "attackType": "melee",
                    "rollModifiers": {
                        "bo": 96,
                        "boInjuryPenalty": -5,
                        "boActionsPointsPenalty": -2,
                        "boPacePenalty": -3,
                        "boFatiguePenalty": -1,
                        "rangePenalty": 0,
                        "bd": -11,
                        "bdShield": -10,
                        "parry": -10,
                        "customBonus": 5,
                    },
                },
            }
        },
    )

    actionId: str = Field(..., description="Action ID")
    sourceId: str = Field(..., description="Source ID")
    targetId: str = Field(..., description="Target ID")
    modifiers: AttackModifiersDTO = Field(
        ..., description="Attack modifiers including type and bonuses"
    )

    def to_command(self):
        return CreateAttackCommand(
            action_id=self.actionId,
            source_id=self.sourceId,
            target_id=self.targetId,
            modifiers=self.modifiers.to_domain(),
        )
