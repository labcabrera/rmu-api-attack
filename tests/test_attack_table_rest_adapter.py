"""
Tests for Attack Table REST Adapter.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.infrastructure.adapters.external.attack_table_rest_adapter import (
    AttackTableRestAdapter,
    AttackTableRestAdapterWithRetry,
)
from app.domain.entities.attack_table import AttackTableEntry


class TestAttackTableRestAdapter:
    """Test cases for AttackTableRestAdapter"""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance for testing"""
        return AttackTableRestAdapter(
            base_url="http://test-api.com", timeout=10.0, api_key="test-key"
        )

    @pytest.mark.asyncio
    async def test_get_attack_table_entry_success(self, adapter):
        """Test successful API call"""
        # Mock response data
        mock_response_data = {"roll": 95, "at": 10, "damage": 15, "critical": "A"}

        # Mock httpx client
        with patch.object(adapter, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = (
                mock_response_data  # This should be synchronous
            )
            mock_response.raise_for_status.return_value = (
                None  # This should be synchronous too
            )
            mock_client.get.return_value = mock_response

            # Execute
            result = await adapter.get_attack_table_entry(roll=95, at=10)

            # Verify
            assert result is not None
            assert isinstance(result, AttackTableEntry)
            assert result.roll == 95
            assert result.at == 10
            assert result.damage == 15
            assert result.critical == "A"

            # Verify API call
            mock_client.get.assert_called_once_with(
                "http://test-api.com/attack-tables/10/entries", params={"roll": 95}
            )

    @pytest.mark.asyncio
    async def test_get_attack_table_entry_not_found(self, adapter):
        """Test API returns 404"""
        with patch.object(adapter, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_client.get.return_value = mock_response

            # Execute
            result = await adapter.get_attack_table_entry(roll=50, at=5)

            # Verify
            assert result is None

    @pytest.mark.asyncio
    async def test_get_attack_table_entry_http_error(self, adapter):
        """Test HTTP error handling"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.get.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 Internal Server Error", request=AsyncMock(), response=mock_response
            )

            # Execute and verify exception
            with pytest.raises(Exception) as exc_info:
                await adapter.get_attack_table_entry(roll=75, at=8)

            assert "Attack table API error: 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_attack_table_entry_network_error(self, adapter):
        """Test network error handling"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_client.get.side_effect = httpx.RequestError("Connection failed")

            # Execute and verify exception
            with pytest.raises(Exception) as exc_info:
                await adapter.get_attack_table_entry(roll=60, at=12)

            assert "Network error accessing attack table API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_close_client(self, adapter):
        """Test client cleanup"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Initialize client
            await adapter._get_client()

            # Close
            await adapter.close()

            # Verify
            mock_client.aclose.assert_called_once()
            assert adapter._client is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager usage"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            async with AttackTableRestAdapter("http://test.com") as adapter:
                assert adapter is not None

            # Verify close was called
            mock_client.aclose.assert_called_once()


class TestAttackTableRestAdapterWithRetry:
    """Test cases for AttackTableRestAdapterWithRetry"""

    @pytest.fixture
    def retry_adapter(self):
        """Create retry adapter instance for testing"""
        return AttackTableRestAdapterWithRetry(
            base_url="http://test-api.com",
            timeout=5.0,
            max_retries=2,
            retry_delay=0.1,  # Short delay for testing
        )

    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self, retry_adapter):
        """Test retry mechanism with eventual success"""
        mock_response_data = {"roll": 80, "at": 15, "damage": 12, "critical": None}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # First call fails, second succeeds
            first_response = AsyncMock()
            first_response.status_code = 500
            first_response.text = "Server Error"
            first_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 Server Error", request=AsyncMock(), response=first_response
            )

            second_response = AsyncMock()
            second_response.status_code = 200
            second_response.json.return_value = mock_response_data

            mock_client.get.side_effect = [first_response, second_response]

            # Execute
            result = await retry_adapter.get_attack_table_entry(roll=80, at=15)

            # Verify success after retry
            assert result is not None
            assert result.roll == 80
            assert result.at == 15
            assert result.damage == 12
            assert result.critical is None

            # Verify two calls were made
            assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhausted(self, retry_adapter):
        """Test all retries exhausted"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # All calls fail
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Persistent Error"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 Server Error", request=AsyncMock(), response=mock_response
            )
            mock_client.get.return_value = mock_response

            # Execute and verify exception
            with pytest.raises(Exception) as exc_info:
                await retry_adapter.get_attack_table_entry(roll=70, at=20)

            assert "Attack table API error: 500" in str(exc_info.value)

            # Verify retry attempts (original + 2 retries = 3 total)
            assert mock_client.get.call_count == 3
