from app.domain.entities import Attack
from app.domain.services import AttackCalculator
from app.application.commands import UpdateFumbleRollCommand

from app.application.ports import AttackRepository, AttackTableClient


class UpdateFumbleRollUseCase:
    """Use case for updating a fumble roll for an attack."""

    def __init__(
        self,
        attack_repository: AttackRepository,
        attack_calculator: AttackCalculator,
        attack_table_client: AttackTableClient,
    ):
        self._attack_repository = attack_repository
        self._attack_calculator = attack_calculator
        self._attack_table_client = attack_table_client

    async def execute(self, command: UpdateFumbleRollCommand) -> Attack:
        return await self.attack_resolution_service.update_fumble_roll(
            attack_id=command.attack_id,
            roll=command.roll,
        )
