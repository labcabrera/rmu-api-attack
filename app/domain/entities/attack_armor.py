from dataclasses import dataclass


@dataclass
class AttackArmor:
    """Attack armor data"""

    at: int | None = None
    body_at: int | None = None
    head_at: int | None = None
    arms_at: int | None = None
    legs_at: int | None = None
