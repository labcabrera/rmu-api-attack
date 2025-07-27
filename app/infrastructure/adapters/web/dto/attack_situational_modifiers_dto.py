from pydantic import BaseModel, ConfigDict, Field

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

    cover: Cover = Field("none", description="Cover status")
    restrictedQuarters: RestrictedQuarters = Field(
        "none", description="Restricted quarters status"
    )
    positionalSource: PositionalSource = Field(
        "none", description="Positional source status"
    )
    positionalTarget: PositionalTarget = Field(
        "none", description="Positional target status"
    )
    dodge: DodgeType = Field("none", description="Dodge status")

    disabledDB: bool = Field(False, description="Disabled DB status")
    disabledShield: bool = Field(False, description="Disabled shield status")
    disabledParry: bool = Field(False, description="Disabled parry status")

    sizeDifference: int = Field(0, description="Size difference")
    offHand: bool = Field(False, description="Off-hand status")
    higherGround: bool = Field(False, description="Higher ground status")

    sourceStatus: list[str] = Field([], description="Source status list")
    targetStatus: list[str] = Field([], description="Target status list")

    model_config = ConfigDict(use_enum_values=True)

    def to_entity(self):
        return AttackSituationalModifiers(
            cover=Cover.from_value(self.cover),
            restricted_quarters=RestrictedQuarters.from_value(self.restrictedQuarters),
            positional_source=PositionalSource.from_value(self.positionalSource),
            positional_target=PositionalTarget.from_value(self.positionalTarget),
            dodge=DodgeType.from_value(self.dodge),
            disabled_db=self.disabledDB,
            disabled_shield=self.disabledShield,
            disabled_parry=self.disabledParry,
            size_difference=self.sizeDifference,
            off_hand=self.offHand,
            higher_ground=self.higherGround,
            source_status=self.sourceStatus,
            target_status=self.targetStatus,
        )

    @classmethod
    def from_entity(
        cls, entity: AttackSituationalModifiers
    ) -> "AttackSituationalModifiersDTO":
        if not entity:
            return None
        return cls(
            cover=entity.cover.value,
            restrictedQuarters=entity.restricted_quarters,
            positionalSource=entity.positional_source,
            positionalTarget=entity.positional_target,
            dodge=entity.dodge,
            disabledDB=entity.disabled_db,
            disabledShield=entity.disabled_shield,
            disabledParry=entity.disabled_parry,
            sizeDifference=entity.size_difference,
            offHand=entity.off_hand,
            higherGround=entity.higher_ground,
            sourceStatus=entity.source_status,
            targetStatus=entity.target_status,
        )
