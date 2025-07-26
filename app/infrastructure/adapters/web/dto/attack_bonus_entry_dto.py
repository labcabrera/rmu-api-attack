from dataclasses import Field
from pydantic import BaseModel

from domain.entities import AttackBonusEntry


class AttackBonusEntryDTO(BaseModel):
    """DTO for attack bonus entry"""

    key: str = Field(..., description="Bonus key")
    value: int = Field(..., description="Bonus value")

    def to_entity(self):
        return AttackBonusEntry(key=self.key, value=self.value)

    @classmethod
    def from_entity(cls, entity: AttackBonusEntry) -> "AttackBonusEntryDTO":
        return cls(
            key=entity.key,
            value=entity.value,
        )
