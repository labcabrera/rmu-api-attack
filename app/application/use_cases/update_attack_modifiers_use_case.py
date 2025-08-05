from typing import Optional

from app.domain.entities import Attack
from app.domain.services.attack_calculator import AttackCalculator
from app.application.ports import AttackNotificationPort, AttackRepository

from app.application.commands import (
    UpdateAttackModifiersCommand,
)


class UpdateAttackModifiersUseCase:
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

    async def execute(self, command: UpdateAttackModifiersCommand) -> Optional[Attack]:
        """Execute the update attack use case"""

        command.validate()

        attack_id = command.attack_id
        attack = await self._attack_repository.find_by_id(attack_id)

        self._update_attack_modifiers_partially(attack, command.modifiers)

        if attack.roll:
            await self._attack_calculator.calculate_attack(attack)

        updated_attack = await self._attack_repository.update(attack)

        if self._notification_port and updated_attack:
            await self._notification_port.notify_attack_updated(updated_attack)

        return updated_attack

    def _update_attack_modifiers_partially(self, attack: Attack, new_modifiers) -> None:
        """
        Update attack modifiers partially, only modifying fields that are provided.
        This implements PATCH semantics instead of full replacement.
        """
        if not new_modifiers:
            return

        # Update main modifier fields if provided
        if (
            hasattr(new_modifiers, "attack_type")
            and new_modifiers.attack_type is not None
        ):
            attack.modifiers.attack_type = new_modifiers.attack_type

        if (
            hasattr(new_modifiers, "attack_table")
            and new_modifiers.attack_table is not None
        ):
            attack.modifiers.attack_table = new_modifiers.attack_table

        if (
            hasattr(new_modifiers, "attack_size")
            and new_modifiers.attack_size is not None
        ):
            attack.modifiers.attack_size = new_modifiers.attack_size

        if hasattr(new_modifiers, "at") and new_modifiers.at is not None:
            attack.modifiers.at = new_modifiers.at

        # Update roll modifiers if provided
        if (
            hasattr(new_modifiers, "roll_modifiers")
            and new_modifiers.roll_modifiers is not None
        ):
            self._update_roll_modifiers_partially(attack, new_modifiers.roll_modifiers)

        # Update situational modifiers if provided
        if (
            hasattr(new_modifiers, "situational_modifiers")
            and new_modifiers.situational_modifiers is not None
        ):
            self._update_situational_modifiers_partially(
                attack, new_modifiers.situational_modifiers
            )

    def _update_roll_modifiers_partially(
        self, attack: Attack, new_roll_modifiers
    ) -> None:
        """Update roll modifiers partially"""
        roll_mod = attack.modifiers.roll_modifiers

        # Update each roll modifier field if provided
        if hasattr(new_roll_modifiers, "bo") and new_roll_modifiers.bo is not None:
            roll_mod.bo = new_roll_modifiers.bo

        if (
            hasattr(new_roll_modifiers, "bo_injury_penalty")
            and new_roll_modifiers.bo_injury_penalty is not None
        ):
            roll_mod.bo_injury_penalty = new_roll_modifiers.bo_injury_penalty

        if (
            hasattr(new_roll_modifiers, "bo_actions_points_penalty")
            and new_roll_modifiers.bo_actions_points_penalty is not None
        ):
            roll_mod.bo_actions_points_penalty = (
                new_roll_modifiers.bo_actions_points_penalty
            )

        if (
            hasattr(new_roll_modifiers, "bo_pace_penalty")
            and new_roll_modifiers.bo_pace_penalty is not None
        ):
            roll_mod.bo_pace_penalty = new_roll_modifiers.bo_pace_penalty

        if (
            hasattr(new_roll_modifiers, "bo_fatigue_penalty")
            and new_roll_modifiers.bo_fatigue_penalty is not None
        ):
            roll_mod.bo_fatigue_penalty = new_roll_modifiers.bo_fatigue_penalty

        if hasattr(new_roll_modifiers, "bd") and new_roll_modifiers.bd is not None:
            roll_mod.bd = new_roll_modifiers.bd

        if (
            hasattr(new_roll_modifiers, "bd_shield")
            and new_roll_modifiers.bd_shield is not None
        ):
            roll_mod.bd_shield = new_roll_modifiers.bd_shield

        if (
            hasattr(new_roll_modifiers, "range_penalty")
            and new_roll_modifiers.range_penalty is not None
        ):
            roll_mod.range_penalty = new_roll_modifiers.range_penalty

        if (
            hasattr(new_roll_modifiers, "parry")
            and new_roll_modifiers.parry is not None
        ):
            roll_mod.parry = new_roll_modifiers.parry

        if (
            hasattr(new_roll_modifiers, "custom_bonus")
            and new_roll_modifiers.custom_bonus is not None
        ):
            roll_mod.custom_bonus = new_roll_modifiers.custom_bonus

    def _update_situational_modifiers_partially(
        self, attack: Attack, new_situational_modifiers
    ) -> None:
        """Update situational modifiers partially"""
        sit_mod = attack.modifiers.situational_modifiers

        # Update each situational modifier field if provided
        if (
            hasattr(new_situational_modifiers, "cover")
            and new_situational_modifiers.cover is not None
        ):
            sit_mod.cover = new_situational_modifiers.cover

        if (
            hasattr(new_situational_modifiers, "restricted_quarters")
            and new_situational_modifiers.restricted_quarters is not None
        ):
            sit_mod.restricted_quarters = new_situational_modifiers.restricted_quarters

        if (
            hasattr(new_situational_modifiers, "positional_source")
            and new_situational_modifiers.positional_source is not None
        ):
            sit_mod.positional_source = new_situational_modifiers.positional_source

        if (
            hasattr(new_situational_modifiers, "positional_target")
            and new_situational_modifiers.positional_target is not None
        ):
            sit_mod.positional_target = new_situational_modifiers.positional_target

        if (
            hasattr(new_situational_modifiers, "dodge")
            and new_situational_modifiers.dodge is not None
        ):
            sit_mod.dodge = new_situational_modifiers.dodge

        if (
            hasattr(new_situational_modifiers, "stunned_target")
            and new_situational_modifiers.stunned_target is not None
        ):
            sit_mod.stunned_target = new_situational_modifiers.stunned_target

        if (
            hasattr(new_situational_modifiers, "disabled_db")
            and new_situational_modifiers.disabled_db is not None
        ):
            sit_mod.disabled_db = new_situational_modifiers.disabled_db

        if (
            hasattr(new_situational_modifiers, "disabled_shield")
            and new_situational_modifiers.disabled_shield is not None
        ):
            sit_mod.disabled_shield = new_situational_modifiers.disabled_shield

        if (
            hasattr(new_situational_modifiers, "surprised")
            and new_situational_modifiers.surprised is not None
        ):
            sit_mod.surprised = new_situational_modifiers.surprised

        if (
            hasattr(new_situational_modifiers, "prone_attacker")
            and new_situational_modifiers.prone_attacker is not None
        ):
            sit_mod.prone_attacker = new_situational_modifiers.prone_attacker

        if (
            hasattr(new_situational_modifiers, "prone_defender")
            and new_situational_modifiers.prone_defender is not None
        ):
            sit_mod.prone_defender = new_situational_modifiers.prone_defender

        if (
            hasattr(new_situational_modifiers, "size_difference")
            and new_situational_modifiers.size_difference is not None
        ):
            sit_mod.size_difference = new_situational_modifiers.size_difference

        if (
            hasattr(new_situational_modifiers, "off_hand")
            and new_situational_modifiers.off_hand is not None
        ):
            sit_mod.off_hand = new_situational_modifiers.off_hand

        if (
            hasattr(new_situational_modifiers, "higher_ground")
            and new_situational_modifiers.higher_ground is not None
        ):
            sit_mod.higher_ground = new_situational_modifiers.higher_ground

        if (
            hasattr(new_situational_modifiers, "range")
            and new_situational_modifiers.range is not None
        ):
            sit_mod.range = new_situational_modifiers.range

        if (
            hasattr(new_situational_modifiers, "ranged_attack_in_melee")
            and new_situational_modifiers.ranged_attack_in_melee is not None
        ):
            sit_mod.ranged_attack_in_melee = (
                new_situational_modifiers.ranged_attack_in_melee
            )
