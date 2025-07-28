from app.domain.entities import Attack
from app.domain.services import AttackResolutionService

from app.application.commands import UpdateCriticalRollCommand


class UpdateCriticalRollUseCase:
    """Use case for updating a critical roll for an attack."""

    def __init__(self, attack_resolution_service: AttackResolutionService):
        self.attack_resolution_service = attack_resolution_service

    async def execute(self, command: UpdateCriticalRollCommand) -> Attack:
        return await self.attack_resolution_service.update_critical_roll(
            attack_id=command.attack_id,
            critical_key=command.critical_key,
            roll=command.roll,
        )
