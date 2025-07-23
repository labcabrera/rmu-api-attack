"""
Critical domain ports (interfaces).
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.critical import Critical


class CriticalRepository(ABC):
    """Repository port for Critical operations"""
    
    @abstractmethod
    async def save(self, critical: Critical) -> Critical:
        """Save a critical"""
        pass
    
    @abstractmethod
    async def find_by_id(self, critical_id: str) -> Optional[Critical]:
        """Find a critical by its ID"""
        pass
    
    @abstractmethod
    async def update(self, critical: Critical) -> Optional[Critical]:
        """Update an existing critical"""
        pass
    
    @abstractmethod
    async def delete(self, critical_id: str) -> bool:
        """Delete a critical by its ID"""
        pass
    
    @abstractmethod
    async def find_all(self, status: Optional[str] = None,
                      type: Optional[str] = None,
                      limit: int = 100, 
                      skip: int = 0) -> List[Critical]:
        """Find criticals with optional filters"""
        pass
    
    @abstractmethod
    async def exists(self, critical_id: str) -> bool:
        """Check if a critical exists"""
        pass


class CriticalNotificationPort(ABC):
    """Port for critical notifications"""
    
    @abstractmethod
    async def notify_critical_created(self, critical: Critical) -> None:
        """Notify that a critical was created"""
        pass
    
    @abstractmethod
    async def notify_critical_applied(self, critical: Critical) -> None:
        """Notify that a critical was applied"""
        pass
    
    @abstractmethod
    async def notify_critical_updated(self, critical: Critical) -> None:
        """Notify that a critical was updated"""
        pass
