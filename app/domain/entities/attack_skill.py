from dataclasses import dataclass


@dataclass
class AttackSkill:
    """Attack skill data"""

    skill_id: str = None
    bonus: int = 0
