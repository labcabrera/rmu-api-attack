from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.domain.entities import AttackResult
from .attack_fumble_result_dto import AttackFumbleResultDTO
from .attack_critical_result_dto import AttackCriticalResultDTO
from .attack_table_entry_dto import AttackTableEntryDTO


class AttackResultDTO(BaseModel):
    """DTO for attack result"""

    model_config = ConfigDict(use_enum_values=True)

    attackTableEntry: Optional[AttackTableEntryDTO] = Field(
        None, description="Attack table entry"
    )
    criticals: list = Field(
        default_factory=list, description="List of critical results"
    )
    fumble: Optional[AttackFumbleResultDTO] = Field(None, description="Fumble result")

    def to_entity(self):
        return AttackResult(
            attack_table_entry=(
                self.attackTableEntry.to_entity() if self.attackTableEntry else None
            ),
            criticals=[
                AttackCriticalResultDTO.from_entity(critical)
                for critical in self.criticals
            ],
            fumble=(
                AttackFumbleResultDTO.from_entity(self.fumble) if self.fumble else None
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
            criticals=[
                AttackCriticalResultDTO.from_entity(critical)
                for critical in entity.criticals
            ],
            fumble=(
                AttackFumbleResultDTO.from_entity(entity.fumble)
                if entity.fumble
                else None
            ),
        )
