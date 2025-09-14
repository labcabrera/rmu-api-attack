from dataclasses import dataclass
from typing import Optional

from .critical import CriticalEffect
from .enums import FumbleStatus


@dataclass
class AttackFumbleResult:

    status: FumbleStatus = None
    text: Optional[str] = None
    additional_damage_text: Optional[str] = None
    damage: Optional[int] = None
    effects: Optional[list[CriticalEffect]] = None
