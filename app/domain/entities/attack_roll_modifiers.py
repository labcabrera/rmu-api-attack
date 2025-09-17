from dataclasses import dataclass


@dataclass
class AttackRollModifiers:
    """Modifiers for attack roll calculated by tactical domain model"""

    bo: int = 0
    injury_penalty: int = 0
    pace_penalty: int = 0
    fatigue_penalty: int = 0
    called_shot_penalty: int = 0
    bd: int = 0
    shield: int = 0
    range_penalty: int = 0
    parry: int = 0
    attack_number: int = 1
    attack_targets: int = 1
    game_lethality: int = 0
    custom_bonus: int = 0
