"""
Application layer commands for Attack operations.
"""

from dataclasses import dataclass
from app.domain.entities.attack import AttackModifiers


@dataclass
class CreateAttackCommand:
    """Command object for creating an attack"""

    action_id: str
    source_id: str
    target_id: str
    modifiers: AttackModifiers

    def validate(self) -> None:
        """Validate command data"""
        if not self.action_id:
            raise ValueError("Action ID is required")
        if not self.source_id:
            raise ValueError("Source ID is required")
        if not self.target_id:
            raise ValueError("Target ID is required")
        if not self.modifiers:
            raise ValueError("Modifiers are required")
