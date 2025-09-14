from dataclasses import dataclass
from typing import Optional


@dataclass
class AttackRoll:
    """Attack roll data"""

    roll: Optional[int] = None
    location: Optional[str] = None
    at: int = None
    critical_rolls: dict[str, int] = None
    fumble_roll: Optional[int] = None
