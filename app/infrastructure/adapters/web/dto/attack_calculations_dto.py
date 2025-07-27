from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackCalculations
from .attack_bonus_entry_dto import AttackBonusEntryDTO


class AttackCalculationsDTO(BaseModel):
    """DTO for attack calculations"""

    modifiers: list[AttackBonusEntryDTO] = Field(
        ..., description="Attack modifiers in key-value pairs"
    )
    total: int = Field(..., description="Total calculated value")
    critical_modifiers: list[AttackBonusEntryDTO] = Field(
        default_factory=list, description="Critical modifiers in key-value pairs"
    )
    critical_total: int = Field(
        0, description="Total calculated value for critical hits"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "modifiers": [{"key": "bo", "value": 65}, {"key": "bd", "value": -20}],
                "total": 54,
            }
        }
    )

    def to_entity(self):
        return AttackCalculations(
            modifiers=[m.to_entity() for m in self.modifiers],
            total=self.total,
            critical_modifiers=[m.to_entity() for m in self.critical_modifiers],
            critical_total=self.critical_total,
        )

    @classmethod
    def from_entity(cls, entity: AttackCalculations) -> "AttackCalculationsDTO":
        return cls(
            modifiers=[AttackBonusEntryDTO.from_entity(m) for m in entity.modifiers],
            total=entity.total,
            critical_modifiers=[
                AttackBonusEntryDTO.from_entity(m) for m in entity.critical_modifiers
            ],
            critical_total=entity.critical_total,
        )
