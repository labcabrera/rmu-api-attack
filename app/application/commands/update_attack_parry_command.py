from dataclasses import dataclass


@dataclass
class UpdateAttackParryCommand:
    """Command object for updating an attack parry"""

    attack_id: str
    parry: int

    def validate(self) -> None:
        """Validate command data"""
        if not self.attack_id:
            raise ValueError("Attack ID is required")
        if not isinstance(self.parry, int):
            raise ValueError("Parry must be a integer")
        if self.parry < 0:
            raise ValueError("Parry must be a non-negative integer")
