from pydantic import BaseModel, ConfigDict, Field


from app.domain.entities import CriticalTableEntry


class CriticalTableEntryDTO(BaseModel):

    text: str = Field(..., description="Text description of the critical")
    damage: int = Field(..., description="Damage value")
    location: str = Field(..., description="Location of the critical")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "damage": 10,
                "location": "head",
                "text": "Example critical description",
            }
        }
    )

    def to_entity(self):
        return CriticalTableEntry(
            damage=self.damage, location=self.location, text=self.text
        )

    @classmethod
    def from_entity(cls, entity: CriticalTableEntry) -> "CriticalTableEntryDTO":
        return cls(damage=entity.damage, location=entity.location, text=entity.text)
