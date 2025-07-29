from typing import Optional
from app.domain.entities import Attack, AttackRoll
from app.domain.ports import AttackRepository, AttackNotificationPort
from app.domain.entities.enums import AttackStatus
from .attack_calculator import AttackCalculator


class AttackResolutionService:
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

    async def update_attack_roll(self, attack_id: str, roll: int) -> Attack:
        # TODO check valid status
        attack = await self._attack_repository.find_by_id(attack_id)
        attack.roll = AttackRoll(roll=roll)
        await self._attack_calculator.calculate_attack(attack)
        updated_attack = await self._attack_repository.update(attack)
        return updated_attack

    async def update_critical_roll(
        self, attack_id: str, critical_key: str, roll: int
    ) -> Attack:
        # TODO check valid status
        attack = await self._attack_repository.find_by_id(attack_id)

        critical_result = attack.results.get_critical_by_key(critical_key)
        if not critical_result:
            raise ValueError("Invalid critical key")
        if not attack.roll.critical_rolls:
            attack.roll.critical_rolls = {}

        attack.roll.critical_rolls[critical_key] = roll
        # TODO calculations
        updated_attack = await self._attack_repository.update(attack)
        return updated_attack

    async def update_fumble_roll(self, attack_id: str, roll: int) -> Attack:
        # TODO check valid status
        attack = await self._attack_repository.find_by_id(attack_id)
        # TODO
        return attack
