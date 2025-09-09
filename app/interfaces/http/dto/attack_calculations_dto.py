from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackCalculations
from .attack_bonus_entry_dto import AttackBonusEntryDTO


class AttackCalculationsDTO(BaseModel):
    """DTO for attack calculations"""

    rollModifiers: list[AttackBonusEntryDTO] = Field(
        ..., description="Attack modifiers in key-value pairs"
    )
    criticalModifiers: list[AttackBonusEntryDTO] = Field(
        [], description="Critical modifiers in key-value pairs"
    )
    criticalSeverityModifiers: list[AttackBonusEntryDTO] = Field(
        [], description="Critical severity modifiers in key-value pairs"
    )
    rollTotal: int = Field(..., description="Total calculated value")
    criticalTotal: int = Field(
        0, description="Total calculated value for critical hits"
    )
    criticalSeverityTotal: int = Field(
        0, description="Total calculated value for critical severity"
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
            roll_modifiers=[m.to_entity() for m in self.rollModifiers],
            critical_modifiers=[m.to_entity() for m in self.criticalModifiers],
            critical_severity_modifiers=[
                m.to_entity() for m in self.criticalSeverityModifiers
            ],
            roll_total=self.rollTotal,
            critical_total=self.criticalTotal,
            critical_severity_total=self.criticalSeverityTotal,
        )

    @classmethod
    def from_entity(cls, entity: AttackCalculations) -> "AttackCalculationsDTO":
        return cls(
            rollModifiers=[
                AttackBonusEntryDTO.from_entity(m) for m in entity.roll_modifiers
            ],
            criticalModifiers=[
                AttackBonusEntryDTO.from_entity(m) for m in entity.critical_modifiers
            ],
            criticalSeverityModifiers=[
                AttackBonusEntryDTO.from_entity(m)
                for m in entity.critical_severity_modifiers
            ],
            rollTotal=entity.roll_total,
            criticalTotal=entity.critical_total,
            criticalSeverityTotal=entity.critical_severity_total,
        )
