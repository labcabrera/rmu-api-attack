from typing import Optional

from app.domain.entities.attack import Attack, AttackCalculations, AttackBonusEntry
from app.domain.ports.attack_ports import AttackNotificationPort, AttackRepository


class AttackCalculator:

    def __init__(
        self,
        notification_port: Optional[AttackNotificationPort] = None,
    ):
        self._notification_port = notification_port

    async def calculate_attack(self, attack: Attack) -> Attack:
        self.validate_attack(attack)
        self.calculate_attack_results(attack)

    def validate_attack(self, attack: Attack) -> None:
        if not attack:
            raise ValueError("Attack cannot be None")
        if not attack.roll:
            raise ValueError("Attack must have a roll to calculate results")
        if not attack.modifiers:
            raise ValueError("Attack must have modifiers to calculate results")

    def calculate_attack_results(self, attack: Attack) -> Attack:

        attack.calculated = AttackCalculations(total=0, modifiers=[])

        attack.calculated.modifiers.append(
            AttackBonusEntry(key="bo", value=attack.modifiers.roll_modifiers.bo)
        )
        attack.calculated.modifiers.append(
            AttackBonusEntry(
                key="bo_injury_penalty",
                value=attack.modifiers.roll_modifiers.bo_injury_penalty,
            )
        )
        attack.calculated.modifiers.append(
            AttackBonusEntry(
                key="bo_action_points_penalty",
                value=attack.modifiers.roll_modifiers.bo_actions_points_penalty,
            )
        )
        attack.calculated.modifiers.append(
            AttackBonusEntry(key="bd", value=attack.modifiers.roll_modifiers.bd)
        )
        attack.calculated.modifiers = [
            p for p in attack.calculated.modifiers if p.value != 0
        ]

        attack.calculated.total = sum(p.value for p in attack.calculated.modifiers)
