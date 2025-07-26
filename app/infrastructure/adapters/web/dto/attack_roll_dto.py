from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities import (
    AttackRoll,
)


class AttackRollDTO(BaseModel):
    """DTO for attack roll"""

    model_config = ConfigDict(use_enum_values=True)

    roll: int = Field(..., description="Roll result")

    def to_entity(self):
        return AttackRoll(roll=self.roll)

    @classmethod
    def from_entity(cls, entity: AttackRoll) -> "AttackRollDTO":
        return cls(roll=entity.roll)
