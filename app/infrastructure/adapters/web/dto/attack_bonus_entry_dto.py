from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackBonusEntry


class AttackBonusEntryDTO(BaseModel):
    """DTO for attack bonus entry"""

    key: str = Field(..., description="Bonus key")
    value: int = Field(..., description="Bonus value")

    model_config = ConfigDict(json_schema_extra={"example": {"key": "bo", "value": 65}})

    def to_entity(self):
        return AttackBonusEntry(key=self.key, value=self.value)

    @classmethod
    def from_entity(cls, entity: AttackBonusEntry) -> "AttackBonusEntryDTO":
        return cls(
            key=entity.key,
            value=entity.value,
        )
