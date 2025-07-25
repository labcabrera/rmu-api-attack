"""
Domain services for the Attack system.
These contain business logic that doesn't naturally fit into entities.
"""

from typing import Optional
from app.domain.entities import Attack, AttackRoll, AttackResult, Critical
from app.domain.ports import AttackRepository, AttackNotificationPort
from app.domain.entities.enums import AttackStatus
from app.domain.exceptions import (
    AttackInvalidStateException,
    AttackNotFoundException,
    AttackValidationException,
)
from .attack_calculator import AttackCalculator


class AttackDomainService:
    """Domain service for attack business logic"""

    def __init__(
        self,
        attack_repository: AttackRepository,
        attack_calculator: AttackCalculator,
        notification_port: Optional[AttackNotificationPort] = None,
    ):
        self._attack_repository = attack_repository
        self._attack_calculator = attack_calculator
        self._notification_port = notification_port

    async def create_attack(self, attack: Attack) -> Attack:
        """Create a new attack with business validation"""

        created_attack = await self._attack_repository.save(attack)
        if self._notification_port:
            await self._notification_port.notify_attack_created(created_attack)

        return created_attack

    async def update_attack_roll(self, attack_id: str, roll_value: int) -> Attack:
        """Execute a roll for an attack"""

        attack = await self._attack_repository.find_by_id(attack_id)
        attack.roll = AttackRoll(roll=roll_value)
        await self._attack_calculator.calculate_attack(attack)
        updated_attack = await self._attack_repository.update(attack)
        return updated_attack

    async def apply_attack_results(
        self,
        attack_id: str,
    ) -> Optional[Attack]:
        """Apply results to an attack"""

        attack = await self._attack_repository.find_by_id(attack_id)
        if not attack:
            raise AttackNotFoundException(attack_id=attack_id)
            return None
        if attack.status != AttackStatus.CALCULATED:
            raise AttackInvalidStateException(
                attack_id=attack.id,
                current_state=attack.status.value,
                expected_state=AttackStatus.CALCULATED.value,
                operation="apply_results",
            )
        if not attack.roll:
            raise AttackValidationException(
                attack_id=attack.id,
                message="Cannot apply results: attack roll is not executed",
            )

        # TODO send message to notification port
        if self._notification_port:
            await self._notification_port.notify_attack_results_applied(attack)
            attack.status = AttackStatus.APPLIED
            updated_attack = await self._attack_repository.update(attack)
            return updated_attack
        pass

    def calculate_attack_result(
        self, roll_value: int, attack_bonus: int = 0
    ) -> tuple[str, int]:
        """
        Calculate attack result based on roll value.
        This is a simplified RMU attack table calculation.
        """
        total_roll = roll_value + attack_bonus

        if total_roll >= 100:
            return "Critical Hit", 15
        elif total_roll >= 80:
            return "12AT", 12
        elif total_roll >= 60:
            return "8AT", 8
        elif total_roll >= 40:
            return "5AT", 5
        elif total_roll >= 20:
            return "3AT", 3
        else:
            return "Miss", 0
