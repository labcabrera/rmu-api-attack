"""
Domain entities for the RMU Attack system.
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum
from .critical import Critical


class AttackMode(Enum):
    """Attack mode enumeration"""
    MAIN_HAND = "mainHand"
    OFF_HAND = "offHand"


@dataclass
class AttackInput:
    """Attack input data"""
    source_id: str
    target_id: str
    action_points: int
    mode: AttackMode


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
    status: str
    input: AttackInput
    roll: Optional[AttackRoll] = None
    results: Optional[AttackResult] = None
    
    def execute_roll(self, roll_value: int) -> None:
        """Execute attack roll"""
        self.roll = AttackRoll(roll=roll_value)
    
    def apply_results(self, label: str, hit_points: int, criticals: list[Critical] = None) -> None:
        """Apply attack results"""
        if criticals is None:
            criticals = []
        self.results = AttackResult(
            label_result=label,
            hit_points=hit_points,
            criticals=criticals
        )
        self.status = "executed"
    
    def is_pending(self) -> bool:
        """Check if attack is pending execution"""
        return self.status == "pending"
    
    def is_executed(self) -> bool:
        """Check if attack is executed"""
        return self.status == "executed"
