from app.domain.entities import Attack
from app.domain.services import AttackDomainService

from app.application.commands import UpdateFumbleRollCommand


class UpdateFumbleRollUseCase:
    """Use case for updating a fumble roll for an attack."""

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, command: UpdateFumbleRollCommand) -> Attack:
        # TODO
        pass
