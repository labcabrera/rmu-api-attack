from dataclasses import dataclass


@dataclass
class UpdateCriticalRollCommand:
    """Command object for updating an critical roll"""

    attack_id: str
    critical_key: str
    roll: int

    def validate(self) -> None:
        """Validate command data"""
        if not self.attack_id:
            raise ValueError("Attack ID is required")
        if not self.critical_key:
            raise ValueError("Critical key is required")
        if not isinstance(self.roll, int):
            raise ValueError("Roll must be an integer")
