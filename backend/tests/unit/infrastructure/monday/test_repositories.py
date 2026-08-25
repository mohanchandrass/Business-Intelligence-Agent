import pytest
from unittest.mock import AsyncMock, patch
from app.infrastructure.monday.repositories import MondayDealRepository
from app.infrastructure.monday.client import MondayClient

@pytest.mark.asyncio
async def test_monday_deal_repository_pagination():
    from unittest.mock import MagicMock
    mock_client = MagicMock(spec=MondayClient)
    mock_client.execute = AsyncMock()
    
    # Mock responses for two pages
    page_1 = {
        "data": {
            "boards": [{
                "items_page": {
                    "cursor": "cursor-123",
                    "items": [
                        {"id": "1", "name": "Deal 1", "column_values": []}
                    ]
                }
            }]
        }
    }
    page_2 = {
        "data": {
            "boards": [{
                "items_page": {
                    "cursor": None,
                    "items": [
                        {"id": "2", "name": "Deal 2", "column_values": []}
                    ]
                }
            }]
        }
    }
    
    mock_client.execute.side_effect = [page_1, page_2]

    from app.infrastructure.monday.discovery_models import BoardDescriptor, SemanticMapping
    descriptor = BoardDescriptor(
        board_id="12345",
        board_name="Deals Board",
        columns=[],
        semantic_mapping=SemanticMapping(mappings={})
    )
    
    repo = MondayDealRepository(client=mock_client, descriptor=descriptor)
    deals = await repo.get_all_deals()

    
    assert len(deals) == 2
    assert deals[0].id == "1"
    assert deals[1].id == "2"
    assert mock_client.execute.call_count == 2
    
    # Verify the first call had no cursor
    call_1_args = mock_client.execute.call_args_list[0]
    assert "cursor" not in call_1_args.args[1]
    
    # Verify the second call used the cursor
    call_2_args = mock_client.execute.call_args_list[1]
    assert call_2_args.args[1]["cursor"] == "cursor-123"
