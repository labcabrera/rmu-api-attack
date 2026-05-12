from abc import ABC, abstractmethod

from app.domain.entities import Attack


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
