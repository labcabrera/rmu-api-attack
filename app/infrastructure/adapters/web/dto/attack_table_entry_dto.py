from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities import (
    AttackTableEntry,
)


class AttackTableEntryDTO(BaseModel):
    """DTO for attack table entry"""

    model_config = ConfigDict(use_enum_values=True)

    literal: str = Field(..., description="Literal result description")
    damage: int = Field(..., description="Damage points")
    criticalType: Optional[str] = Field(None, description="Critical type")
    criticalSeverity: Optional[str] = Field(None, description="Critical severity")

    def to_entity(self):
        return AttackTableEntry(
            literal=self.literal,
            damage=self.damage,
            criticalType=self.criticalType,
            criticalSeverity=self.criticalSeverity,
        )

    @classmethod
    def from_entity(cls, entity: AttackTableEntry) -> "AttackTableEntryDTO":
        return cls(
            literal=entity.literal,
            damage=entity.damage,
            criticalType=entity.criticalType,
            criticalSeverity=entity.criticalSeverity,
        )
