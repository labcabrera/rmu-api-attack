from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.attack_table import AttackTableEntry


class AttackTableClient(ABC):

    @abstractmethod
    async def get_attack_table_entry(
        self, attack_table: str, size: str, roll: int, at: int
    ) -> Optional[AttackTableEntry]:
        pass
