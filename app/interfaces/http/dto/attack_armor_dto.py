from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackArmor


class AttackArmorDTO(BaseModel):
    """DTO for attack armor"""

    at: int | None = Field(default=None, description="Overall armor type")
    bodyAt: int | None = Field(default=None, description="Body armor type")
    headAt: int | None = Field(default=None, description="Head armor type")
    armsAt: int | None = Field(default=None, description="Arms armor type")
    legsAt: int | None = Field(default=None, description="Legs armor type")

    model_config = ConfigDict(json_schema_extra={"example": {"at": 1}})

    def to_entity(self):
        return AttackArmor(
            at=self.at,
            body_at=self.bodyAt,
            head_at=self.headAt,
            arms_at=self.armsAt,
            legs_at=self.legsAt,
        )

    @classmethod
    def from_entity(cls, entity: AttackArmor) -> "AttackArmorDTO":
        return cls(
            at=entity.at,
            bodyAt=entity.body_at,
            headAt=entity.head_at,
            armsAt=entity.arms_at,
            legsAt=entity.legs_at,
        )
