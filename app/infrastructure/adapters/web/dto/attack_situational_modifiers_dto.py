from dataclasses import Field
from pydantic import BaseModel, ConfigDict

from app.domain.entities import AttackSituationalModifiers
from app.domain.entities.enums import (
    Cover,
    DodgeType,
    PositionalSource,
    PositionalTarget,
    RestrictedQuarters,
)


class AttackSituationalModifiersDTO(BaseModel):
    """DTO for attack situational modifiers"""

    model_config = ConfigDict(use_enum_values=True)

    cover: Cover = Field(None, description="Cover status")
    restrictedQuarters: RestrictedQuarters = Field(
        None, description="Restricted quarters status"
    )
    positionalSource: PositionalSource = Field(
        None, description="Positional source status"
    )
    positionalTarget: PositionalTarget = Field(
        None, description="Positional target status"
    )
    dodge: DodgeType = Field(None, description="Dodge status")
    stunnedTarget: bool = Field(False, description="Stunned target status")
    disabledDB: bool = Field(False, description="Disabled DB status")
    disabledShield: bool = Field(False, description="Disabled shield status")
    surprised: bool = Field(False, description="Surprised status")
    proneAttacker: bool = Field(False, description="Prone attacker status")
    proneDefender: bool = Field(False, description="Prone defender status")
    sizeDifference: int = Field(0, description="Size difference")
    offHand: bool = Field(False, description="Off-hand status")
    higherGround: bool = Field(False, description="Higher ground status")
    range: int = Field(0, description="Range")
    rangedAttackInMelee: bool = Field(
        False, description="Ranged attack in melee status"
    )

    def to_entity(self):
        return AttackSituationalModifiers(
            cover=self.cover,
            restricted_quarters=self.restrictedQuarters,
            positional_source=self.positionalSource,
            positional_target=self.positionalTarget,
            dodge=self.dodge,
            stunned_target=self.stunnedTarget,
            disabled_db=self.disabledDB,
            disabled_shield=self.disabledShield,
            surprised=self.surprised,
            prone_attacker=self.proneAttacker,
            prone_defender=self.proneDefender,
            size_difference=self.sizeDifference,
            off_hand=self.offHand,
            higher_ground=self.higherGround,
            range=self.range,
            ranged_attack_in_melee=self.rangedAttackInMelee,
        )

    @classmethod
    def from_entity(
        cls, entity: AttackSituationalModifiers
    ) -> "AttackSituationalModifiersDTO":
        return cls(
            cover=entity.cover,
            restrictedQuarters=entity.restricted_quarters,
            positionalSource=entity.positional_source,
            positionalTarget=entity.positional_target,
            dodge=entity.dodge,
            stunnedTarget=entity.stunned_target,
            disabledDB=entity.disabled_db,
            disabledShield=entity.disabled_shield,
            surprised=entity.surprised,
            proneAttacker=entity.prone_attacker,
            proneDefender=entity.prone_defender,
            sizeDifference=entity.size_difference,
            offHand=entity.off_hand,
            higherGround=entity.higher_ground,
            range=entity.range,
            rangedAttackInMelee=entity.ranged_attack_in_melee,
        )
