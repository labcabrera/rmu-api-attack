from pydantic import BaseModel, Field

from app.domain.entities import AttackSkill


class AttackSkillDTO(BaseModel):

    skillId: str = Field(..., description="Identifier for the skill")
    bonus: int = Field(..., description="Bonus for the skill")

    def to_entity(self):
        return AttackSkill(skillId=self.skillId, bonus=self.bonus)

    @classmethod
    def from_entity(cls, entity: AttackSkill) -> "AttackSkillDTO":
        return cls(skillId=entity.skillId, bonus=entity.bonus)
