import pytest
from google.genai import types
from app.infrastructure.llm.gemini import GeminiProvider
from app.infrastructure.llm.provider import ToolCallRequest

@pytest.mark.asyncio
async def test_gemini_preserves_raw_content_for_tool_calls():
    # Arrange
    provider = GeminiProvider()
    
    # Simulate a raw SDK FunctionCall Content part that has a thought_signature
    mock_raw_content = types.Content(
        role="model", 
        parts=[types.Part.from_function_call(name="dummy_tool", args={"x": 1})]
    )
    # The SDK would have attached internal attributes to the raw response part here
    
    messages = [
        {"role": "user", "parts": [{"text": "Hello"}]},
        {
            "role": "model_tool_call",
            "raw_content": mock_raw_content,
            "parts": [{"name": "dummy_tool", "args": {"x": 1}}]
        },
        {
            "role": "tool",
            "parts": [{"name": "dummy_tool", "response": {"result": 2}}]
        }
    ]
    
    from unittest.mock import AsyncMock, patch
    
    mock_generate_content = AsyncMock()
    mock_generate_content.return_value = types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(parts=[types.Part.from_text(text="I got the result")]))]
    )
    
    # Act
    with patch.object(provider.client.aio.models, 'generate_content', mock_generate_content):
        await provider.chat(messages=messages)
    
    # Assert
    # generate_content was called with args/kwargs. We want to inspect contents kwarg
    mock_generate_content.assert_called_once()
    kwargs = mock_generate_content.call_args.kwargs
    sent_contents = kwargs.get('contents', [])
    assert len(sent_contents) == 3
    
    # The first is user text
    assert sent_contents[0].role == "user"
    
    # The second MUST be our mock_raw_content object exactly, not a reconstructed dictionary-based part
    assert sent_contents[1] is mock_raw_content
    
    # The third is the tool response which gets converted to role='user' with function_response
    assert sent_contents[2].role == "user"
    assert sent_contents[2].parts[0].function_response.name == "dummy_tool"
