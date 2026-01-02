"""
Domain entities for the RMU Attack system.
"""

from typing import Optional, Dict, Tuple
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

# Map type: for each Cover value store a pair (melee_bonus, ranged_bonus)
MapCoverToInts = Dict[Cover, Tuple[int, int]]

# bonuses: (melee, ranged)
COVER_BONUSES: MapCoverToInts = {
    Cover.SOFT_PARTIAL: (-10, -20),
    Cover.SOFT_HALF: (-20, -40),
    Cover.SOFT_FULL: (-50, -100),
    Cover.HARD_PARTIAL: (-20, -40),
    Cover.HARD_HALF: (-40, -80),
    Cover.HARD_FULL: (-100, -200),
}

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
            self._append_bonus("roll", self.roll.roll)

        self._append_bonus("bo", roll_modifiers.bo)
        self._append_bonus("injury-penalty", roll_modifiers.injury_penalty)
        self._append_bonus("fatigue-penalty", roll_modifiers.fatigue_penalty)
        self._append_pace_penalty()
        self._append_bonus("range-penalty", roll_modifiers.range_penalty)
        self._append_action_points()
        self._append_bonus_bd()
        self._append_bonus_bd_shield()
        self._append_parry()
        self._append_restricted_quarters()
        self._append_source_statuses()
        self._append_target_statuses()
        self._append_source_weapon_type()
        self._append_positional_source()
        self._append_positional_target()
        self._append_cover()
        self._append_range_in_melee_bonus()
        self._append_size_bonus()
        self._append_called_shot_bonus()
        self._append_attack_number_bonus()
        self._append_attack_target_bonus()
        self._append_higher_ground_bonus()
        self._append_game_lethality()
        self._append_bonus("custom-bonus", roll_modifiers.custom_bonus)

    def _append_bonus(self, key: str, value: int) -> None:
        if not self.calculated:
            self.calculated = AttackCalculations()
        self.calculated.roll_modifiers.append(AttackBonusEntry(key=key, value=value))

    def _append_bonus_with_skill(
        self, key: str, value: int, skill_id: str
    ) -> None:
        if not value or value == 0:
            return
        skill_bonus = self._get_skill_bonus(skill_id)
        skill_bonus_adjusted = min(abs(value), skill_bonus)
        self._append_bonus(key, value)
        self._append_bonus(f"{key}-skill-{skill_id}", skill_bonus_adjusted)

    def _get_skill_bonus(self, skill_id: str) -> int:
        for skill in self.modifiers.source_skills:
            if skill.skill_id == skill_id:
                return skill.bonus
        return 0

    def _append_bonus_bd(self) -> None:
        if not self.modifiers.situational_modifiers.disabled_db:
            self._append_bonus("bd", -self.modifiers.roll_modifiers.bd)

    def _append_action_points(self) -> None:
        if(self.is_melee()):
            self._append_bonus("action-points", (4 - self.modifiers.action_points) *-25)
            return
        else:
            self._append_bonus("action-points", (3 - self.modifiers.action_points) *-25)
            return
        

    def _append_bonus_bd_shield(self) -> None:
        if not self.modifiers.situational_modifiers.disabled_shield:
            self._append_bonus("shield", -self.modifiers.roll_modifiers.shield)

    def _append_parry(self) -> None:
        if not self.modifiers.situational_modifiers.disabled_parry:
            self._append_bonus("parry", -self.modifiers.roll_modifiers.parry)

    def _append_cover(self) -> None:
        bonus = 0
        is_melee = self.is_melee()
        cover = self.modifiers.situational_modifiers.cover
        if cover in COVER_BONUSES:
            melee_val, ranged_val = COVER_BONUSES[cover]
            bonus = melee_val if is_melee else ranged_val
        self._append_bonus("cover", bonus)

    def _append_positional_source(self) -> None:
        if self.modifiers.situational_modifiers.positional_source and self.is_melee():
            bonus = 0
            match self.modifiers.situational_modifiers.positional_source:
                case PositionalSource.TO_FLANK:
                    bonus = -30
                case PositionalSource.TO_REAR:
                    bonus = -70
            self._append_bonus_with_skill("positional-source", bonus, "reverse-strike")

    def _append_positional_target(self) -> None:
        if self.modifiers.situational_modifiers.positional_target and self.is_melee():
            bonus = 0
            match self.modifiers.situational_modifiers.positional_target:
                case PositionalTarget.FLANK:
                    bonus = 15
                case PositionalTarget.REAR:
                    bonus = 35
            self._append_bonus("positional-target", bonus)

    def _append_pace_penalty(self) -> None:
        if self.is_melee():
            bonus = self.modifiers.roll_modifiers.pace_penalty
            self._append_bonus_with_skill("pace-penalty",bonus,"footwork")
        else:
            self._append_bonus("pace-penalty", self.modifiers.roll_modifiers.pace_penalty)

    def _append_source_weapon_type(self) -> None:
        if self.modifiers.situational_modifiers.off_hand:
            # TODO check ambidextrous talent
            self._append_bonus("off-hand-weapon", -20)
            if self.source_has_status("ambidextrous"):
                self._append_bonus("ambidextrous", 20)
        if (
            self.modifiers.situational_modifiers.two_handed_weapon
            and self.is_melee()
        ):
            self._append_bonus("two-handed-weapon", 10)

    def _append_range_in_melee_bonus(self) -> None:
        if not self.is_melee() and self.source_has_status("melee"):
            self._append_bonus("range-in-melee", -20)

    def _append_source_statuses(self) -> None:
        if self.source_has_status("prone"):
            self._append_bonus("prone-source", -50)

    def _append_target_statuses(self) -> None:
        if self.target_has_status("stunned"):
            self._append_bonus("stunned-target", 20)
        if self.target_has_status("surprised"):
            self._append_bonus("surprised-target", 25)
        if self.target_has_status("prone"):
            if self.is_melee():
                self._append_bonus("prone-target", 30)
            else:
                self._append_bonus("prone-target", -30)

    def _append_restricted_quarters(self) -> None:
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
            self._append_bonus_with_skill("restricted-quarters", bonus, "restricted-quarters")

    def _append_size_bonus(self) -> None:
        sizeDif = self.modifiers.situational_modifiers.size_difference
        if (sizeDif and sizeDif < 0):
            self._append_bonus("size-bonus", sizeDif * 5)

    def _append_called_shot_bonus(self) -> None:
        if self.modifiers.called_shot and not self.modifiers.called_shot == 'none':
            basePenalty = self.modifiers.roll_modifiers.called_shot_penalty or -25
            self._append_bonus_with_skill("called-shot", basePenalty, "called-shot")

    def _append_attack_number_bonus(self) -> None:
        if self.modifiers.roll_modifiers.attack_number and self.modifiers.roll_modifiers.attack_number > 1:
            bonus = -75 + (self.modifiers.roll_modifiers.attack_number - 2) * -25
            self._append_bonus_with_skill("attack-number", bonus, "multiple-attacks")

    def _append_attack_target_bonus(self) -> None:
        if self.modifiers.roll_modifiers.attack_targets and self.modifiers.roll_modifiers.attack_targets > 1:
            bonus = -20 * (self.modifiers.roll_modifiers.attack_targets - 1)
            self._append_bonus_with_skill("attack-targets", bonus, "multiple-attacks")

    def _append_game_lethality(self) -> None:
        if self.modifiers.roll_modifiers.game_lethality and self.modifiers.roll_modifiers.game_lethality > 0:
            bonus = self.modifiers.roll_modifiers.game_lethality
            self._append_bonus("game-lethality", bonus)

    def _append_higher_ground_bonus(self) -> None:
        if self.modifiers.situational_modifiers.higher_ground:
            self._append_bonus_with_skill("higher-ground", 10, "higher-ground") 

    def source_has_status(self, status: str) -> bool:
        return status in self.modifiers.situational_modifiers.source_status

    def target_has_status(self, status: str) -> bool:
        return status in self.modifiers.situational_modifiers.target_status

    def set_roll(self, roll: int, location: Optional[str]) -> None:
        if not roll:
            raise ValueError("Roll value must be provided")
        if self.is_called_shot() and location:
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
    
    def is_called_shot(self) -> bool:
        if(not self.modifiers.called_shot):
            return False
        return self.modifiers.called_shot != 'none'
