"""
Domain enumerations for the RMU Attack system.
"""

from enum import Enum
from typing import Union


class AttackStatus(Enum):
    """Attack status enumeration"""

    DRAFT = "draft"
    READY_TO_ROLL = "ready_to_roll"
    ROLLED = "ready_to_critical_roll"
    CALCULATED = "calculated"
    APPLIED = "applied"
    FAILED = "failed"


class AttackSize(Enum):
    """Attack size enumeration"""

    SMALL = "small"
    MEDIUM = "medium"
    BIG = "big"


class AttackType(Enum):
    """Attack type enumeration"""

    MELEE = "melee"
    RANGED = "ranged"

    @classmethod
    def from_value(cls, value: Union[str, "AttackType"]) -> "AttackType":
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            for i in cls:
                if i.value == value:
                    return i
        raise TypeError(f"Invalid Cover value: {value}")


class PositionalSource(Enum):
    """Positional attacker enumeration"""

    NONE = "none"
    TO_FLANK = "to_flank"
    TO_REAR = "to_rear"

    @classmethod
    def from_value(cls, value: Union[str, "PositionalSource"]) -> "PositionalSource":
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            for i in cls:
                if i.value == value:
                    return i
        raise TypeError(f"Invalid PositionalSource value: {value}")


class PositionalTarget(Enum):
    """Positional target enumeration"""

    NONE = "none"
    FLANK = "flank"
    REAR = "rear"

    @classmethod
    def from_value(cls, value: Union[str, "PositionalTarget"]) -> "PositionalTarget":
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            for i in cls:
                if i.value == value:
                    return i
        raise TypeError(f"Invalid PositionalTarget value: {value}")


class ProneStatus(Enum):
    """Prone status enumeration"""

    NONE = "none"
    PRONE = "prone"

    @classmethod
    def from_value(cls, value: Union[str, "ProneStatus"]) -> "ProneStatus":
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            for i in cls:
                if i.value == value:
                    return i
        raise TypeError(f"Invalid ProneStatus value: {value}")


class Cover(Enum):
    """Cover status enumeration"""

    NONE = "none"
    PARTIAL = "partial"
    HALF = "half"
    FULL = "full"

    @classmethod
    def from_value(cls, value: Union[str, "Cover"]) -> "Cover":
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            for i in cls:
                if i.value == value:
                    return i
        raise TypeError(f"Invalid Cover value: {value}")


class DodgeType(Enum):
    """Dodge type enumeration"""

    NONE = "none"
    PASSIVE = "passive"
    PARTIAL = "partial"
    FULL = "full"

    @classmethod
    def from_value(cls, value: Union[str, "DodgeType"]) -> "DodgeType":
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            for i in cls:
                if i.value == value:
                    return i
        raise TypeError(f"Invalid DodgeType value: {value}")


class RestrictedQuarters(Enum):
    """Restricted quarters enumeration"""

    NONE = "none"
    CLOSE = "close"
    CRAMPED = "cramped"
    TIGHT = "tight"
    CONFINED = "confined"

    @classmethod
    def from_value(
        cls, value: Union[str, "RestrictedQuarters"]
    ) -> "RestrictedQuarters":
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            for i in cls:
                if i.value == value:
                    return i
        raise TypeError(f"Invalid RestrictedQuarters value: {value}")
