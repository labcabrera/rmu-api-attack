"""
Use cases for the Attack system.
These orchestrate domain operations and contain application-specific logic.
"""

from typing import Optional, List, Dict, Any
from app.domain.entities import Attack, AttackModifiers, AttackMode, Critical
from app.domain.ports import AttackRepository, AttackNotificationPort
from app.domain.services import AttackDomainService
from app.application.commands import CreateAttackCommand
from app.domain.entities.enums import AttackStatus


class CreateAttackUseCase:
    """Use case for creating a new attack"""

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, command: CreateAttackCommand) -> Attack:
        """Execute the create attack use case"""

        command.validate()
        attack = Attack(
            id=None,
            actionId=command.action_id,
            source_id=command.source_id,
            target_id=command.target_id,
            modifiers=command.modifiers,
            status=AttackStatus.PENDING,
        )
        return await self._domain_service.create_attack(attack)


class GetAttackUseCase:
    """Use case for retrieving an attack by ID"""

    def __init__(self, attack_repository: AttackRepository):
        self._attack_repository = attack_repository

    async def execute(self, attack_id: str) -> Optional[Attack]:
        """Execute the get attack use case"""
        return await self._attack_repository.find_by_id(attack_id)


class ListAttacksUseCase:
    """Use case for listing attacks"""

    def __init__(self, attack_repository: AttackRepository):
        self._attack_repository = attack_repository

    async def execute(
        self,
        tactical_game_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
        """Execute the list attacks use case"""
        return await self._attack_repository.find_all(
            tactical_game_id=tactical_game_id, status=status, limit=limit, skip=skip
        )


class UpdateAttackUseCase:
    """Use case for updating an attack"""

    def __init__(
        self,
        attack_repository: AttackRepository,
        notification_port: Optional[AttackNotificationPort] = None,
    ):
        self._attack_repository = attack_repository
        self._notification_port = notification_port

    async def execute(
        self, attack_id: str, update_data: Dict[str, Any]
    ) -> Optional[Attack]:
        """Execute the update attack use case"""
        attack = await self._attack_repository.find_by_id(attack_id)
        if not attack:
            return None

        # Apply updates to the attack
        if "status" in update_data:
            attack.status = update_data["status"]

        if "roll" in update_data and update_data["roll"]:
            attack.execute_roll(update_data["roll"]["roll"])

        if "results" in update_data and update_data["results"]:
            results_data = update_data["results"]
            criticals = []
            if "criticals" in results_data:
                criticals = [
                    Critical(id=c.get("id", ""), status=c.get("status", ""))
                    for c in results_data["criticals"]
                ]
            attack.apply_results(
                results_data.get("label_result", ""),
                results_data.get("hit_points", 0),
                criticals,
            )

        # Update the attack
        updated_attack = await self._attack_repository.update(attack)

        # Notify about update
        if self._notification_port and updated_attack:
            await self._notification_port.notify_attack_updated(updated_attack)

        return updated_attack


class DeleteAttackUseCase:
    """Use case for deleting an attack"""

    def __init__(self, attack_repository: AttackRepository):
        self._attack_repository = attack_repository

    async def execute(self, attack_id: str) -> bool:
        """Execute the delete attack use case"""
        return await self._attack_repository.delete(attack_id)


class ExecuteAttackRollUseCase:
    """Use case for executing an attack roll"""

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, attack_id: str, roll_value: int) -> Optional[Attack]:
        """Execute the attack roll use case"""
        return await self._domain_service.execute_attack_roll(attack_id, roll_value)


class ApplyAttackResultsUseCase:
    """Use case for applying attack results"""

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(
        self,
        attack_id: str,
        label: str,
        hit_points: int,
        criticals: List[Critical] = None,
    ) -> Optional[Attack]:
        """Execute the apply attack results use case"""
        return await self._domain_service.apply_attack_results(
            attack_id, label, hit_points, criticals
        )
