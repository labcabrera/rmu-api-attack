"""
Data Transfer Objects for the web API.
These convert between domain entities and API representations.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

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
    boInjuryPenalty: int = Field(None, description="Injury penalty to offensive bonus")
    boActionsPointsPenalty: int = Field(
        None, description="Actions points penalty to offensive bonus"
    )
    boPacePenalty: int = Field(None, description="Pace penalty to offensive bonus")
    boFatiguePenalty: int = Field(
        None, description="Fatigue penalty to offensive bonus"
    )
    rangePenalty: int = Field(None, description="Range penalty")
    parry: int = Field(None, description="Parry value")
    customBonus: int = Field(None, description="Custom bonus to offensive bonus")


class AttackModifiersDTO(BaseModel):
    """DTO for attack modifiers"""

    model_config = ConfigDict(use_enum_values=True)

    attackType: AttackType = Field(..., description="Type of attack (melee, ranged)")
    rollModifiers: AttackRollModifiersDTO = Field(
        ..., description="Modifiers for the attack roll"
    )


class AttackBonusEntryDTO(BaseModel):
    """DTO for attack bonus entry"""

    key: str = Field(..., description="Bonus key")
    value: int = Field(..., description="Bonus value")


class AttackCalculationsDTO(BaseModel):
    """DTO for attack calculations"""

    model_config = ConfigDict(use_enum_values=True)

    modifiers: list[AttackBonusEntryDTO] = Field(
        ..., description="Attack modifiers in key-value pairs"
    )
    total: int = Field(..., description="Total calculated value")


class AttackDTO(BaseModel):
    """DTO for complete attack"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": "68837ba24b9293ca54e6ff72",
                "actionId": "action_001",
                "sourceId": "character_001",
                "targetId": "character_002",
                "status": "draft",
                "modifiers": {
                    "attackType": "melee",
                    "rollModifiers": {
                        "bo": 96,
                        "bd": -11,
                        "boInjuryPenalty": -5,
                        "boActionsPointsPenalty": -2,
                        "boPacePenalty": -3,
                        "boFatiguePenalty": -1,
                        "rangePenalty": 0,
                        "parry": 10,
                        "customBonus": 5,
                    },
                },
                "roll": {"roll": 55},
                "calculated": {
                    "modifiers": [
                        {"key": "roll", "value": 55},
                        {"key": "bo", "value": 96},
                        {"key": "bd", "value": -11},
                    ],
                    "total": 140,
                },
                "results": None,
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
    calculated: Optional[AttackCalculationsDTO] = Field(
        None, description="Calculated attack data"
    )
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
                    "rollModifiers": {
                        "bo": 96,
                        "bd": -11,
                        "boInjuryPenalty": -5,
                        "boActionsPointsPenalty": -2,
                        "boPacePenalty": -3,
                        "boFatiguePenalty": -1,
                        "rangePenalty": 0,
                        "parry": 10,
                        "customBonus": 5,
                    },
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


class UpdateAttackModifiersRequestDTO(BaseModel):
    """DTO for update attack modifiers request"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "modifiers": {
                    "attackType": "ranged",
                    "rollModifiers": {"bo": 90, "bd": -10},
                }
            }
        },
    )

    modifiers: AttackModifiersDTO = Field(
        ..., description="Updated attack modifiers including type and bonuses"
    )


class UpdateAttackRollRequestDTO(BaseModel):
    """DTO for update attack roll request"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "roll": 15,
            }
        },
    )

    roll: int = Field(..., description="Roll value to apply to the attack")


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
