import math
from typing import Optional
from uuid import uuid4

from app.domain.entities import (
    Attack,
    AttackCalculations,
    AttackBonusEntry,
    AttackFumbleResult,
    AttackResult,
    AttackCriticalResult
)
from app.domain.entities.enums import AttackStatus, Cover, CriticalStatus, FumbleStatus, PositionalSource, PositionalTarget, RestrictedQuarters

from app.domain.ports.attack_ports import AttackNotificationPort
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
        self.initialize_attack_calculations(attack)
        if not attack.is_fumble():
            self.calculate_attack_roll_modifiers(attack)
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
        attack.calculated = AttackCalculations(
            roll_total=0,
            roll_modifiers=[],
            critical_modifiers=[],
            critical_total=0,
            critical_severity_modifiers=[],
            critical_severity_total=0,
        )
        attack.results = AttackResult(
            attack_table_entry=None,
            criticals=[],
            fumble=None,
        )

    async def calculate_attack_results(self, attack: Attack) -> None:
        if self._attack_table_client:
            try:
                attack_table_entry = (
                    await self._attack_table_client.get_attack_table_entry(
                        attack_table=attack.modifiers.attack_table,
                        size=attack.modifiers.attack_size,
                        roll=attack.calculated.roll_total,
                        at=attack.modifiers.at,
                    )
                )
                attack.results = AttackResult(
                    attack_table_entry=attack_table_entry,
                    criticals=[],
                )
            except Exception as e:
                logger.error(f"Error calculating attack results: {e}")
                # TODO update attack message
                attack.status = AttackStatus.FAILED

    def calculate_attack_roll_modifiers(self, attack: Attack) -> None:
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
        self.append_off_hand(attack)
        self.append_restricted_quarters(attack)
        self.append_source_statuses(attack)
        self.append_target_statuses(attack)
        self.append_source_weapon_type(attack)
        self.append_positional_source(attack)
        self.append_positional_target(attack)
        self.append_cover(attack)
        self.append_range_in_melee_bonus(attack)
        self.append_size_bonus(attack)
        
        # TODO called shot

        attack.calculated.roll_modifiers = [
            p for p in attack.calculated.roll_modifiers if p.value != 0
        ]

        attack.calculated.roll_total = sum(p.value for p in attack.calculated.roll_modifiers)



    def append_bonus(self, attack: Attack, key: str, value: int) -> None:
        attack.calculated.roll_modifiers.append(AttackBonusEntry(key=key, value=value))

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

    def source_has_status(self, attack: Attack, status: str) -> bool:
        return status in attack.modifiers.situational_modifiers.source_status

    def target_has_status(self, attack: Attack, status: str) -> bool:
        return status in attack.modifiers.situational_modifiers.target_status

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

    def append_off_hand(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.off_hand:
            self.append_bonus(attack, "off-hand", -20)

    def append_restricted_quarters(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.restricted_quarters:
            bonus = 0;
            match attack.modifiers.situational_modifiers.restricted_quarters:
                case RestrictedQuarters.CLOSE:
                    bonus = -25
                case RestrictedQuarters.CRAMPED:
                    bonus = -50
                case RestrictedQuarters.TIGHT:
                    bonus = -75
                case RestrictedQuarters.CONFINED:
                    bonus = -100
            self.append_with_skill(attack, "restricted-quarters", bonus, "restricted-quarters")

    def append_positional_source(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.positional_source and attack.is_melee():
            bonus = 0
            match attack.modifiers.situational_modifiers.positional_source:
                case PositionalSource.TO_FLANK:
                    bonus = -30
                case PositionalSource.TO_REAR:
                    bonus = -70
            self.append_bonus(attack, "positional-source", bonus)
            reverse_strike_skill_bonus = self.get_skill_bonus(attack, "reverse-strike")
            self.append_bonus(attack, "positional-source-skill-reverse-strike", reverse_strike_skill_bonus)

    def append_positional_target(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.positional_target and attack.is_melee():
            bonus = 0
            match attack.modifiers.situational_modifiers.positional_target:
                case PositionalTarget.FLANK:
                    bonus = 15
                case PositionalTarget.REAR:
                    bonus = 35
            self.append_bonus(attack, "positional-target", bonus)

    def append_source_statuses(self, attack: Attack) -> None:
        if self.source_has_status(attack, "prone"):
            self.append_bonus(attack, "prone-source", -50)

    def append_target_statuses(self, attack: Attack) -> None:
        if self.target_has_status(attack, "stunned"):
            self.append_bonus(attack, "stunned-target", 20)
        if self.target_has_status(attack, "surprised"):
            self.append_bonus(attack, "surprised-target", 25)
        if self.target_has_status(attack, "prone"):
            if attack.is_melee():
                self.append_bonus(attack, "prone-target", 30)
            else:
                self.append_bonus(attack, "prone-target", -30)

    def append_source_weapon_type(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.off_hand:
            self.append_bonus(attack,"off-hand-weapon",-20)
            if self.source_has_status(attack, "ambidextrous"):
                self.append_bonus(attack, "ambidextrous", 20)
        if attack.modifiers.situational_modifiers.two_handed_weapon and attack.is_melee():
            self.append_bonus(attack, "two-handed-weapon", 10)

    def append_range_in_melee_bonus(self, attack: Attack) -> None:
        if not attack.is_melee() and self.source_has_status(attack, "melee"):
            self.append_bonus(attack, "range-in-melee", -20)

    def append_cover(self, attack: Attack) -> None:
        bonus = 0
        match attack.modifiers.situational_modifiers.cover:
            case Cover.SOFT_PARTIAL:
                bonus = -10 or not attack.is_melee() -20
            case Cover.SOFT_HALF:
                bonus = -20 or not attack.is_melee() -40
            case Cover.SOFT_FULL:
                bonus = -50 or not attack.is_melee() -100
            case Cover.HARD_PARTIAL:
                bonus = -20 or not attack.is_melee() -40
            case Cover.HARD_HALF:
                bonus = -40 or not attack.is_melee() -80
            case Cover.HARD_FULL:
                bonus = -100 or not attack.is_melee() -200
        self.append_bonus(attack, "cover", bonus)

    def append_size_bonus(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.size_difference and attack.modifiers.situational_modifiers.size_difference < 0:
            self.append_bonus(attack, "size-bonus", attack.modifiers.situational_modifiers.size_difference * 5)

    def calculate_critical_modifiers(self, attack: Attack) -> None:
        if attack.calculated.roll_total > 175:
            diff = attack.calculated.roll_total - 175
            absolute_hit_bonus = math.ceil(diff / 5)
            attack.calculated.critical_modifiers.append(AttackBonusEntry("absolute-hit", absolute_hit_bonus))

        attack.calculated.critical_total = sum(
            p.value for p in attack.calculated.critical_modifiers
        )

    def calculate_critical_severity_modifiers(self, attack: Attack) -> None:
        if attack.modifiers.situational_modifiers.size_difference != 0:
            attack.calculated.critical_severity_modifiers.append(AttackBonusEntry("size-difference", attack.modifiers.situational_modifiers.size_difference))
        attack.calculated.critical_severity_total = sum(
            p.value for p in attack.calculated.critical_severity_modifiers
        )

    def calculate_fumble_result(self, attack: Attack) -> None:
        attack.fumble = AttackFumbleResult(
            status=AttackStatus.PENDING_FUMBLE_ROLL,
        )

    def create_critical_results(self, attack: Attack) -> None:
        if not attack.results.attack_table_entry or not attack.results.attack_table_entry.critical_type:
            return
        critical_severity_map: dict[str, list[str]] = {
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
        if attack.results.attack_table_entry.critical_severity not in critical_severity_map:
            raise ValueError(
                f"Invalid critical severity: {attack.results.attack_table_entry.critical_severity}"
            )
        severity_list = critical_severity_map.get(attack.results.attack_table_entry.critical_severity, [])
        attack.results.criticals = [
            AttackCriticalResult(
                critical_type=attack.results.attack_table_entry.critical_type,
                critical_severity=severity,
                status=CriticalStatus.PENDING_CRITICAL_ROLL,
            ) for severity in severity_list
        ]
        # TODO check additional critical features
        for idx, critical in enumerate(attack.results.criticals):
            critical.key = f"{critical.critical_type}_{critical.critical_severity}_{idx+1}".lower()

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
