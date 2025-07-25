from dataclasses import dataclass
from app.domain.entities.attack import AttackModifiers


@dataclass
class UpdateAttackModifiersCommand:

    attack_id: str
    modifiers: AttackModifiers
