from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.domain.entities import AttackBonusEntry, AttackArmor


class AttackArmorDTO(BaseModel):
    """DTO for attack armor"""

    at: int | None = Field(default=None, description="Overall armor type")
    body_at: int | None = Field(default=None, description="Body armor type")
    head_at: int | None = Field(default=None, description="Head armor type")
    arms_at: int | None = Field(default=None, description="Arms armor type")
    legs_at: int | None = Field(default=None, description="Legs armor type")

    model_config = ConfigDict(json_schema_extra={"example": {"at": 1}})

    def to_entity(self):
        return AttackArmor(
            at=self.at,
            body_at=self.body_at,
            head_at=self.head_at,
            arms_at=self.arms_at,
            legs_at=self.legs_at,
        )

    @classmethod
    def from_entity(cls, entity: AttackArmor) -> "AttackArmorDTO":
        return cls(
            at=entity.at,
            body_at=entity.body_at,
            head_at=entity.head_at,
            arms_at=entity.arms_at,
            legs_at=entity.legs_at,
        )
