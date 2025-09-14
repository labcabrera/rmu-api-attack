from dataclasses import dataclass


@dataclass
class AttackBonusEntry:
    """Attack bonus data"""

    key: str
    value: int
