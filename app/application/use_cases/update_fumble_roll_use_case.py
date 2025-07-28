from app.domain.entities import Attack
from app.domain.services import AttackResolutionService

from app.application.commands import UpdateFumbleRollCommand


class UpdateFumbleRollUseCase:
    """Use case for updating a fumble roll for an attack."""

    def __init__(self, attack_resolution_service: AttackResolutionService):
        self.attack_resolution_service = attack_resolution_service

    async def execute(self, command: UpdateFumbleRollCommand) -> Attack:
        return await self.attack_resolution_service.update_fumble_roll(
            attack_id=command.attack_id,
            roll=command.roll,
        )
