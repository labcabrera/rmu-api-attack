from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.domain.entities import CriticalEffect


class CriticalEffectDTO(BaseModel):

    status: str = Field(..., description="Text description of the critical")
    rounds: Optional[int] = Field(
        None, description="Round number for the critical effect"
    )
    value: Optional[int] = Field(
        None, description="Round number for the critical effect"
    )
    delay: Optional[int] = Field(
        None, description="Round number for the critical effect"
    )
    condition: Optional[str] = Field(
        None, description="Round number for the critical effect"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "stunned",
                "rounds": 2,
                "value": -50,
            }
        }
    )

    def to_entity(self):
        return CriticalEffect(
            status=self.status,
            rounds=self.rounds,
            value=self.value,
            delay=self.delay,
            condition=self.condition,
        )

    @classmethod
    def from_entity(cls, entity: CriticalEffect) -> "CriticalEffectDTO":
        return cls(
            status=entity.status,
            rounds=entity.rounds,
            value=entity.value,
            delay=entity.delay,
            condition=entity.condition,
        )
