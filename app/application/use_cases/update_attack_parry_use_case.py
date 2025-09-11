from typing import Optional
from app.domain.entities import Attack
from app.domain.services.attack_calculator import AttackCalculator
from app.application.ports import AttackNotificationPort, AttackRepository
from app.application.commands import UpdateAttackParryCommand


class UpdateAttackParryUseCase:
    """Use case for updating an attack"""

    def __init__(
        self,
        attack_repository: AttackRepository,
        attack_calculator: AttackCalculator,
        notification_port: Optional[AttackNotificationPort] = None,
    ):
        self._attack_repository = attack_repository
        self._attack_calculator = attack_calculator
        self._notification_port = notification_port

    async def execute(self, command: UpdateAttackParryCommand) -> Optional[Attack]:
        command.validate()
        attack = await self._attack_repository.find_by_id(command.attack_id)
        if not attack:
            return None
        attack.modifiers.roll_modifiers.parry = command.parry
        self._attack_calculator.initialize_attack_calculations(attack)
        self._attack_calculator.calculate_attack_roll_modifiers(attack)
        await self._attack_repository.update(attack)
        if self._notification_port:
            await self._notification_port.notify_attack_updated(attack)
        return attack
