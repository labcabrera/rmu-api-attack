from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackModifiers
from app.domain.entities.enums import AttackType

from .attack_skill_dto import AttackSkillDTO
from .attack_feature_dto import AttackFeatureDTO
from .attack_roll_modifiers_dto import AttackRollModifiersDTO
from .attack_situational_modifiers_dto import AttackSituationalModifiersDTO


class AttackModifiersDTO(BaseModel):
    """DTO for attack modifiers"""

    attackType: AttackType = Field(..., description="Type of attack (melee, ranged)")
    attackTable: str = Field(..., description="Attack table identifier")
    attackSize: str = Field(..., description="Attack size identifier")
    at: int = Field(..., description="Attack table type", ge=1)
    actionPoints: int = Field(
        ..., description="Action points available for the attack", ge=1
    )
    rollModifiers: AttackRollModifiersDTO = Field(
        ..., description="Modifiers for the attack roll"
    )
    situationalModifiers: AttackSituationalModifiersDTO = Field(
        ..., description="Situational modifiers for the attack"
    )
    features: list[AttackFeatureDTO] = Field([], description="List of attack features")
    sourceSkills: list[AttackSkillDTO] = Field(
        [], description="List of source skills for the attack"
    )

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "attackType": "melee",
                "attackTable": "arming-sword",
                "attackSize": "medium",
                "at": 1,
            }
        },
    )

    def to_entity(self):
        return AttackModifiers(
            attack_type=self.attackType,
            attack_table=self.attackTable,
            attack_size=self.attackSize,
            at=self.at,
            action_points=self.actionPoints,
            roll_modifiers=self.rollModifiers.to_entity(),
            situational_modifiers=self.situationalModifiers.to_entity(),
            features=[feature.to_entity() for feature in self.features],
            source_skills=[skill.to_entity() for skill in self.sourceSkills],
        )

    @classmethod
    def from_entity(cls, entity: AttackModifiers) -> "AttackModifiersDTO":
        return cls(
            attackType=entity.attack_type,
            attackTable=entity.attack_table,
            attackSize=entity.attack_size,
            at=entity.at,
            actionPoints=entity.action_points,
            rollModifiers=AttackRollModifiersDTO.from_entity(entity.roll_modifiers),
            situationalModifiers=AttackSituationalModifiersDTO.from_entity(
                entity.situational_modifiers
            ),
            features=[
                AttackFeatureDTO.from_entity(feature) for feature in entity.features
            ],
            sourceSkills=[
                AttackSkillDTO.from_entity(skill) for skill in entity.source_skills
            ],
        )
