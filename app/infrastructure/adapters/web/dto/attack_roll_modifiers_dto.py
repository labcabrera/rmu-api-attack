from pydantic import BaseModel, Field

from app.domain.entities import AttackRollModifiers


class AttackRollModifiersDTO(BaseModel):
    """DTO for attack roll modifiers"""

    bo: int = Field(..., description="Source offensive bonus")
    bd: int = Field(..., description="Target defensive bonus")
    injuryPenalty: int = Field(0, description="Injury penalty to offensive bonus")
    pacePenalty: int = Field(0, description="Pace penalty to offensive bonus")
    fatiguePenalty: int = Field(0, description="Fatigue penalty to offensive bonus")
    rangePenalty: int = Field(0, description="Range penalty")
    shield: int = Field(0, description="Shield defensive bonus")
    parry: int = Field(0, description="Parry value")
    customBonus: int = Field(0, description="Custom bonus to offensive bonus")

    def to_entity(self):
        return AttackRollModifiers(
            bo=self.bo,
            bd=self.bd,
            injury_penalty=self.injuryPenalty,
            pace_penalty=self.pacePenalty,
            fatigue_penalty=self.fatiguePenalty,
            range_penalty=self.rangePenalty,
            shield=self.shield,
            parry=self.parry,
            custom_bonus=self.customBonus,
        )

    @classmethod
    def from_entity(cls, entity: AttackRollModifiers) -> "AttackRollModifiersDTO":
        return cls(
            bo=entity.bo,
            bd=entity.bd,
            injuryPenalty=entity.injury_penalty,
            pacePenalty=entity.pace_penalty,
            fatiguePenalty=entity.fatigue_penalty,
            rangePenalty=entity.range_penalty,
            shield=entity.shield,
            parry=entity.parry,
            customBonus=entity.custom_bonus,
        )
