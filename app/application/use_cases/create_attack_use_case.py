from app.domain.entities import Attack
from app.domain.entities.enums import AttackStatus
from app.domain.services import AttackDomainService
from app.application.commands import CreateAttackCommand


class CreateAttackUseCase:
    """Use case for creating a new attack."""

    def __init__(self, domain_service: AttackDomainService):
        self._domain_service = domain_service

    async def execute(self, command: CreateAttackCommand) -> Attack:
        """Execute the create attack use case."""

        command.validate()
        attack = Attack(
            id=None,
            action_id=command.action_id,
            source_id=command.source_id,
            target_id=command.target_id,
            modifiers=command.modifiers,
            status=AttackStatus.DRAFT,
        )
        return await self._domain_service.create_attack(attack)
