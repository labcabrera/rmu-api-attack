import math
from typing import Optional
from app.domain.entities import (
    Attack,
    AttackCalculations,
    AttackBonusEntry,
    AttackFumbleResult,
    AttackResult,
    AttackCriticalResult,
    AttackTableEntry,
)
from app.domain.entities.enums import (
    AttackStatus,
    CriticalStatus,
    FumbleStatus,
)
from app.domain.services.attack_size_service import AttackSizeService
from app.application.ports import AttackNotificationPort, AttackTableClient
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class AttackCalculator:

    def __init__(
        self,
        notification_port: Optional[AttackNotificationPort] = None,
        attack_table_client: AttackTableClient = None,
        attack_size_service: AttackSizeService = None,
    ):
        self._notification_port = notification_port
        self._attack_table_client = attack_table_client
        self._attack_size_service = attack_size_service

    async def calculate_attack(self, attack: Attack) -> None:
        self.validate_attack(attack)
        self.initialize_attack_calculations(attack)
        self.calculate_attack_roll_modifiers(attack)
        if not attack.is_fumble():
            self.calculate_critical_modifiers(attack)
            self.calculate_critical_severity_modifiers(attack)
            await self.calculate_attack_results(attack)
            self.create_critical_results(attack)
        else:
            self.calculate_fumble_result(attack)
        self.update_status(attack)

    def validate_attack(self, attack: Attack) -> None:
        if not attack:
            raise ValueError("Attack cannot be None")
        if not attack.roll:
            raise ValueError("Attack must have a roll to calculate results")
        if not attack.modifiers:
            raise ValueError("Attack must have modifiers to calculate results")
        if attack.status is AttackStatus.APPLIED:
            raise ValueError("Attack already applied, cannot recalculate")

    def initialize_attack_calculations(self, attack: Attack) -> None:
        critical_size_modifier = AttackSizeService.get_critical_size_modifier(attack)
        hit_size_multiplier = AttackSizeService.get_hit_size_multiplier(attack)
        attack.calculated = AttackCalculations(
            roll_total=0,
            roll_modifiers=[],
            critical_modifiers=[],
            critical_total=0,
            critical_severity_modifiers=[],
            critical_severity_total=0,
            critical_size_modifier=critical_size_modifier,
            hit_size_multiplier=hit_size_multiplier,
        )
        attack.results = AttackResult(
            attack_table_entry=None,
            criticals=[],
            fumble=None,
        )

    async def calculate_attack_results(self, attack: Attack) -> None:
        if not self._attack_table_client:
            raise ValueError("No attack table client configured")

        attack_table_entry = await self._attack_table_client.get_attack_table_entry(
            attack_table=attack.modifiers.attack_table,
            size=attack.modifiers.attack_size,
            roll=attack.calculated.roll_total,
            at=attack.roll.at,
        )
        self.apply_size_modifiers(attack_table_entry, attack)
        attack.results = AttackResult(
            attack_table_entry=attack_table_entry,
            criticals=[],
        )

    def apply_size_modifiers(
        self, attack_table_entry: AttackTableEntry, attack: Attack
    ) -> None:
        attack_table_entry.damage_base = attack_table_entry.damage
        attack_table_entry.critical_severity_base = attack_table_entry.critical_severity
        if attack_table_entry.damage_base:
            attack_table_entry.damage = math.ceil(
                attack_table_entry.damage_base * attack.calculated.hit_size_multiplier
            )
        if attack_table_entry.critical_severity:
            attack_table_entry.critical_severity = (
                self._attack_size_service.get_adjusted_severity(
                    attack_table_entry.critical_severity_base,
                    attack.calculated.critical_size_modifier,
                )
            )

    def calculate_attack_roll_modifiers(self, attack: Attack) -> None:
        attack.append_all_modifiers()
        attack.calculated.roll_modifiers = [
            p for p in attack.calculated.roll_modifiers if p.value != 0
        ]
        attack.calculated.roll_total = sum(
            p.value for p in attack.calculated.roll_modifiers
        )

    def get_skill_bonus(self, attack: Attack, skill_id: str) -> int:
        for skill in attack.modifiers.source_skills:
            if skill.skill_id == skill_id:
                return skill.bonus
        return 0

    def calculate_critical_modifiers(self, attack: Attack) -> None:
        if attack.calculated.roll_total > 175:
            diff = attack.calculated.roll_total - 175
            absolute_hit_bonus = math.ceil(diff / 5)
            attack.calculated.critical_modifiers.append(
                AttackBonusEntry("absolute-hit", absolute_hit_bonus)
            )

        attack.calculated.critical_total = sum(
            p.value for p in attack.calculated.critical_modifiers
        )

    def calculate_critical_severity_modifiers(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.size_difference != 0:
            attack.calculated.critical_severity_modifiers.append(
                AttackBonusEntry(
                    "size-difference",
                    attack.modifiers.situational_modifiers.size_difference,
                )
            )
        attack.calculated.critical_severity_total = sum(
            p.value for p in attack.calculated.critical_severity_modifiers
        )

    def calculate_fumble_result(self, attack: Attack) -> None:
        attack.fumble = AttackFumbleResult(
            status=AttackStatus.PENDING_FUMBLE_ROLL,
        )

    def create_critical_results(self, attack: Attack) -> None:
        if (
            not attack.results.attack_table_entry
            or not attack.results.attack_table_entry.critical_type
        ):
            return

        critical_severity_map: dict[str, list[str]] = {
            "Z": ["Z"],
            "A": ["A"],
            "B": ["B"],
            "C": ["C"],
            "D": ["D"],
            "E": ["E"],
            "F": ["E", "A"],
            "G": ["E", "B"],
            "H": ["E", "C"],
            "I": ["E", "C", "A"],
            "J": ["J", "C", "B"],
        }
        if (
            attack.results.attack_table_entry.critical_severity
            not in critical_severity_map
        ):
            raise ValueError(
                f"Invalid critical severity: {attack.results.attack_table_entry.critical_severity}"
            )
        severity_list = critical_severity_map.get(
            attack.results.attack_table_entry.critical_severity, []
        )
        attack.results.criticals = [
            AttackCriticalResult(
                critical_type=attack.results.attack_table_entry.critical_type,
                critical_severity=severity,
                status=CriticalStatus.PENDING_CRITICAL_ROLL,
            )
            for severity in severity_list
        ]
        # TODO check additional critical features
        for idx, critical in enumerate(attack.results.criticals):
            critical.key = (
                f"{critical.critical_type}_{critical.critical_severity}_{idx+1}".lower()
            )

    def update_status(self, attack: Attack) -> None:
        if attack.results.criticals:
            attack.status = AttackStatus.PENDING_CRITICAL_ROLL
        elif attack.results.fumble:
            attack.status = AttackStatus.PENDING_FUMBLE_ROLL
        else:
            attack.status = AttackStatus.PENDING_APPLY

    def calculate_fumble_result(self, attack: Attack) -> None:
        attack.status = AttackStatus.PENDING_FUMBLE_ROLL
        attack.results.fumble = AttackFumbleResult(
            status=FumbleStatus.PENDING_FUMBLE_ROLL
        )
