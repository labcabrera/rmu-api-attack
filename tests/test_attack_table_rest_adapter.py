from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from app.domain.entities import AttackTableEntry
from app.infrastructure.api_client.attack_table_rest_adapter import (
    AttackTableRestAdapter,
    AttackTableRestAdapterWithRetry,
)


class TestAttackTableRestAdapter:
    @pytest.fixture
    def adapter(self):
        return AttackTableRestAdapter(
            base_url="http://test-api.com",
            timeout=10.0,
            api_key="test-key",
        )

    @pytest.mark.asyncio
    async def test_get_attack_table_entry_success(self, adapter):
        response = Mock()
        response.json.return_value = {
            "text": "15AS",
            "damage": 15,
            "criticalType": "S",
            "criticalSeverity": "A",
        }
        response.raise_for_status.return_value = None

        client = AsyncMock()
        client.get.return_value = response

        with patch.object(adapter, "_get_client", return_value=client):
            result = await adapter.get_attack_table_entry(
                attack_table="arming-sword",
                size=2,
                roll=95,
                at=10,
            )

        assert isinstance(result, AttackTableEntry)
        assert result.text == "15AS"
        assert result.damage == 15
        assert result.critical_type == "S"
        assert result.critical_severity == "A"
        assert result.damage_base == 15
        assert result.critical_severity_base == "A"
        client.get.assert_called_once_with(
            "http://test-api.com/attack-tables/arming-sword/medium/10/95"
        )

    @pytest.mark.asyncio
    async def test_get_attack_table_entry_clamps_roll(self, adapter):
        response = Mock()
        response.json.return_value = {"text": "", "damage": 0}
        response.raise_for_status.return_value = None

        client = AsyncMock()
        client.get.return_value = response

        with patch.object(adapter, "_get_client", return_value=client):
            await adapter.get_attack_table_entry(
                attack_table="arming-sword",
                size=2,
                roll=250,
                at=10,
            )

        client.get.assert_called_once_with(
            "http://test-api.com/attack-tables/arming-sword/medium/10/175"
        )

    @pytest.mark.asyncio
    async def test_close_client(self, adapter):
        client = AsyncMock()
        adapter._client = client

        await adapter.close()

        client.aclose.assert_called_once()
        assert adapter._client is None


class TestAttackTableRestAdapterWithRetry:
    @pytest.fixture
    def retry_adapter(self):
        return AttackTableRestAdapterWithRetry(
            base_url="http://test-api.com",
            timeout=5.0,
            max_retries=1,
            retry_delay=0,
        )

    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self, retry_adapter):
        success_response = Mock()
        success_response.json.return_value = {"text": "12", "damage": 12}
        success_response.raise_for_status.return_value = None

        failure_response = Mock()
        failure_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "temporary failure",
            request=Mock(),
            response=failure_response,
        )

        client = AsyncMock()
        client.get.side_effect = [failure_response, success_response]

        with patch.object(retry_adapter, "_get_client", return_value=client):
            result = await retry_adapter.get_attack_table_entry(
                attack_table="arming-sword",
                size=2,
                roll=80,
                at=15,
            )

        assert result.damage == 12
        assert client.get.call_count == 2
