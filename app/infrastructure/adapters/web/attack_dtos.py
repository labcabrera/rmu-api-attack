"""
Data Transfer Objects for the web API.
These convert between domain entities and API representations.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities import (
    Attack,
    AttackRollModifiers,
    AttackModifiers,
    AttackMode,
    AttackRoll,
    AttackResult,
    Critical,
)
from app.domain.entities.enums import AttackType, AttackStatus


class AttackRollDTO(BaseModel):
    """DTO for attack roll"""

    model_config = ConfigDict(use_enum_values=True)

    roll: int = Field(..., description="Roll result")


class CriticalDTO(BaseModel):
    """DTO for critical hit"""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Critical ID")
    status: str = Field(..., description="Critical status")


class AttackResultDTO(BaseModel):
    """DTO for attack result"""

    model_config = ConfigDict(use_enum_values=True)

    labelResult: str = Field(..., description="Result label")
    hitPoints: int = Field(..., description="Hit points")
    criticals: list[CriticalDTO] = Field(..., description="Critical hits")


class AttackRollModifiersDTO(BaseModel):
    """DTO for attack roll modifiers"""

    bo: int = Field(..., description="Source offensive bonus")
    bd: int = Field(..., description="Target defensive bonus")


class AttackModifiersDTO(BaseModel):
    """DTO for attack modifiers"""

    model_config = ConfigDict(use_enum_values=True)

    attackType: AttackType = Field(..., description="Type of attack (melee, ranged)")
    rollModifiers: AttackRollModifiersDTO = Field(
        ..., description="Modifiers for the attack roll"
    )


class AttackDTO(BaseModel):
    """DTO for complete attack"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": "atk_001",
                "actionId": "action_001",
                "status": "executed",
                "input": {
                    "sourceId": "source_001",
                    "targetId": "target_001",
                    "actionPoints": 3,
                    "round": 1,
                    "mode": "mainHand",
                },
                "roll": {"roll": 15},
                "results": {"labelResult": "8AT", "hitPoints": 8, "criticals": []},
            }
        },
    )

    id: str = Field(..., description="Attack ID")
    actionId: str = Field(..., description="Action ID")
    sourceId: str = Field(..., description="Source ID")
    targetId: str = Field(..., description="Target ID")
    status: str = Field(..., description="Attack status")
    modifiers: AttackModifiersDTO = Field(..., description="Attack input")
    roll: Optional[AttackRollDTO] = Field(None, description="Attack roll")
    results: Optional[AttackResultDTO] = Field(None, description="Attack results")


class CreateAttackRequestDTO(BaseModel):
    """DTO for create attack request"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "actionId": "action_001",
                "sourceId": "character_001",
                "targetId": "character_002",
                "modifiers": {
                    "attackType": "melee",
                    "rollModifiers": {"bo": 80, "bd": -20},
                },
            }
        },
    )

    actionId: str = Field(..., description="Action ID")
    sourceId: str = Field(..., description="Source ID")
    targetId: str = Field(..., description="Target ID")
    modifiers: AttackModifiersDTO = Field(
        ..., description="Attack modifiers including type and bonuses"
    )


class AttackNotFoundDTO(BaseModel):
    """DTO for attack not found error"""

    model_config = ConfigDict(use_enum_values=True)

    detail: str = Field(..., description="Error message")
    attack_id: str = Field(..., description="Attack ID that was not found")


class PaginationDTO(BaseModel):
    """DTO for pagination metadata"""

    model_config = ConfigDict(use_enum_values=True)

    page: int = Field(..., description="Current page number (0-based)")
    size: int = Field(..., description="Page size")
    totalElements: int = Field(..., description="Total number of elements")
    totalPages: int = Field(..., description="Total number of pages")


class PagedAttacksDTO(BaseModel):
    """DTO for paginated attack results"""

    model_config = ConfigDict(use_enum_values=True)

    content: list[AttackDTO] = Field(..., description="List of attacks")
    pagination: PaginationDTO = Field(..., description="Pagination metadata")
