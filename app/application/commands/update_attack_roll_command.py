from dataclasses import dataclass


@dataclass
class UpdateAttackRollCommand:
    """Command object for updating an attack roll"""

    attack_id: str
    roll: int

    def validate(self) -> None:
        """Validate command data"""
        if not self.attack_id:
            raise ValueError("Attack ID is required")
        if not isinstance(self.roll, int):
            raise ValueError("Roll must be an integer")
