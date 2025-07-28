from app.domain.entities import Attack
from app.domain.services import AttackDomainService

from app.application.commands import UpdateCriticalRollCommand


class UpdateCriticalRollUseCase:
    """Use case for updating a critical roll for an attack."""

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, command: UpdateCriticalRollCommand) -> Attack:
        # TODO
        pass
