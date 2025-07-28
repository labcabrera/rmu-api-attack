from dataclasses import dataclass
from typing import Optional


@dataclass
class CriticalEffect:
    """Critical effect data"""

    status: str = None
    rounds: int = 0
    value: int = 0
    delay: int = 0


@dataclass
class CriticalTableEntry:
    """Critical result data"""

    dmg: int = 0
    effects: list[CriticalEffect] = None
    location: str = None
    text: str = None


@dataclass
class AttackCriticalResult:
    """Critical result data"""

    key: str = None
    status: str = None
    criticalType: Optional[str] = None
    criticalSeverity: Optional[str] = None
    adjusted_roll: Optional[int] = None
    result: Optional[CriticalTableEntry] = None
