"""
Domain enumerations for the RMU Attack system.
"""

from enum import Enum


class AttackMode(Enum):
    """Attack mode enumeration"""

    MAIN_HAND = "mainHand"
    OFF_HAND = "offHand"


class AttackType(Enum):
    """Attack type enumeration"""

    MELEE = "melee"
    RANGED = "ranged"


class AttackStatus(Enum):
    """Attack status enumeration"""

    DRAFT = "draft"
    READY_TO_ROLL = "ready_to_roll"
    ROLLED = "ready_to_critical_roll"
    CALCULATED = "calculated"
    APPLIED = "applied"
    FAILED = "failed"


class PositionalSource(Enum):
    """Positional attacker enumeration"""

    NONE = "none"
    TO_FLANK = "to_flank"
    TO_REAR = "to_rear"


class PositionalTarget(Enum):
    """Positional target enumeration"""

    NONE = "none"
    FLANK = "flank"
    REAR = "rear"


class ProneStatus(Enum):
    """Prone status enumeration"""

    NONE = "none"
    PRONE = "prone"


class Cover(Enum):
    """Cover status enumeration"""

    NONE = "none"
    PARTIAL = "partial"
    HALF = "half"
    FULL = "full"


class DodgeType(Enum):
    """Dodge type enumeration"""

    NONE = "none"
    PASSIVE = "passive"
    PARTIAL = "partial"
    FULL = "full"


class RestrictedQuarters(Enum):
    """Restricted quarters enumeration"""

    NONE = "none"
    CLOSE = "close"
    CRAMPED = "cramped"
    TIGHT = "tight"
    CONFINED = "confined"
