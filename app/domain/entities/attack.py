"""
Domain entities for the RMU Attack system.
"""

from typing import Optional
from dataclasses import dataclass

from .attack_table import AttackTableEntry
from .enums import (
    AttackStatus,
    AttackType,
    Cover,
    DodgeType,
    FumbleStatus,
    PositionalSource,
    PositionalTarget,
    RestrictedQuarters,
)
from .critical import AttackCriticalResult, CriticalEffect


@dataclass
class AttackBonusEntry:
    """Attack bonus data"""

    key: str
    value: int


@dataclass
class AttackRollModifiers:
    """Modifiers for attack roll calculated by tactical domain model"""

    bo: int = 0
    injury_penalty: int = 0
    pace_penalty: int = 0
    fatigue_penalty: int = 0
    bd: int = 0
    shield: int = 0
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

    disabled_db: bool = False
    disabled_shield: bool = False
    disabled_parry: bool = False

    size_difference: int = 0
    off_hand: bool = False
    two_handed_weapon: bool = False
    higher_ground: bool = False

    source_status: list[str] = None
    target_status: list[str] = None


@dataclass
class AttackFeature:
    """Attack feature data"""

    key: str = None
    value: str = None


@dataclass
class AttackSkill:
    """Attack skill data"""

    skill_id: str = None
    bonus: int = 0


@dataclass
class AttackModifiers:
    """Attack modifiers data"""

    attack_type: AttackType = None
    attack_table: str = None
    attack_size: str = "medium"
    fumble_table: str = None
    at: int = 1
    action_points: int = 4
    fumble: int = 1
    roll_modifiers: AttackRollModifiers = None
    situational_modifiers: AttackSituationalModifiers = None
    features: list[AttackFeature] = None
    source_skills: list[AttackSkill] = None

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

    roll_modifiers: list[AttackBonusEntry] = None
    critical_modifiers: list[AttackBonusEntry] = None
    critical_severity_modifiers: list[AttackBonusEntry] = None
    roll_total: int = 0
    critical_total: int = 0
    critical_severity_total: int = 0


@dataclass
class AttackRoll:
    """Attack roll data"""

    roll: Optional[int] = None
    critical_rolls: dict[str, int] = None
    fumble_roll: Optional[int] = None


@dataclass
class AttackFumbleResult:

    status: FumbleStatus = None
    text: Optional[str] = None
    additional_damage_text: Optional[str] = None
    damage: Optional[int] = None
    effects: Optional[list[CriticalEffect]] = None


@dataclass
class AttackResult:
    """Attack result data"""

    attack_table_entry: Optional[AttackTableEntry] = None
    criticals: list[AttackCriticalResult] = None
    fumble: Optional[AttackFumbleResult] = None

    def get_critical_by_key(self, key: str) -> Optional[AttackCriticalResult]:
        """Get critical result by key"""
        if self.criticals:
            for critical in self.criticals:
                if critical.key == key:
                    return critical
        return None


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

    def is_melee(self) -> bool:
        return self.modifiers.attack_type == AttackType.MELEE

    def is_fumble(self) -> bool:
        return (
            self.modifiers.fumble > 0
            and self.roll
            and self.roll.roll <= self.modifiers.fumble
        )
