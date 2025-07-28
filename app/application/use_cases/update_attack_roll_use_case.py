from app.domain.entities import Attack
from app.domain.services import AttackResolutionService

from app.domain.services import AttackResolutionService
from app.application.commands import UpdateAttackRollCommand


class UpdateAttackRollUseCase:

    def __init__(self, attack_resolution_service: AttackResolutionService):
        self._attack_resolution_service = attack_resolution_service

    async def execute(self, command: UpdateAttackRollCommand) -> Attack:
        """Execute the update attack roll use case."""

        return await self._attack_resolution_service.update_attack_roll(
            attack_id=command.attack_id, roll=command.roll
        )
