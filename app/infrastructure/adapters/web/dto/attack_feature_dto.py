from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackFeature


class AttackFeatureDTO(BaseModel):
    """DTO for attack feature entries"""

    key: str = Field(..., description="Feature key")
    value: str = Field(..., description="Feature value")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "slayer-attack",
                "value": "enabled",
            }
        }
    )

    def to_entity(self):
        return AttackFeature(key=self.key, value=self.value)

    @classmethod
    def from_entity(cls, entity: AttackFeature) -> "AttackFeatureDTO":
        return cls(key=entity.key, value=entity.value)
