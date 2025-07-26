from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackCalculations
from .attack_bonus_entry_dto import AttackBonusEntryDTO


class AttackCalculationsDTO(BaseModel):
    """DTO for attack calculations"""

    model_config = ConfigDict(use_enum_values=True)

    modifiers: list[AttackBonusEntryDTO] = Field(
        ..., description="Attack modifiers in key-value pairs"
    )
    total: int = Field(..., description="Total calculated value")

    def to_entity(self):
        return AttackCalculations(
            modifiers=[m.to_entity() for m in self.modifiers],
            total=self.total,
        )

    @classmethod
    def from_entity(cls, entity: AttackCalculations) -> "AttackCalculationsDTO":
        return cls(
            modifiers=[AttackBonusEntryDTO.from_entity(m) for m in entity.modifiers],
            total=entity.total,
        )
