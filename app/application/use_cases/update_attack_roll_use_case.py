from app.domain.entities import Attack
from app.domain.entities.enums import AttackStatus
from app.domain.services import AttackDomainService

from app.application.commands.update_attack_roll_command import UpdateAttackRollCommand


class UpdateAttackRollUseCase:

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, command: UpdateAttackRollCommand) -> Attack:
        """Execute the update attack roll use case."""

        return await self._domain_service.update_attack_roll(
            attack_id=command.attack_id, roll_value=command.roll
        )
