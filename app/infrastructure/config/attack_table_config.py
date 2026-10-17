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
    # enable_retry: bool = True
    enable_retry: bool = False

    @classmethod
    def from_env(cls) -> "AttackTableApiConfig":
        """Create configuration from environment variables"""
        import os

        # RMU_API_ATTACK_TABLES_URL is the legacy name, still accepted for compatibility.
        base_url = (
            os.getenv("RMU_API_ATTACK_TABLES_URI")
            or os.getenv("RMU_API_ATTACK_TABLES_URL")
            or "http://localhost:3005/v1"
        )
        return cls(
            base_url=base_url,
            timeout=float(os.getenv("RMU_API_ATTACK_TABLES_TIMEOUT", "30.0")),
            api_key=os.getenv("RMU_API_ATTACK_TABLES_KEY"),
            max_retries=int(os.getenv("RMU_API_ATTACK_TABLES_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("RMU_API_ATTACK_TABLES_RETRY_DELAY", "1.0")),
            enable_retry=os.getenv(
                "RMU_API_ATTACK_TABLES_ENABLE_RETRY", "false"
            ).lower()
            == "true",
        )
