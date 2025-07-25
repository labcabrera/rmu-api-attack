from app.domain.entities import Attack
from app.domain.entities.enums import AttackStatus
from app.domain.services import AttackDomainService
from app.application.commands import CreateAttackCommand


class UpdateAttackRollUseCase:

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, attack_id: str) -> Attack:
        """Execute the update attack roll use case."""

        return await self._domain_service.execute_attack_roll(
            attack_id=attack_id, roll_value=0
        )
