"""
Domain entities for the RMU Attack system.
"""

from typing import Optional
from dataclasses import dataclass

from app.domain.entities import AttackBonusEntry
from .attack_calculations import AttackCalculations
from .attack_result import AttackResult
from .attack_roll import AttackRoll
from .attack_modifiers import AttackModifiers
from .enums import (
    AttackStatus,
    AttackType,
    Cover,
    PositionalSource,
    PositionalTarget,
    RestrictedQuarters,
)


@dataclass
class Attack:
    """Attack domain entity."""

    id: str
    game_id: str
    action_id: str
    source_id: str
    target_id: str
    status: AttackStatus
    modifiers: AttackModifiers
    roll: Optional[AttackRoll] = None
    calculated: Optional[AttackCalculations] = None
    results: Optional[AttackResult] = None

    def append_all_modifiers(self) -> None:
        roll_modifiers = self.modifiers.roll_modifiers
        if self.roll:
            self.append_bonus("roll", self.roll.roll)

        self.append_bonus("bo", roll_modifiers.bo)
        self.append_bonus("injury-penalty", roll_modifiers.injury_penalty)
        self.append_bonus("fatigue-penalty", roll_modifiers.fatigue_penalty)
        self.append_pace_penalty()
        self.append_bonus("range-penalty", roll_modifiers.range_penalty)
        self.append_bonus_bd()
        self.append_bonus_bd_shield()
        self.append_parry()
        self.append_restricted_quarters()
        self.append_source_statuses()
        self.append_target_statuses()
        self.append_source_weapon_type()
        self.append_positional_source()
        self.append_positional_target()
        self.append_cover()
        self.append_range_in_melee_bonus()
        self.append_size_bonus()
        self.append_called_shot_bonus()
        self.append_bonus("custom-bonus", roll_modifiers.custom_bonus)

    def append_bonus(self, key: str, value: int) -> None:
        if not self.calculated:
            self.calculated = AttackCalculations()
        self.calculated.roll_modifiers.append(AttackBonusEntry(key=key, value=value))

    def append_with_skill(
        self, key: str, value: int, skill_id: str
    ) -> None:
        if not value or value == 0:
            return
        skill_bonus = self.get_skill_bonus(skill_id)
        skill_bonus_adjusted = min(abs(value), skill_bonus)
        self.append_bonus(key, value)
        self.append_bonus(f"{key}-skill-{skill_id}", skill_bonus_adjusted)

    def get_skill_bonus(self, skill_id: str) -> int:
        for skill in self.modifiers.source_skills:
            if skill.skill_id == skill_id:
                return skill.bonus
        return 0

    def append_bonus_bd(self) -> None:
        if not self.modifiers.situational_modifiers.disabled_db:
            self.append_bonus("bd", -self.modifiers.roll_modifiers.bd)

    def append_bonus_bd_shield(self) -> None:
        if not self.modifiers.situational_modifiers.disabled_shield:
            self.append_bonus("shield", -self.modifiers.roll_modifiers.shield)

    def append_parry(self) -> None:
        if not self.modifiers.situational_modifiers.disabled_parry:
            self.append_bonus("parry", -self.modifiers.roll_modifiers.parry)

    def append_cover(self) -> None:
        bonus = 0
        isMelee = self.is_melee()
        match self.modifiers.situational_modifiers.cover:
            case Cover.SOFT_PARTIAL:
                bonus = -10 or not isMelee -20
            case Cover.SOFT_HALF:
                bonus = -20 or not isMelee -40
            case Cover.SOFT_FULL:
                bonus = -50 or not isMelee -100
            case Cover.HARD_PARTIAL:
                bonus = -20 or not isMelee -40
            case Cover.HARD_HALF:
                bonus = -40 or not isMelee -80
            case Cover.HARD_FULL:
                bonus = -100 or not isMelee -200
        self.append_bonus("cover", bonus)

    def append_positional_source(self) -> None:
        if self.modifiers.situational_modifiers.positional_source and self.is_melee():
            bonus = 0
            match self.modifiers.situational_modifiers.positional_source:
                case PositionalSource.TO_FLANK:
                    bonus = -30
                case PositionalSource.TO_REAR:
                    bonus = -70
            self.append_with_skill("positional-source", bonus, "reverse-strike")

    def append_positional_target(self) -> None:
        if self.modifiers.situational_modifiers.positional_target and self.is_melee():
            bonus = 0
            match self.modifiers.situational_modifiers.positional_target:
                case PositionalTarget.FLANK:
                    bonus = 15
                case PositionalTarget.REAR:
                    bonus = 35
            self.append_bonus("positional-target", bonus)

    def append_pace_penalty(self) -> None:
        if self.is_melee():
            self.append_with_skill(
                "pace-penalty",
                self.modifiers.roll_modifiers.pace_penalty,
                "footwork",
            )
        else:
            self.append_bonus("pace-penalty", self.modifiers.roll_modifiers.pace_penalty)

    def append_source_weapon_type(self) -> None:
        if self.modifiers.situational_modifiers.off_hand:
            # TODO check ambidextrous talent
            self.append_bonus("off-hand-weapon", -20)
            if self.source_has_status("ambidextrous"):
                self.append_bonus("ambidextrous", 20)
        if (
            self.modifiers.situational_modifiers.two_handed_weapon
            and self.is_melee()
        ):
            self.append_bonus("two-handed-weapon", 10)

    def append_range_in_melee_bonus(self) -> None:
        if not self.is_melee() and self.source_has_status("melee"):
            self.append_bonus("range-in-melee", -20)

    def append_source_statuses(self) -> None:
        if self.source_has_status("prone"):
            self.append_bonus("prone-source", -50)

    def append_target_statuses(self) -> None:
        if self.target_has_status("stunned"):
            self.append_bonus("stunned-target", 20)
        if self.target_has_status("surprised"):
            self.append_bonus("surprised-target", 25)
        if self.target_has_status("prone"):
            if self.is_melee():
                self.append_bonus("prone-target", 30)
            else:
                self.append_bonus("prone-target", -30)

    def append_restricted_quarters(self) -> None:
        if self.modifiers.situational_modifiers.restricted_quarters:
            bonus = 0;
            match self.modifiers.situational_modifiers.restricted_quarters:
                case RestrictedQuarters.CLOSE:
                    bonus = -25
                case RestrictedQuarters.CRAMPED:
                    bonus = -50
                case RestrictedQuarters.TIGHT:
                    bonus = -75
                case RestrictedQuarters.CONFINED:
                    bonus = -100
            self.append_with_skill("restricted-quarters", bonus, "restricted-quarters")

    def append_size_bonus(self) -> None:
        sizeDif = self.modifiers.situational_modifiers.size_difference
        if (sizeDif and sizeDif < 0):
            self.append_bonus("size-bonus", sizeDif * 5)

    def append_called_shot_bonus(self) -> None:
        if self.modifiers.called_shot and not self.modifiers.called_shot == 'none':
            basePenalty = self.modifiers.roll_modifiers.called_shot_penalty or -25
            self.append_with_skill("called-shot", basePenalty, "called-shot")

    def source_has_status(self, status: str) -> bool:
        return status in self.modifiers.situational_modifiers.source_status

    def target_has_status(self, status: str) -> bool:
        return status in self.modifiers.situational_modifiers.target_status

    def set_roll(self, roll: int, location: Optional[str]) -> None:
        if not roll:
            raise ValueError("Roll value must be provided")
        if self.modifiers.called_shot and location:
            raise ValueError("Location should not be provided for a called shot")
        if not self.modifiers.armor.at and not location:
            raise ValueError("Location must be provided using different AT values")
        effective_location = location or self.modifiers.called_shot
        effective_at = self.modifiers.armor.at
        if not effective_at:
            match effective_location:
                case "body":
                    effective_at = self.modifiers.armor.body_at
                case "head":
                    effective_at = self.modifiers.armor.head_at
                case "arms":
                    effective_at = self.modifiers.armor.arms_at
                case "legs":
                    effective_at = self.modifiers.armor.legs_at
        self.roll = AttackRoll(roll=roll, location=effective_location, at=effective_at)

    def is_melee(self) -> bool:
        return self.modifiers.attack_type == AttackType.MELEE

    def is_fumble(self) -> bool:
        return (
            self.modifiers.fumble > 0
            and self.roll
            and self.roll.roll <= self.modifiers.fumble
        )
