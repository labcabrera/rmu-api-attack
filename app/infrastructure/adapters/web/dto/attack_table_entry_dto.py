from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities import (
    AttackTableEntry,
)


class AttackTableEntryDTO(BaseModel):
    """DTO for attack table entry"""

    model_config = ConfigDict(use_enum_values=True)

    text: str = Field(..., description="Text result description")
    damage: int = Field(..., description="Damage points")
    criticalType: Optional[str] = Field(None, description="Critical type")
    criticalSeverity: Optional[str] = Field(None, description="Critical severity")

    def to_entity(self):
        return AttackTableEntry(
            text=self.text,
            damage=self.damage,
            critical_type=self.criticalType,
            critical_severity=self.criticalSeverity,
        )

    @classmethod
    def from_entity(cls, entity: AttackTableEntry) -> "AttackTableEntryDTO":
        return cls(
            text=entity.text,
            damage=entity.damage,
            criticalType=entity.critical_type,
            criticalSeverity=entity.critical_severity,
        )
