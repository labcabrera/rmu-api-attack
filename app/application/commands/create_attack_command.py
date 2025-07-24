"""
Application layer commands for Attack operations.
"""

from dataclasses import dataclass
from app.domain.entities import AttackMode


@dataclass
class CreateAttackCommand:
    """Command object for creating an attack"""

    tactical_game_id: str
    source_id: str
    target_id: str
    action_points: int
    mode: AttackMode

    def validate(self) -> None:
        """Validate command data"""
        if not self.tactical_game_id:
            raise ValueError("Tactical game ID is required")
        if not self.source_id:
            raise ValueError("Source ID is required")
        if not self.target_id:
            raise ValueError("Target ID is required")
        if self.action_points < 1 or self.action_points > 4:
            raise ValueError("Invalid action points, must be between 1 and 4")
