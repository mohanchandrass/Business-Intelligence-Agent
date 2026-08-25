import json
import logging
from typing import Dict, Any, List, Callable, Awaitable, Optional
from google.genai import types

from app.config import get_settings
from app.application.snapshot import BusinessDataSnapshot
from app.infrastructure.llm.provider import LLMProvider
from app.agents.tools.registry import ToolRegistry, ToolDefinition
from app.agents.prompts.system import SYSTEM_PROMPT_V1

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, llm_provider: LLMProvider, tool_registry: ToolRegistry):
        self.llm = llm_provider
        self.registry = tool_registry
        self.settings = get_settings().gemini
        
    def _tool_def_to_google_schema(self, tool: ToolDefinition) -> types.Tool:
        """Convert our ToolDefinition to google-genai Tool declaration."""
        # For simplicity, we define basic function declarations. 
        # In a real app we would map the Pydantic model to OpenAPI JSON schema,
        # but for this MVP, we map basic properties.
        schema_props = {}
        required = []
        for field_name, field_info in tool.parameters_schema.model_fields.items():
            # Basic mapping, assume string for simplicity in this MVP
            prop_type = "STRING"
            schema_props[field_name] = types.Schema(type=prop_type, description=field_info.description or "")
            if field_info.is_required():
                required.append(field_name)

        func_decl = types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=types.Schema(
                type="OBJECT",
                properties=schema_props,
                required=required if required else None
            ) if schema_props else None
        )
        return types.Tool(function_declarations=[func_decl])

    async def execute(self, query: str, snapshot_factory: Callable[[], Awaitable[BusinessDataSnapshot]], req_id: str = "REQ unknown") -> Dict[str, Any]:
        messages = [{"role": "user", "parts": [{"text": query}]}]
        snapshot: Optional[BusinessDataSnapshot] = None
        
        logger.info(f"[{req_id}] TOOL REGISTRY preparing tools")
        tools = [self._tool_def_to_google_schema(t) for t in self.registry.get_all_tools()]
        logger.info(f"[{req_id}] Registered {len(tools)} tools for Gemini")
        
        max_turns = self.settings.max_tool_calls if hasattr(self.settings, 'max_tool_calls') else 5
        turn_count = 0
        
        collected_data = []
        collected_warnings = []
        
        while turn_count < max_turns:
            turn_count += 1
            
            # 1. Call LLM
            logger.info(f"[{req_id}] GEMINI REQUEST #{turn_count} sending {len(messages)} messages")
            response = await self.llm.chat(
                messages=messages,
                system_instruction=SYSTEM_PROMPT_V1,
                tools=tools if tools else None
            )
            
            logger.info(f"[{req_id}] GEMINI RESPONSE received: has_text={bool(response.text)}, tool_calls={len(response.tool_calls) if response.tool_calls else 0}")
            
            if response.tool_calls:
                for tc in response.tool_calls:
                    logger.info(f"[{req_id}] Gemini returned function call: {tc.tool_name}")

            if response.text and not response.tool_calls:
                logger.info(f"[{req_id}] GEMINI FINAL RESPONSE generated")
                return {
                    "answer": response.text,
                    "data": collected_data,
                    "warnings": collected_warnings
                }
                
            if not response.tool_calls:
                logger.info(f"[{req_id}] GEMINI FINAL RESPONSE (fallback)")
                return {
                    "answer": "I couldn't process your request.",
                    "data": collected_data,
                    "warnings": collected_warnings
                }
                
            # Add the model's tool call back to history
            # We preserve the raw SDK content (which includes the thought_signature and tool call IDs)
            messages.append({
                "role": "model_tool_call",
                "raw_content": response.raw_content,
                "parts": [{"name": tc.tool_name, "args": tc.arguments} for tc in response.tool_calls]
            })
            
            # 2. Execute tools
            if response.tool_calls and snapshot is None:
                logger.info(f"[{req_id}] Tool call requested, fetching BusinessDataSnapshot lazily")
                snapshot = await snapshot_factory()

            tool_responses = []
            for tc in response.tool_calls:
                logger.info(f"[{req_id}] TOOL CALL executing: {tc.tool_name}")
                tool_def = self.registry.get_tool(tc.tool_name)
                if not tool_def:
                    logger.error(f"[{req_id}] Tool not found: {tc.tool_name}")
                    tool_responses.append({
                        "name": tc.tool_name, 
                        "response": {"error": f"Tool {tc.tool_name} not found"}
                    })
                    continue
                    
                try:
                    # Validate args
                    args = tool_def.parameters_schema(**tc.arguments)
                    # Execute
                    result = await tool_def.handler(snapshot, args)
                    logger.info(f"[{req_id}] TOOL RESULT generated for {tc.tool_name}")
                    
                    # Collect visualization data and warnings for frontend
                    if result.data:
                        if "kpis" in result.data:
                            collected_data.extend(result.data["kpis"])
                        if "tables" in result.data:
                            collected_data.extend(result.data["tables"])
                    if result.warnings:
                        collected_warnings.extend(result.warnings)
                        
                    # Serialize result
                    tool_responses.append({
                        "name": tc.tool_name,
                        "response": result.model_dump(mode="json")
                    })
                except Exception as e:
                    logger.error(f"[{req_id}] Tool execution error: {str(e)}")
                    tool_responses.append({
                        "name": tc.tool_name,
                        "response": {"error": str(e)}
                    })
                    
            # Add tool results back to history
            messages.append({
                "role": "tool",
                "parts": tool_responses
            })
            
        logger.info(f"[{req_id}] Tool limit reached")
        return {
            "answer": "I've reached my internal tool execution limit and couldn't complete the request.",
            "data": collected_data,
            "warnings": collected_warnings
        }
