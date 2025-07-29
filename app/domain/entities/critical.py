from dataclasses import dataclass
from typing import Optional

from app.domain.entities.enums import CriticalStatus, FumbleStatus


@dataclass
class CriticalEffect:
    """Critical effect data"""

    status: str = None
    rounds: Optional[int] = 0
    value: Optional[int] = 0
    delay: Optional[int] = 0
    condition: Optional[str] = None


@dataclass
class CriticalTableEntry:
    """Critical result data"""

    damage: int = 0
    effects: list[CriticalEffect] = None
    location: str = None
    text: str = None


@dataclass
class AttackCriticalResult:
    """Critical result data"""

    key: str = None
    status: CriticalStatus = None
    critical_type: Optional[str] = None
    critical_severity: Optional[str] = None
    adjusted_roll: Optional[int] = None
    result: Optional[CriticalTableEntry] = None


@dataclass
class FumbleTableEntry:
    """Fumble result data"""

    status: FumbleStatus = None
    text: Optional[str] = None
    additional_damage_text: Optional[str] = None
    effects: Optional[list[CriticalEffect]] = None
