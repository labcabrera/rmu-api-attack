from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities import (
    AttackTableEntry,
)


class AttackTableEntryDTO(BaseModel):
    """DTO for attack table entry"""

    model_config = ConfigDict(use_enum_values=True)

    roll: int = Field(..., description="Roll value")
    at: int = Field(..., description="AT value")
    literal: str = Field(..., description="Literal result description")
    damage: int = Field(..., description="Damage points")
    criticalType: Optional[str] = Field(None, description="Critical type")
    criticalSeverity: Optional[str] = Field(None, description="Critical severity")

    def to_entity(self):
        return AttackTableEntry(
            roll=self.roll,
            at=self.at,
            literal=self.literal,
            damage=self.damage,
            criticalType=self.criticalType,
            criticalSeverity=self.criticalSeverity,
        )

    @classmethod
    def from_entity(cls, entity: AttackTableEntry) -> "AttackTableEntryDTO":
        return cls(
            roll=entity.roll,
            at=entity.at,
            literal=entity.literal,
            damage=entity.damage,
            criticalType=entity.criticalType,
            criticalSeverity=entity.criticalSeverity,
        )
