"""
Converters between DTOs and domain entities for the Attack system.
This module handles conversion between web DTOs and domain entities/commands.
"""

from app.domain.entities import (
    Attack,
    AttackRollModifiers,
    AttackModifiers,
)
from app.domain.entities.enums import AttackType, AttackStatus
from app.application.commands import CreateAttackCommand
from .attack_dtos import (
    AttackDTO,
    AttackModifiersDTO,
    AttackRollModifiersDTO,
    CreateAttackRequestDTO,
    CriticalDTO,
    AttackResultDTO,
    AttackRollDTO,
)


class AttackDTOConverter:
    """Converter class for Attack DTOs"""

    @staticmethod
    def create_request_to_command(dto: CreateAttackRequestDTO) -> CreateAttackCommand:
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

    @staticmethod
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
            actionId=attack.action_id,
            sourceId=attack.source_id,
            targetId=attack.target_id,
            status=attack.status,
            modifiers=modifiers_dto,
            roll=roll_dto,
            results=results_dto,
        )

    @staticmethod
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
            action_id=dto.actionId,
            status=AttackStatus.DRAFT,
            modifiers=attack_modifiers,
        )


# Convenience functions that delegate to the converter class
def create_request_to_command(dto: CreateAttackRequestDTO) -> CreateAttackCommand:
    """Convert CreateAttackRequestDTO to CreateAttackCommand"""
    return AttackDTOConverter.create_request_to_command(dto)


def attack_to_dto(attack: Attack) -> AttackDTO:
    """Convert domain Attack to DTO"""
    return AttackDTOConverter.attack_to_dto(attack)


def create_request_to_domain(dto: CreateAttackRequestDTO) -> Attack:
    """Convert CreateAttackRequestDTO to domain Attack"""
    return AttackDTOConverter.create_request_to_domain(dto)
