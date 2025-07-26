from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities import (
    AttackResult,
)
from app.infrastructure.adapters.web.dto import (
    AttackTableEntryDTO,
)


class AttackResultDTO(BaseModel):
    """DTO for attack result"""

    model_config = ConfigDict(use_enum_values=True)

    attackTableEntry: Optional[AttackTableEntryDTO] = Field(
        None, description="Attack table entry"
    )

    def to_entity(self):
        return AttackResult(
            attack_table_entry=(
                self.attackTableEntry.to_entity() if self.attackTableEntry else None
            ),
        )

    @classmethod
    def from_entity(cls, entity: AttackResult) -> "AttackResultDTO":
        return cls(
            attackTableEntry=(
                AttackTableEntryDTO.from_entity(entity.attack_table_entry)
                if entity.attack_table_entry
                else None
            ),
        )
