from dataclasses import dataclass
from typing import Optional


@dataclass
class AttackTableEntry:
    """Represents an entry in the attack table readed from RMU Attack Table API."""

    text: str
    damage: int
    critical_type: Optional[str] = None
    critical_severity: Optional[str] = None
    damage_base: int = 0
    critical_severity_base: Optional[str] = None
