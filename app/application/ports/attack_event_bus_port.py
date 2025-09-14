from abc import ABC, abstractmethod
from app.domain.entities import Attack


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
