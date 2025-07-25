from dataclasses import dataclass
from app.domain.entities.attack import AttackModifiers


@dataclass
class UpdateAttackModifiersCommand:

    attack_id: str
    modifiers: AttackModifiers

    def validate(self) -> None:
        """Validate command data"""
        if not self.attack_id:
            raise ValueError("Attack ID is required")
        if not self.modifiers:
            raise ValueError("Modifiers are required")
        if not self.modifiers.attack_type:
            raise ValueError("Attack type is required")
        if not self.modifiers.attack_table:
            raise ValueError("Attack table is required")
        if not self.modifiers.attack_size:
            raise ValueError("Attack size is required")
        if (
            not isinstance(self.modifiers.at, int)
            or self.modifiers.at < 1
            or self.modifiers.at > 10
        ):
            raise ValueError("AT must be a non-negative integer between 1 and 10")
