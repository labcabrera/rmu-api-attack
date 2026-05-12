"""
Data Transfer Objects for the web API.
These convert between domain entities and API representations.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import (
    Attack,
)

from .attack_calculations_dto import AttackCalculationsDTO
from .attack_modifiers_dto import AttackModifiersDTO
from .attack_result_dto import AttackResultDTO
from .attack_roll_dto import AttackRollDTO


class AttackDTO(BaseModel):
    """DTO for complete attack"""

    id: str = Field(..., description="Attack identifier")
    gameId: str = Field(..., description="Tactical game identifier")
    actionId: str = Field(..., description="Action identifier")
    sourceId: str = Field(..., description="Source identifier")
    targetId: str = Field(..., description="Target identifier")
    status: str = Field(..., description="Attack status")
    modifiers: AttackModifiersDTO = Field(..., description="Attack input")
    roll: Optional[AttackRollDTO] = Field(None, description="Attack roll")
    calculated: Optional[AttackCalculationsDTO] = Field(
        None, description="Calculated attack data"
    )
    results: Optional[AttackResultDTO] = Field(None, description="Attack results")

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": "68837ba24b9293ca54e6ff72",
                "gameId": "game_001",
                "actionId": "action_001",
                "sourceId": "character_001",
                "targetId": "character_002",
                "status": "draft",
                "modifiers": {
                    "attackType": "melee",
                    "rollModifiers": {
                        "bo": 96,
                        "bd": -11,
                        "boInjuryPenalty": -5,
                        "boActionsPointsPenalty": -2,
                        "boPacePenalty": -3,
                        "boFatiguePenalty": -1,
                        "rangePenalty": 0,
                        "parry": 10,
                        "customBonus": 5,
                    },
                },
                "roll": {"roll": 55},
                "calculated": {
                    "modifiers": [
                        {"key": "roll", "value": 55},
                        {"key": "bo", "value": 96},
                        {"key": "bd", "value": -11},
                    ],
                    "total": 140,
                },
                "results": None,
            }
        },
    )

    def to_entity(self):
        return Attack(
            id=self.id,
            game_id=self.gameId,
            action_id=self.actionId,
            source_id=self.sourceId,
            target_id=self.targetId,
            status=self.status,
            modifiers=self.modifiers.to_entity(),
            roll=self.roll.to_entity() if self.roll else None,
            calculated=self.calculated.to_entity() if self.calculated else None,
            results=self.results.to_entity() if self.results else None,
        )

    @classmethod
    def from_entity(cls, entity: Attack) -> "AttackDTO":
        return cls(
            id=entity.id,
            gameId=entity.game_id,
            actionId=entity.action_id,
            sourceId=entity.source_id,
            targetId=entity.target_id,
            status=entity.status,
            modifiers=AttackModifiersDTO.from_entity(entity.modifiers),
            roll=AttackRollDTO.from_entity(entity.roll) if entity.roll else None,
            calculated=(
                AttackCalculationsDTO.from_entity(entity.calculated)
                if entity.calculated
                else None
            ),
            results=(
                AttackResultDTO.from_entity(entity.results) if entity.results else None
            ),
        )
