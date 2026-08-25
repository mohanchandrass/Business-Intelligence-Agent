import asyncio
from app.application.chat import ChatApplicationService
from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.application.snapshot import BusinessDataService
from app.config import get_settings

async def main():
    settings = get_settings()
    monday_client = MondayClient()
    board_catalog = BoardCatalog(client=monday_client)
    data_service = BusinessDataService(catalog=board_catalog)
    chat_service = ChatApplicationService(data_service=data_service)
    
    print(f"Configured model: {chat_service.llm_provider.settings.model}")
    
    result = await chat_service.process_query("What is our total pipeline?")
    print("Answer:")
    print(result.get("answer"))

if __name__ == "__main__":
    asyncio.run(main())
