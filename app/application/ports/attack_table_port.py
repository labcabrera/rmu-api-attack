from abc import ABC, abstractmethod

from app.domain.entities import AttackTableEntry, CriticalTableEntry, FumbleTableEntry


class AttackTableClient(ABC):

    @abstractmethod
    async def get_attack_table_entry(
        self, attack_table: str, size: str, roll: int, at: int
    ) -> AttackTableEntry:
        pass

    @abstractmethod
    async def get_critical_table_entry(
        self, critical_type: str, critical_severity: str, roll: int
    ) -> CriticalTableEntry:
        pass

    @abstractmethod
    async def get_fumble_table_entry(
        self, fumble_type: str, fumble_severity: str, roll: int
    ) -> FumbleTableEntry:
        pass
