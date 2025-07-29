from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


from app.domain.entities import CriticalTableEntry

from .critical_effect_dto import CriticalEffectDTO


class CriticalTableEntryDTO(BaseModel):

    text: str = Field(..., description="Text description of the critical")
    damage: int = Field(..., description="Damage value")
    location: str = Field(..., description="Location of the critical")
    effects: Optional[list[CriticalEffectDTO]] = Field(
        None, description="List of effects associated with the critical"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "damage": 10,
                "location": "head",
                "text": "Example critical description",
            }
        }
    )

    @classmethod
    def from_entity(cls, entity: CriticalTableEntry) -> "CriticalTableEntryDTO":
        return cls(
            damage=entity.damage,
            location=entity.location,
            text=entity.text,
            effects=(
                [CriticalEffectDTO.from_entity(effect) for effect in entity.effects]
                if entity.effects
                else None
            ),
        )
