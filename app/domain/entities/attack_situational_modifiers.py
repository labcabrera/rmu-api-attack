from dataclasses import dataclass

from .enums import (
    Cover,
    DodgeType,
    PositionalSource,
    PositionalTarget,
    RestrictedQuarters,
)


@dataclass
class AttackSituationalModifiers:
    """Modifiers for attack situation calculated by tactical domain model"""

    cover: Cover = Cover.NONE
    restricted_quarters: RestrictedQuarters = RestrictedQuarters.NONE
    positional_source: PositionalSource = PositionalSource.NONE
    positional_target: PositionalTarget = PositionalTarget.NONE
    dodge: DodgeType = DodgeType.NONE

    disabled_db: bool = False
    disabled_shield: bool = False
    disabled_parry: bool = False

    size_difference: int = 0
    off_hand: bool = False
    two_handed_weapon: bool = False
    higher_ground: bool = False

    source_status: list[str] = None
    target_status: list[str] = None
