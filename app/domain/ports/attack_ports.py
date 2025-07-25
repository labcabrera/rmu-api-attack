"""
Domain ports for the Attack system.
These are interfaces that define contracts for external dependencies.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities import Attack


class AttackRepository(ABC):
    """Port for attack persistence operations"""

    @abstractmethod
    async def find_by_id(self, attack_id: str) -> Optional[Attack]:
        """Find an attack by its ID"""
        pass

    @abstractmethod
    async def save(self, attack: Attack) -> Attack:
        """Save an attack"""
        pass

    @abstractmethod
    async def update(self, attack: Attack) -> Optional[Attack]:
        """Update an existing attack"""
        pass

    @abstractmethod
    async def delete(self, attack_id: str) -> bool:
        """Delete an attack by its ID"""
        pass

    @abstractmethod
    async def find_all(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
        """Find attacks with optional filters"""
        pass

    @abstractmethod
    async def count_all(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count attacks with optional filters"""
        pass

    @abstractmethod
    async def exists(self, attack_id: str) -> bool:
        """Check if an attack exists"""
        pass


class AttackNotificationPort(ABC):
    """Port for attack notifications"""

    @abstractmethod
    async def notify_attack_created(self, attack: Attack) -> None:
        """Notify that an attack was created"""
        pass

    @abstractmethod
    async def notify_attack_executed(self, attack: Attack) -> None:
        """Notify that an attack was executed"""
        pass

    @abstractmethod
    async def notify_attack_updated(self, attack: Attack) -> None:
        """Notify that an attack was updated"""
        pass


class AttackValidationPort(ABC):
    """Port for attack validation"""

    @abstractmethod
    async def validate_attack_creation(self, attack: Attack) -> bool:
        """Validate if an attack can be created"""
        pass

    @abstractmethod
    async def validate_attack_execution(self, attack: Attack) -> bool:
        """Validate if an attack can be executed"""
        pass
