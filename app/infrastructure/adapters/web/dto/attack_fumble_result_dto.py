from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackFumbleResult
from app.domain.entities.enums import FumbleStatus


class AttackFumbleResultDTO(BaseModel):
    """DTO for attack fumble result"""

    status: FumbleStatus = Field(..., description="Fumble status")
    text: Optional[str] = Field(None, description="Fumble text")
    additionalDamageText: Optional[str] = Field(
        None, description="Additional damage text"
    )
    damage: Optional[int] = Field(None, description="Damage value")
    effects: Optional[list] = Field(None, description="List of effects")

    model_config = ConfigDict(json_schema_extra={"example": {"key": "bo", "value": 65}})

    def to_entity(self):
        return AttackFumbleResult(
            status=self.status,
            text=self.text,
            additional_damage_text=self.additionalDamageText,
            damage=self.damage,
            effects=self.effects,
        )

    @classmethod
    def from_entity(cls, entity: AttackFumbleResult) -> "AttackFumbleResultDTO":
        return cls(
            status=entity.status,
            text=entity.text,
            additionalDamageText=entity.additional_damage_text,
            damage=entity.damage,
            effects=entity.effects,
        )
