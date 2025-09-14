"""
Domain entities for the RMU Attack system.
"""

from typing import Optional
from dataclasses import dataclass

from .attack_calculations import AttackCalculations
from .attack_result import AttackResult
from .attack_roll import AttackRoll
from .attack_modifiers import AttackModifiers
from .enums import (
    AttackStatus,
    AttackType,
)


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

    def set_roll(self, roll: int, location: Optional[str]) -> None:
        if not roll:
            raise ValueError("Roll value must be provided")
        if self.modifiers.called_shot and location:
            raise ValueError("Location should not be provided for a called shot")
        if not self.modifiers.armor.at and not location:
            raise ValueError("Location must be provided using different AT values")
        effective_location = location or self.modifiers.called_shot
        effective_at = self.modifiers.armor.at
        if not effective_at:
            match effective_location:
                case "body":
                    effective_at = self.modifiers.armor.body_at
                case "head":
                    effective_at = self.modifiers.armor.head_at
                case "arms":
                    effective_at = self.modifiers.armor.arms_at
                case "legs":
                    effective_at = self.modifiers.armor.legs_at
        self.roll = AttackRoll(roll=roll, location=effective_location, at=effective_at)

    def is_melee(self) -> bool:
        return self.modifiers.attack_type == AttackType.MELEE

    def is_fumble(self) -> bool:
        return (
            self.modifiers.fumble > 0
            and self.roll
            and self.roll.roll <= self.modifiers.fumble
        )
