"""
REST adapter for Attack Table Service.
This adapter implements the AttackTableService port by making HTTP calls to an external API.
"""

import asyncio
from logging import critical
from typing import Optional
import httpx
from app.domain.ports.attack_table_port import AttackTableClient
from app.domain.entities.attack_table import AttackTableEntry
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class AttackTableRestAdapter(AttackTableClient):
    """REST adapter for Attack Table Service"""

    def __init__(
        self, base_url: str, timeout: float = 30.0, api_key: Optional[str] = None
    ):
        """
        Initialize the REST adapter

        Args:
            base_url: Base URL of the attack table API
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout), headers=headers
            )
        return self._client

    async def get_attack_table_entry(
        attack_table: str, size: str, self, roll: int, at: int
    ) -> Optional[AttackTableEntry]:
        """
        Get attack table entry from external API

        Args:
            roll: Attack roll result
            at: Attack table type/identifier

        Returns:
            AttackTableEntry if found, None otherwise

        Raises:
            Exception: If API call fails after retries
        """
        logger.info(f"Fetching attack table entry for roll={roll}, at={at}")

        try:
            client = await self._get_client()

            # Construct API endpoint
            url = f"{self.base_url}/attack-tables/{attack_table}/{size}/{at}/{roll}"

            logger.debug(f"Making request to {url}")

            response = await client.get(url)

            if response.status_code == 404:
                logger.warning(f"Attack table entry not found for roll={roll}, at={at}")
                return None

            response.raise_for_status()

            data = response.json()
            logger.debug(f"Received response: {data}")

            # Parse response and create AttackTableEntry

            # TODO parse
            damage = 0
            criticalType = None
            criticalSeverity = None

            entry = AttackTableEntry(
                roll=data.get("roll", roll),
                at=data.get("at", at),
                literal=data.data,
                damage=damage,
                criticalType=criticalType,
                criticalSeverity=criticalSeverity,
            )

            logger.info(f"Successfully retrieved attack table entry: {entry}")
            return entry

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error calling attack table API: {e.response.status_code} - {e.response.text}"
            )
            raise Exception(f"Attack table API error: {e.response.status_code}")

        except httpx.RequestError as e:
            logger.error(f"Network error calling attack table API: {str(e)}")
            raise Exception(f"Network error accessing attack table API: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error calling attack table API: {str(e)}")
            raise Exception(f"Unexpected error accessing attack table API: {str(e)}")

    async def close(self):
        """Close HTTP client connection"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


class AttackTableRestAdapterWithRetry(AttackTableRestAdapter):
    """REST adapter with retry mechanism"""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the REST adapter with retry

        Args:
            base_url: Base URL of the attack table API
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        super().__init__(base_url, timeout, api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def get_attack_table_entry(
        self, roll: int, at: int
    ) -> Optional[AttackTableEntry]:
        """
        Get attack table entry with retry mechanism
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt} for roll={roll}, at={at}")
                    await asyncio.sleep(self.retry_delay * attempt)

                return await super().get_attack_table_entry(roll, at)

            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying: {str(e)}")
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed for roll={roll}, at={at}"
                    )

        # If all retries failed, raise the last exception
        raise last_exception
