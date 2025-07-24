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
from app.application.commands import CreateAttackCommand


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


# Conversion functions between DTOs and domain entities


def create_request_to_command(dto: CreateAttackRequestDTO) -> "CreateAttackCommand":
    """Convert CreateAttackRequestDTO to CreateAttackCommand"""

    # attack_type = dto.modifiers.attackType
    attack_type = AttackType.MELEE

    modifiers = AttackModifiers(
        attack_type=attack_type,
        roll_modifiers=AttackRollModifiers(
            bo=dto.modifiers.rollModifiers.bo,
            bo_injury_penalty=0,
            bo_actions_points_penalty=0,
            bo_pace_penalty=0,
            bo_fatigue_penalty=0,
            bd=dto.modifiers.rollModifiers.bd,
            range_penalty=0,
            parry=0,
            custom_bonus=0,
        ),
    )

    return CreateAttackCommand(
        action_id=dto.actionId,
        source_id=dto.sourceId,
        target_id=dto.targetId,
        modifiers=modifiers,
    )


def attack_to_dto(attack: Attack) -> AttackDTO:
    """Convert domain Attack to DTO"""
    modifiers_dto = AttackModifiersDTO(
        attackType=attack.modifiers.attack_type,
        rollModifiers=AttackRollModifiersDTO(
            bo=attack.modifiers.roll_modifiers.bo,
            bd=attack.modifiers.roll_modifiers.bd,
        ),
    )

    roll_dto = None
    if attack.roll:
        roll_dto = AttackRollDTO(roll=attack.roll.roll)

    results_dto = None
    if attack.results:
        criticals_dto = [
            CriticalDTO(id=c.id, status=c.status) for c in attack.results.criticals
        ]
        results_dto = AttackResultDTO(
            labelResult=attack.results.label_result,
            hitPoints=attack.results.hit_points,
            criticals=criticals_dto,
        )

    return AttackDTO(
        id=attack.id,
        actionId=attack.tactical_game_id,
        status=attack.status,
        modifiers=modifiers_dto,
        roll=roll_dto,
        results=results_dto,
    )


def create_request_to_domain(dto: CreateAttackRequestDTO) -> Attack:
    """Convert CreateAttackRequestDTO to domain Attack"""
    attack_modifiers = AttackModifiers(
        attack_type=dto.modifiers.attackType,
        roll_modifiers=AttackRollModifiers(
            bo=dto.modifiers.rollModifiers.bo,
            bo_injury_penalty=0,
            bo_actions_points_penalty=0,
            bo_pace_penalty=0,
            bo_fatigue_penalty=0,
            bd=dto.modifiers.rollModifiers.bd,
            range_penalty=0,
            parry=0,
            custom_bonus=0,
        ),
    )

    return Attack(
        id=None,
        tactical_game_id=dto.actionId,
        status=AttackStatus.DRAFT,
        modifiers=attack_modifiers,
    )
