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

    bo: int
    bo_injury_penalty: int
    bo_actions_points_penalty: int
    bo_pace_penalty: int
    bo_fatigue_penalty: int
    bd: int
    range_penalty: int
    parry: int
    custom_bonus: int


class AttackSituationalModifiers:
    """Modifiers for attack situation calculated by tactical domain model"""

    off_hand: bool
    stunned_target: bool
    size_difference: int
    disabled_db: bool
    disabled_shield: bool
    higher_ground: bool
    surprised: bool
    prone_attacker: bool
    prone_defender: bool
    restricted_quarters: RestrictedQuarters
    positional_attacker: bool
    positional_defender: bool
    cover: Cover
    dodge: DodgeType
    ranged_attack_in_melee: bool
    range: int


@dataclass
class AttackModifiers:
    """Attack modifiers data"""

    attack_type: AttackType
    roll_modifiers: AttackRollModifiers
    attack_table: str
    attack_size: str
    at: int

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

    attack_table_entry: Optional[AttackTableEntry] = None
    criticals: list[Critical] = None


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
