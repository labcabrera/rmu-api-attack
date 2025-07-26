"""
Domain entities for the RMU Attack system.
"""

from typing import Optional
from dataclasses import dataclass
from .critical import Critical
from .attack_table import AttackTableEntry
from .enums import (
    AttackStatus,
    AttackType,
    Cover,
    DodgeType,
    PositionalSource,
    PositionalTarget,
    RestrictedQuarters,
)


@dataclass
class AttackBonusEntry:
    """Attack bonus data"""

    key: str
    value: int


@dataclass
class AttackRollModifiers:
    """Modifiers for attack roll calculated by tactical domain model"""

    bo: int = 0
    bo_injury_penalty: int = 0
    bo_actions_points_penalty: int = 0
    bo_pace_penalty: int = 0
    bo_fatigue_penalty: int = 0
    bd: int = 0
    bd_shield: int = 0
    range_penalty: int = 0
    parry: int = 0
    custom_bonus: int = 0


@dataclass
class AttackSituationalModifiers:
    """Modifiers for attack situation calculated by tactical domain model"""

    cover: Cover = Cover.NONE
    restricted_quarters: RestrictedQuarters = RestrictedQuarters.NONE
    positional_source: PositionalSource = PositionalSource.NONE
    positional_target: PositionalTarget = PositionalTarget.NONE
    dodge: DodgeType = DodgeType.NONE

    stunned_target: bool = False

    disabled_db: bool = False
    disabled_shield: bool = False

    surprised: bool = False
    prone_attacker: bool = False
    prone_defender: bool = False

    size_difference: int = 0
    off_hand: bool = False
    higher_ground: bool = False

    range: int = 0
    ranged_attack_in_melee: bool = False


@dataclass
class AttackModifiers:
    """Attack modifiers data"""

    attack_type: AttackType
    attack_table: str
    attack_size: str = "medium"
    at: int = 1
    roll_modifiers: AttackRollModifiers = None
    situational_modifiers: AttackSituationalModifiers = None

    def __post_init__(self):
        """Validate input data after initialization"""
        # Convert string values to enum if necessary
        if isinstance(self.attack_type, str):
            self.attack_type = AttackType(self.attack_type)
        elif not isinstance(self.attack_type, AttackType):
            raise ValueError("Invalid attack type")

        if not isinstance(self.roll_modifiers, AttackRollModifiers):
            raise ValueError("Invalid roll modifiers")

        if not isinstance(self.attack_table, str):
            raise ValueError("attack_table must be a string")

        if not isinstance(self.attack_size, str):
            raise ValueError("attack_size must be a string")

        if not isinstance(self.at, int) or self.at < 0:
            raise ValueError("at must be a non-negative integer")


@dataclass
class AttackCalculations:
    """Calculated data for attack processing"""

    modifiers: list[AttackBonusEntry]
    total: int


@dataclass
class AttackRoll:
    """Attack roll data"""

    roll: int


@dataclass
class AttackResult:
    """Attack result data"""

    label_result: str
    hit_points: int
    criticals: list[Critical]
    attack_table_entry: Optional[AttackTableEntry] = None


@dataclass
class Attack:
    """Attack domain entity."""

    id: str
    action_id: str
    source_id: str
    target_id: str
    status: AttackStatus
    modifiers: AttackModifiers
    roll: Optional[AttackRoll] = None
    calculated: Optional[AttackCalculations] = None
    results: Optional[AttackResult] = None
