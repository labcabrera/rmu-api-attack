from typing import Optional

from app.domain.entities import Attack, AttackRoll
from app.domain.entities.enums import AttackStatus, CriticalStatus
from app.application.ports import (
    AttackRepository,
    AttackNotificationPort,
    AttackTableClient,
)

from .attack_calculator import AttackCalculator


class AttackResolutionService:
    """Domain service for attack business logic"""

    def __init__(
        self,
        attack_repository: AttackRepository,
        attack_calculator: AttackCalculator,
        notification_port: Optional[AttackNotificationPort] = None,
        attack_table_client: AttackTableClient = None,
    ):
        self._attack_repository = attack_repository
        self._attack_calculator = attack_calculator
        self._notification_port = notification_port
        self._attack_table_client = attack_table_client

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

        attack = await self._attack_repository.find_by_id(attack_id)
        if not attack.status == AttackStatus.PENDING_CRITICAL_ROLL:
            raise ValueError("Attack is not in a state to roll criticals")

        critical_result = attack.results.get_critical_by_key(critical_key)
        if not critical_result:
            raise ValueError("Invalid critical key")
        if not attack.roll.critical_rolls:
            attack.roll.critical_rolls = {}

        attack.roll.critical_rolls[critical_key] = roll
        # TODO calculations

        roll_bonus = attack.calculated.critical_total or 0
        adjusted_roll = min(100, max(roll + roll_bonus, 1))

        critical_table_entry = await self._attack_table_client.get_critical_table_entry(
            critical_type=critical_result.critical_type,
            critical_severity=critical_result.critical_severity,
            roll=adjusted_roll,
        )
        critical_result.adjusted_roll = adjusted_roll
        critical_result.status = CriticalStatus.PENDING_APPLY
        critical_result.result = critical_table_entry

        updated_attack = await self._attack_repository.update(attack)
        return updated_attack

    async def update_fumble_roll(self, attack_id: str, roll: int) -> Attack:
        # TODO check valid status
        attack = await self._attack_repository.find_by_id(attack_id)
        # TODO
        return attack
