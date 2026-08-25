from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

class ApplicationSettings(BaseSettings):
    app_name: str = "Skylark BI Backend"
    cors_origins: str = Field("http://localhost:3000,http://10.17.7.218:3000", validation_alias="CORS_ORIGINS")

class MondaySettings(BaseSettings):
    api_token: str = Field(..., validation_alias="MONDAY_API_TOKEN")
    api_url: str = Field("https://api.monday.com/v2", validation_alias="MONDAY_API_URL")
    api_version: str = Field("2026-07", validation_alias="MONDAY_API_VERSION")
    deals_board_id: Optional[str] = Field(None, validation_alias="MONDAY_DEALS_BOARD_ID")
    work_orders_board_id: Optional[str] = Field(None, validation_alias="MONDAY_WORK_ORDERS_BOARD_ID")
    default_board_ids: Optional[str] = Field(None, validation_alias="MONDAY_DEFAULT_BOARD_IDS")
    timeout_seconds: int = Field(30, validation_alias="MONDAY_TIMEOUT_SECONDS")
    max_retries: int = Field(3, validation_alias="MONDAY_MAX_RETRIES")
    
class GeminiSettings(BaseSettings):
    api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    model: str = Field("gemini-3.5-flash-lite", validation_alias="GEMINI_MODEL")
    temperature: float = Field(0.0, validation_alias="GEMINI_TEMPERATURE")
    max_output_tokens: int = Field(2048, validation_alias="GEMINI_MAX_OUTPUT_TOKENS")
    top_p: float = Field(0.95, validation_alias="GEMINI_TOP_P")
    top_k: int = Field(40, validation_alias="GEMINI_TOP_K")

class AgentSettings(BaseSettings):
    max_tool_calls: int = Field(5, validation_alias="AGENT_MAX_TOOL_CALLS")
    max_context_records: int = Field(50, validation_alias="AGENT_MAX_CONTEXT_RECORDS")

class AnalyticsSettings(BaseSettings):
    default_currency: str = Field("INR", validation_alias="DEFAULT_CURRENCY")

class Settings(BaseSettings):
    app: ApplicationSettings = Field(default_factory=ApplicationSettings)
    monday: MondaySettings = Field(default_factory=MondaySettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    analytics: AnalyticsSettings = Field(default_factory=AnalyticsSettings)

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../.env"),
        env_file_encoding='utf-8',
        extra='ignore',
        env_nested_delimiter='__'
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
