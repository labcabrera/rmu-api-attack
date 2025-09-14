"""
Domain entities for the RMU Attack system.
"""

from typing import Optional
from dataclasses import dataclass
from .attack_roll_modifiers import AttackRollModifiers
from .attack_modifiers import AttackModifiers
from .critical import CriticalEffect, AttackCriticalResult
from .attack_table_entry import AttackTableEntry
from .enums import (
    AttackStatus,
    AttackType,
    FumbleStatus,
)


@dataclass
class AttackBonusEntry:
    """Attack bonus data"""

    key: str
    value: int


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
    game_id: str
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
