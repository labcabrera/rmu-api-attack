"""
Domain ports for the Attack system.
These are interfaces that define contracts for external dependencies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

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
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
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
    async def find_by_rsql(
        self,
        rsql_query: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
        """Find attacks using RSQL query"""
        pass

    @abstractmethod
    async def count_by_rsql(
        self,
        rsql_query: Optional[str] = None,
    ) -> int:
        """Count attacks using RSQL query"""
        pass

    @abstractmethod
    async def find_with_filters(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
        """Find attacks with individual filters (deprecated, use find_by_rsql instead)"""
        pass

    @abstractmethod
    async def count_with_filters(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count attacks with individual filters (deprecated, use count_by_rsql instead)"""
        pass

    @abstractmethod
    async def exists(self, attack_id: str) -> bool:
        """Check if an attack exists"""
        pass
