from typing import Optional

from app.domain.entities.attack import (
    Attack,
    AttackCalculations,
    AttackBonusEntry,
    AttackResult,
)
from app.domain.entities.attack_table import AttackTableEntry
from app.domain.ports.attack_ports import AttackNotificationPort, AttackRepository
from app.domain.ports.attack_table_port import AttackTableClient

from app.infrastructure.logging.logger_config import get_logger

logger = get_logger(__name__)


class AttackCalculator:

    def __init__(
        self,
        notification_port: Optional[AttackNotificationPort] = None,
        attack_table_client: AttackTableClient = None,
    ):
        self._notification_port = notification_port
        self._attack_table_client = attack_table_client

    async def calculate_attack(self, attack: Attack) -> None:
        self.validate_attack(attack)
        self.update_attack_calculated_modifiers(attack)
        await self.calculate_attack_results(attack)

    def validate_attack(self, attack: Attack) -> None:
        if not attack:
            raise ValueError("Attack cannot be None")
        if not attack.roll:
            raise ValueError("Attack must have a roll to calculate results")
        if not attack.modifiers:
            raise ValueError("Attack must have modifiers to calculate results")

    async def calculate_attack_results(self, attack: Attack) -> None:
        self.update_attack_calculated_modifiers(attack)
        if self._attack_table_client:
            attack_table_entry = await self._attack_table_client.get_attack_table_entry(
                attack_table=attack.modifiers.attack_table,
                size=attack.modifiers.attack_size,
                roll=attack.calculated.total,
                at=5,
            )
            attack.results = AttackResult(
                attack_table_entry=attack_table_entry,
                criticals=[],
            )

    def update_attack_calculated_modifiers(self, attack: Attack) -> None:
        attack.calculated = AttackCalculations(total=0, modifiers=[])
        roll_modifiers = attack.modifiers.roll_modifiers

        self.append_bonus(attack, "roll", attack.roll.roll)
        self.append_bonus(attack, "bo", roll_modifiers.bo)
        self.append_injury_penalty(attack)
        self.append_bonus(attack, "fatigue-penalty", roll_modifiers.fatigue_penalty)
        self.append_pace_penalty(attack)
        self.append_bonus(attack, "range-penalty", roll_modifiers.range_penalty)
        self.append_bonus_bd(attack)
        self.append_bonus_bd_shield(attack)
        self.append_parry(attack)
        self.append_bonus(attack, "custom-bonus", roll_modifiers.custom_bonus)

        attack.calculated.modifiers = [
            p for p in attack.calculated.modifiers if p.value != 0
        ]

        attack.calculated.total = sum(p.value for p in attack.calculated.modifiers)

    def append_bonus(self, attack: Attack, key: str, value: int) -> None:
        attack.calculated.modifiers.append(AttackBonusEntry(key=key, value=value))

    def append_with_skill(
        self, attack: Attack, key: str, value: int, skill_id: str
    ) -> None:
        if not value or value == 0:
            return
        skill_bonus = self.get_skill_bonus(attack, skill_id)
        skill_bonus_adjusted = min(abs(value), skill_bonus)
        self.append_bonus(attack, key, value)
        self.append_bonus(attack, f"{key}-skill-{skill_id}", skill_bonus_adjusted)

    def get_skill_bonus(self, attack: Attack, skill_id: str) -> int:
        for skill in attack.modifiers.source_skills:
            if skill.skill_id == skill_id:
                return skill.bonus
        return 0

    def append_bonus_bd(self, attack: Attack) -> None:
        if not attack.modifiers.situational_modifiers.disabled_db:
            self.append_bonus(attack, "bd", attack.modifiers.roll_modifiers.bd)

    def append_bonus_bd_shield(self, attack: Attack) -> None:
        if not attack.modifiers.situational_modifiers.disabled_shield:
            self.append_bonus(attack, "shield", attack.modifiers.roll_modifiers.shield)

    def append_injury_penalty(self, attack: Attack) -> None:
        self.append_bonus(
            attack,
            "injury-penalty",
            attack.modifiers.roll_modifiers.injury_penalty,
        )

    def append_pace_penalty(self, attack: Attack) -> None:
        # Only use footwork skill for melee attacks
        if attack.is_melee():
            self.append_with_skill(
                attack,
                "pace-penalty",
                attack.modifiers.roll_modifiers.pace_penalty,
                "footwork",
            )
        else:
            self.append_bonus(
                attack,
                "pace-penalty",
                attack.modifiers.roll_modifiers.pace_penalty,
            )

    def append_parry(self, attack: Attack) -> None:
        if not attack.modifiers.situational_modifiers.disabled_parry:
            self.append_bonus(attack, "parry", attack.modifiers.roll_modifiers.parry)
