from pydantic import BaseModel, Field

from app.domain.entities import AttackRollModifiers


class AttackRollModifiersDTO(BaseModel):
    """DTO for attack roll modifiers"""

    bo: int = Field(..., description="Source offensive bonus")
    bd: int = Field(..., description="Target defensive bonus")
    boInjuryPenalty: int = Field(0, description="Injury penalty to offensive bonus")
    boPacePenalty: int = Field(0, description="Pace penalty to offensive bonus")
    boFatiguePenalty: int = Field(0, description="Fatigue penalty to offensive bonus")
    rangePenalty: int = Field(0, description="Range penalty")
    bdShield: int = Field(0, description="Shield defensive bonus")
    parry: int = Field(0, description="Parry value")
    customBonus: int = Field(0, description="Custom bonus to offensive bonus")

    def to_entity(self):
        return AttackRollModifiers(
            bo=self.bo,
            bd=self.bd,
            bo_injury_penalty=self.boInjuryPenalty,
            bo_pace_penalty=self.boPacePenalty,
            bo_fatigue_penalty=self.boFatiguePenalty,
            range_penalty=self.rangePenalty,
            parry=self.parry,
            custom_bonus=self.customBonus,
        )

    @classmethod
    def from_entity(cls, entity: AttackRollModifiers) -> "AttackRollModifiersDTO":
        return cls(
            bo=entity.bo,
            bd=entity.bd,
            boInjuryPenalty=entity.bo_injury_penalty,
            boPacePenalty=entity.bo_pace_penalty,
            boFatiguePenalty=entity.bo_fatigue_penalty,
            rangePenalty=entity.range_penalty,
            parry=entity.parry,
            customBonus=entity.custom_bonus,
        )
