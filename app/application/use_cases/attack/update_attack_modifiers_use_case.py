from typing import Any, Dict, Optional
from app.domain.entities.attack import Attack
from app.domain.entities.critical import Critical
from app.domain.ports.attack_ports import AttackNotificationPort, AttackRepository
from app.application.commands.update_attack_modifiers_command import (
    UpdateAttackModifiersCommand,
)


class UpdateAttackModifiersUseCase:
    """Use case for updating an attack"""

    def __init__(
        self,
        attack_repository: AttackRepository,
        notification_port: Optional[AttackNotificationPort] = None,
    ):
        self._attack_repository = attack_repository
        self._notification_port = notification_port

    async def execute(self, command: UpdateAttackModifiersCommand) -> Optional[Attack]:
        """Execute the update attack use case"""

        attack_id = command.attack_id
        attack = await self._attack_repository.find_by_id(attack_id)

        attack.modifiers = command.modifiers

        updated_attack = await self._attack_repository.update(attack)

        if self._notification_port and updated_attack:
            await self._notification_port.notify_attack_updated(updated_attack)

        return updated_attack
