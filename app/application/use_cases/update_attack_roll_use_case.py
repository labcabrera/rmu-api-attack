from app.domain.entities import Attack

from app.application.commands import UpdateAttackRollCommand
from app.application.ports import AttackRepository
from app.domain.services import AttackCalculator


class UpdateAttackRollUseCase:

    def __init__(
        self,
        attack_repository: AttackRepository,
        attack_calculator: AttackCalculator,
    ):
        self._attack_repository = attack_repository
        self._attack_calculator = attack_calculator

    async def execute(self, command: UpdateAttackRollCommand) -> Attack:
        """Execute the update attack roll use case."""

        # TODO check valid status
        attack = await self._attack_repository.find_by_id(command.attack_id)
        attack.set_roll(roll=command.roll, location=command.location)
        await self._attack_calculator.calculate_attack(attack)
        updated_attack = await self._attack_repository.update(attack)
        return updated_attack
