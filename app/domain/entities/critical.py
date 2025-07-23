"""
Critical domain entities for the RMU Attack system.
"""

from dataclasses import dataclass


@dataclass
class Critical:
    """Critical hit domain entity"""
    id: str
    type: str
    roll: int
    result: str
    status: str
    
    def is_applied(self) -> bool:
        """Check if critical is applied"""
        return self.status == "applied"
    
    def is_pending(self) -> bool:
        """Check if critical is pending"""
        return self.status == "pending"
    
    def apply(self) -> None:
        """Mark critical as applied"""
        self.status = "applied"
    
    def cancel(self) -> None:
        """Mark critical as cancelled"""
        self.status = "cancelled"
    
    def is_cancelled(self) -> bool:
        """Check if critical is cancelled"""
        return self.status == "cancelled"
