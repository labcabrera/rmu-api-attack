from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackRoll


class AttackRollDTO(BaseModel):
    """DTO for attack roll"""

    roll: int = Field(..., description="Roll result")
    location: Optional[str] = Field(None, description="Hit location")
    at: int = Field(..., description="Resolved armor type")
    criticalRolls: Optional[dict[str, int]] = Field(
        None, description="Critical rolls by type"
    )
    fumbleRoll: Optional[int] = Field(None, description="Fumble roll result")

    model_config = ConfigDict(use_enum_values=True)

    def to_entity(self):
        return AttackRoll(
            roll=self.roll,
            location=self.location,
            at=self.at,
            critical_rolls=self.criticalRolls,
            fumble_roll=self.fumbleRoll,
        )

    @classmethod
    def from_entity(cls, entity: AttackRoll) -> "AttackRollDTO":
        return cls(
            roll=entity.roll,
            location=entity.location,
            at=entity.at,
            criticalRolls=entity.critical_rolls,
            fumbleRoll=entity.fumble_roll,
        )
