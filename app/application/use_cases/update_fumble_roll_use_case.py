from app.domain.entities import Attack
from app.domain.services import AttackCalculator
from app.application.commands import UpdateFumbleRollCommand

from app.application.ports import AttackRepository, AttackTableClient
from app.domain.entities.attack_fumble_result import AttackFumbleResult
from app.domain.entities.enums import AttackStatus, FumbleStatus


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
        attack_id = command.attack_id
        attack = await self._attack_repository.find_by_id(attack_id)
        roll = command.roll
        if not attack.status == AttackStatus.PENDING_FUMBLE_ROLL:
            raise ValueError("Attack is not in a state to roll fumbles")

        fumble_table = attack.modifiers.fumble_table
        adjusted_roll = min(100, max(roll, 1))

        fumble_table_entry = await self._attack_table_client.get_fumble_table_entry(
            fumble_table, adjusted_roll
        )

        # TODO calculate
        additionalDamageText = "TODO"
        damage = 0
        attack.results.fumble = AttackFumbleResult(
            status=FumbleStatus.PENDING_APPLY,
            text=fumble_table_entry.text,
            additional_damage_text=additionalDamageText,
            damage=damage,
            effects=fumble_table_entry.effects,
        )

        updated_attack = await self._attack_repository.update(attack)
        return updated_attack
