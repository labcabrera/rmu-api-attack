from app.domain.entities import Attack
from app.application.commands import UpdateCriticalRollCommand
from app.application.ports import AttackRepository, AttackTableClient
from app.domain.services import AttackCalculator
from app.domain.entities.enums import AttackStatus, CriticalStatus


class UpdateCriticalRollUseCase:
    """Use case for updating a critical roll for an attack."""

    def __init__(
        self,
        attack_repository: AttackRepository,
        attack_calculator: AttackCalculator,
        attack_table_client: AttackTableClient,
    ):
        self._attack_repository = attack_repository
        self._attack_calculator = attack_calculator
        self._attack_table_client = attack_table_client

    async def execute(self, command: UpdateCriticalRollCommand) -> Attack:
        attack_id = command.attack_id
        attack = await self._attack_repository.find_by_id(attack_id)
        critical_key = command.critical_key
        roll = command.roll
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
