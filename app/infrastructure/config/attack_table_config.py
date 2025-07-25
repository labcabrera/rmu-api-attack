"""
Configuration for Attack Table REST adapter.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AttackTableApiConfig:
    """Configuration for Attack Table API"""

    base_url: str
    timeout: float = 30.0
    api_key: Optional[str] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_retry: bool = True

    @classmethod
    def from_env(cls) -> "AttackTableApiConfig":
        """Create configuration from environment variables"""
        import os

        return cls(
            base_url=os.getenv("RMU_API_ATTACK_TABLES_URL", "http://localhost:3005/v1"),
            timeout=float(os.getenv("RMU_API_ATTACK_TABLES_TIMEOUT", "30.0")),
            api_key=os.getenv("RMU_API_ATTACK_TABLES_KEY"),
            max_retries=int(os.getenv("RMU_API_ATTACK_TABLES_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("RMU_API_ATTACK_TABLES_RETRY_DELAY", "1.0")),
            enable_retry=os.getenv("RMU_API_ATTACK_TABLES_ENABLE_RETRY", "true").lower()
            == "true",
        )
