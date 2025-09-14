from dataclasses import dataclass
from typing import Optional

from .attack_fumble_result import AttackFumbleResult
from .attack_table_entry import AttackTableEntry
from .critical import AttackCriticalResult


@dataclass
class AttackResult:
    """Attack result data"""

    attack_table_entry: Optional[AttackTableEntry] = None
    criticals: list[AttackCriticalResult] = None
    fumble: Optional[AttackFumbleResult] = None

    def get_critical_by_key(self, key: str) -> Optional[AttackCriticalResult]:
        """Get critical result by key"""
        if self.criticals:
            for critical in self.criticals:
                if critical.key == key:
                    return critical
        return None
