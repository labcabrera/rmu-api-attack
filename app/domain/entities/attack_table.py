from typing import Optional
from dataclasses import dataclass


@dataclass
class AttackTableEntry:
    """Represents an entry in the attack table readed from RMU Attack Table API."""

    text: str
    damage: int
    critical_type: Optional[str] = None
    critical_severity: Optional[str] = None
