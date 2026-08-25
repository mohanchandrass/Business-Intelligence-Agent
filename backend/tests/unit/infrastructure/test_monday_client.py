import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.infrastructure.monday.client import MondayClient, MondayClientError
from app.config.settings import Settings

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("MONDAY_API_TOKEN", "fake_token")
    monkeypatch.setenv("MONDAY_DEALS_BOARD_ID", "123")
    monkeypatch.setenv("MONDAY_WORK_ORDERS_BOARD_ID", "456")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    return Settings()

@pytest.mark.asyncio
async def test_monday_client_graphql_error(mock_settings):
    """Test that GraphQL errors correctly raise MondayClientError."""
    client = MondayClient()
    mock_response = AsyncMock()
    from unittest.mock import MagicMock
    mock_response.json = MagicMock(return_value={"errors": [{"message": "Invalid query"}]})
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with pytest.raises(MondayClientError, match="GraphQL Errors: Invalid query"):
            await client.execute("{ test }")
