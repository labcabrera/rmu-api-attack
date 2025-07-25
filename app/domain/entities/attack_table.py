from typing import Optional
from dataclasses import dataclass


@dataclass
class AttackTableEntry:

    roll: int
    at: int
    damage: int
    critical: Optional[str] = None
