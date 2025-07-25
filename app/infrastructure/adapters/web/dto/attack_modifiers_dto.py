from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackModifiers
from app.domain.entities.enums import AttackType

from .attack_roll_modifiers_dto import AttackRollModifiersDTO
from .attack_situational_modifiers_dto import AttackSituationalModifiersDTO


class AttackModifiersDTO(BaseModel):
    """DTO for attack modifiers"""

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

    attackType: AttackType = Field(..., description="Type of attack (melee, ranged)")
    attackTable: str = Field(..., description="Attack table identifier")
    attackSize: str = Field(..., description="Attack size identifier")
    at: int = Field(..., description="Attack table type", ge=0)
    rollModifiers: AttackRollModifiersDTO = Field(
        ..., description="Modifiers for the attack roll"
    )
    situationalModifiers: AttackSituationalModifiersDTO = Field(
        ..., description="Situational modifiers for the attack"
    )

    def to_entity(self):
        return AttackModifiers(
            attack_type=self.attackType,
            attack_table=self.attackTable,
            attack_size=self.attackSize,
            at=self.at,
            roll_modifiers=self.rollModifiers.to_entity(),
            situational_modifiers=self.situationalModifiers.to_entity(),
        )

    @classmethod
    def from_entity(cls, entity: AttackModifiers) -> "AttackModifiersDTO":
        return cls(
            attackType=entity.attack_type,
            attackTable=entity.attack_table,
            attackSize=entity.attack_size,
            at=entity.at,
            rollModifiers=AttackRollModifiersDTO.from_entity(entity.roll_modifiers),
            situationalModifiers=AttackSituationalModifiersDTO.from_entity(
                entity.situational_modifiers
            ),
        )
