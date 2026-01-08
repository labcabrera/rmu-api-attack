from dataclasses import dataclass

from .attack_bonus_entry import AttackBonusEntry


@dataclass
class AttackCalculations:
    """Calculated data for attack processing"""

    roll_modifiers: list[AttackBonusEntry] = None
    critical_modifiers: list[AttackBonusEntry] = None
    critical_severity_modifiers: list[AttackBonusEntry] = None
    roll_total: int = 0
    critical_total: int = 0
    critical_severity_total: int = 0
    critical_size_modifier: int = 0
    hit_size_multiplier: float = 1.0
