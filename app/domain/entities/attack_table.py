from typing import Optional
from dataclasses import dataclass


@dataclass
class AttackTableEntry:

    roll: int
    at: int
    literal: str
    damage: int
    # TODO enum
    criticalType: Optional[str] = None
    criticalSeverity: Optional[str] = None
