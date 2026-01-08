from dataclasses import dataclass

from .attack_armor import AttackArmor
from .attack_skill import AttackSkill
from .attack_roll_modifiers import AttackRollModifiers
from .attack_situational_modifiers import AttackSituationalModifiers
from .attack_feature import AttackFeature
from .enums import AttackType


@dataclass
class AttackModifiers:
    """Attack modifiers data"""

    attack_type: AttackType = None
    attack_table: str = None
    attack_size: int = 2
    fumble_table: str = None
    armor: AttackArmor = None
    action_points: int = 4
    fumble: int = 1
    called_shot: str = None
    roll_modifiers: AttackRollModifiers = None
    situational_modifiers: AttackSituationalModifiers = None
    features: list[AttackFeature] = None
    source_skills: list[AttackSkill] = None

    def __post_init__(self):
        """Validate input data after initialization"""
        # Convert string values to enum if necessary
        if isinstance(self.attack_type, str):
            self.attack_type = AttackType(self.attack_type)
        elif not isinstance(self.attack_type, AttackType):
            raise ValueError("Invalid attack type")
        if not isinstance(self.roll_modifiers, AttackRollModifiers):
            raise ValueError("Invalid roll modifiers")
        if not isinstance(self.attack_table, str):
            raise ValueError("attack_table must be a string")
        if not isinstance(self.attack_size, int):
            raise ValueError("attack_size must be an integer")
        if not isinstance(self.armor, AttackArmor):
            raise ValueError("armor must be an instance of AttackArmor")
        # TODO check armor
