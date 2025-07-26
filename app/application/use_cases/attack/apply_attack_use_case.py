from app.domain.entities import Attack
from app.domain.services import AttackDomainService


class ApplyAttackUseCase:
    """Use case for applying attack results."""

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, attack_id: str) -> Attack:
        """Execute the create attack use case."""

        return await self._domain_service.apply_attack_results(attack_id=attack_id)
