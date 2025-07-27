from typing import Optional
from dataclasses import dataclass


@dataclass
class AttackTableEntry:

    literal: str
    damage: int
    criticalType: Optional[str] = None
    criticalSeverity: Optional[str] = None
