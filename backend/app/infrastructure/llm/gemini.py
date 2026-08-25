from google import genai
from google.genai import types
from typing import Dict, Any, List, Optional
from app.config import get_settings
from app.infrastructure.llm.provider import LLMProvider, LLMProviderError, LLMResponse, ToolCallRequest

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.settings = get_settings().gemini
        self.client = genai.Client(api_key=self.settings.api_key)

    async def verify_authentication(self) -> Dict[str, Any]:
        """Test authentication to the Gemini provider by listing models."""
        try:
            models = await self.list_available_models()
            if models:
                return {"status": "success", "message": "Authentication successful", "models_count": len(models)}
            return {"status": "error", "message": "Authenticated but no models found"}
        except LLMProviderError as e:
            return {"status": "error", "message": str(e)}

    async def list_available_models(self) -> List[str]:
        """List models available to the current API key."""
        try:
            models = []
            async for model in self.client.aio.models.list():
                models.append(model.name)
            return models
        except Exception as e:
            raise LLMProviderError(f"Failed to list models: {str(e)}") from e

    async def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt."""
        try:
            response = await self.client.aio.models.generate_content(
                model=self.settings.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise LLMProviderError(f"Generation failed: {str(e)}") from e

    async def chat(self, messages: List[Dict[str, Any]], system_instruction: Optional[str] = None, tools: Optional[List[Any]] = None) -> LLMResponse:
        try:
            formatted_contents = []
            for msg in messages:
                role = msg.get("role", "user")
                if role == "tool":
                    # Tool responses go into a user content part
                    parts = [types.Part.from_function_response(name=p["name"], response=p["response"]) for p in msg.get("parts", [])]
                    formatted_contents.append(types.Content(role="user", parts=parts))
                elif role == "model_tool_call":
                    # The model's previous tool calls
                    # If we have the raw_content (types.Content), use it directly
                    raw_content = msg.get("raw_content")
                    if raw_content:
                        formatted_contents.append(raw_content)
                    else:
                        # Fallback for old tests or manual dicts
                        parts = [types.Part.from_function_call(name=p["name"], args=p["args"]) for p in msg.get("parts", [])]
                        formatted_contents.append(types.Content(role="model", parts=parts))
                else:
                    parts = [types.Part.from_text(text=p["text"]) for p in msg.get("parts", [])]
                    formatted_contents.append(types.Content(role=role, parts=parts))

            config = types.GenerateContentConfig(
                temperature=self.settings.temperature,
                max_output_tokens=self.settings.max_output_tokens,
                top_p=self.settings.top_p,
                top_k=self.settings.top_k,
                system_instruction=system_instruction
            )
            
            if tools:
                config.tools = tools
                # Explicitly disable automatic function execution since the application manages it
                config.automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)

            response = await self.client.aio.models.generate_content(
                model=self.settings.model,
                contents=formatted_contents,
                config=config
            )

            tool_calls = []
            if response.function_calls:
                for fc in response.function_calls:
                    # In python SDK, response.candidates[0].content.parts contains the actual parts
                    # However, we can just pass the raw FunctionCall object (fc) which has the thought_signature
                    tool_calls.append(ToolCallRequest(
                        tool_name=fc.name,
                        arguments=fc.args,
                        raw_part=fc
                    ))
                    
            return LLMResponse(
                text=response.text,
                tool_calls=tool_calls,
                raw_content=response.candidates[0].content if response.candidates else None
            )
        except Exception as e:
            raise LLMProviderError(f"Chat execution failed: {str(e)}") from e
