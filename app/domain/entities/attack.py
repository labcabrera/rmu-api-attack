"""
Domain entities for the RMU Attack system.
"""

from typing import Optional
from dataclasses import dataclass
from .critical import Critical
from .enums import (
    AttackStatus,
    AttackType,
    Cover,
    DodgeType,
    RestrictedQuarters,
)


@dataclass
class AttackKeyBonus:
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

    def __post_init__(self):
        """Validate input data after initialization"""
        # Convert string values to enum if necessary
        if isinstance(self.attack_type, str):
            self.attack_type = AttackType(self.attack_type)
        elif not isinstance(self.attack_type, AttackType):
            raise ValueError("Invalid attack type")
            
        if not isinstance(self.roll_modifiers, AttackRollModifiers):
            raise ValueError("Invalid roll modifiers")


@dataclass
class AttackCalculations:
    """Calculated data for attack processing"""

    modifiers: list[AttackKeyBonus]
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


@dataclass
class Attack:
    """Attack domain entity"""

    id: str
    tactical_game_id: str
    status: AttackStatus
    modifiers: AttackModifiers
    roll: Optional[AttackRoll] = None
    results: Optional[AttackResult] = None

    def execute_roll(self, roll_value: int) -> None:
        """Execute attack roll"""
        self.roll = AttackRoll(roll=roll_value)

    def apply_results(
        self, label: str, hit_points: int, criticals: list[Critical] = None
    ) -> None:
        """Apply attack results"""
        if criticals is None:
            criticals = []
        self.results = AttackResult(
            label_result=label, hit_points=hit_points, criticals=criticals
        )
        self.status = "executed"

    def is_pending(self) -> bool:
        """Check if attack is pending execution"""
        return self.status == "pending"

    def is_executed(self) -> bool:
        """Check if attack is executed"""
        return self.status == "executed"
