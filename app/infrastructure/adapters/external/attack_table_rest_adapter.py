"""
REST adapter for Attack Table Service.
This adapter implements the AttackTableService port by making HTTP calls to an external API.
"""

import asyncio
from logging import critical
from typing import Optional
import httpx

from app.domain.entities import (
    AttackTableEntry,
    CriticalTableEntry,
    CriticalEffect,
    FumbleTableEntry,
)
from app.domain.ports.attack_table_port import AttackTableClient
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class AttackTableRestAdapter(AttackTableClient):
    """REST adapter for Attack Table Service"""

    def __init__(
        self, base_url: str, timeout: float = 30.0, api_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout), headers=headers
            )
        return self._client

    async def get_attack_table_entry(
        self, attack_table: str, size: str, roll: int, at: int
    ) -> AttackTableEntry:

        logger.info(f"Fetching attack table entry for roll={roll}, at={at}")
        try:
            client = await self._get_client()
            adjusted_roll = min(175, max(roll, 1))
            url = f"{self.base_url}/attack-tables/{attack_table}/{size}/{at}/{adjusted_roll}"
            logger.debug(f"Making request to {url}")
            response = await client.get(url)
            response.raise_for_status()
            logger.debug(f"Received response: {response}")
            json = response.json()
            entry = AttackTableEntry(
                text=json.get("text", ""),
                damage=json.get("damage", 0),
                critical_type=json.get("criticalType", None),
                critical_severity=json.get("criticalSeverity", None),
            )
            logger.info(f"Successfully retrieved attack table entry: {entry}")
            return entry
        except Exception as e:
            logger.error(f"Unexpected error calling attack table API: {str(e)}")
            raise Exception(f"Unexpected error accessing attack table API: {str(e)}")

    async def get_critical_table_entry(
        self, critical_type: str, critical_severity: str, roll: int
    ) -> CriticalTableEntry:
        """
        Get attack table entry by critical type, critical severity, roll and AT.
        """

        logger.info(
            f"Fetching critical {critical_type}-{critical_severity} for roll={roll}"
        )
        try:
            client = await self._get_client()
            url = f"{self.base_url}/critical-tables/{critical_type}/{critical_severity}/{roll}"
            logger.debug(f"Making request to {url}")
            response = await client.get(url)
            response.raise_for_status()
            logger.debug(f"Received response: {response}")
            json = response.json()

            effects = None
            if json.get("effects"):
                effects = []
                for effect in json["effects"]:
                    effects.append(
                        CriticalEffect(
                            status=effect.get("status"),
                            rounds=effect.get("rounds", None),
                            value=effect.get("value", None),
                            delay=effect.get("delay", None),
                            condition=effect.get("condition", None),
                        )
                    )

            return CriticalTableEntry(
                text=json.get("message", ""),
                damage=json.get("dmg", 0),
                location=json.get("location", ""),
                effects=effects,
            )
        except Exception as e:
            logger.error(f"Unexpected error calling attack table API: {str(e)}")
            raise Exception(f"Unexpected error accessing attack table API: {str(e)}")

    async def get_fumble_table_entry(
        self, fumble_table: str, roll: int
    ) -> FumbleTableEntry:
        """
        Get fumble table entry by fumble type, fumble severity, roll.
        """

        logger.info(f"Fetching fumble {fumble_table} for roll={roll}")
        try:
            client = await self._get_client()
            url = f"{self.base_url}/fumble-tables/{fumble_table}/{roll}"
            logger.debug(f"Making request to {url}")
            response = await client.get(url)
            response.raise_for_status()
            logger.debug(f"Received response: {response}")
            json = response.json()
            effects = None
            if json.get("effects"):
                effects = []
                for effect in json["effects"]:
                    effects.append(
                        CriticalEffect(
                            status=effect.get("status"),
                            rounds=effect.get("rounds", None),
                            value=effect.get("value", None),
                            delay=effect.get("delay", None),
                            condition=effect.get("condition", None),
                        )
                    )
            return FumbleTableEntry(
                text=json.get("message", ""),
                status=json.get("status", None),
                additional_damage_text=json.get("additionalDamageText", None),
                effects=effects,
            )
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
        super().__init__(base_url, timeout, api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def get_attack_table_entry(
        self, attack_table: str, size: str, roll: int, at: int
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

                return await super().get_attack_table_entry(
                    attack_table=attack_table, size=size, roll=roll, at=at
                )

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
