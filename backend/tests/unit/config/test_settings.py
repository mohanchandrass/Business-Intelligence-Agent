import pytest
import os
from pydantic import ValidationError
from app.config.settings import Settings, MondaySettings, GeminiSettings

def test_settings_can_instantiate_with_env(monkeypatch):
    """Test that settings load correctly when all required variables are present."""
    monkeypatch.setenv("MONDAY_API_TOKEN", "fake_token")
    monkeypatch.setenv("MONDAY_DEALS_BOARD_ID", "123")
    monkeypatch.setenv("MONDAY_WORK_ORDERS_BOARD_ID", "456")
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini")
    
    settings = Settings()
    
    assert settings.monday.api_token == "fake_token"
    assert settings.monday.deals_board_id == "123"
    assert settings.gemini.api_key == "fake_gemini"

def test_settings_fails_without_required_secrets():
    """Test that settings fail to instantiate if required variables are missing."""
    # Ensure environment is clear of required vars
    if "MONDAY_API_TOKEN" in os.environ:
        del os.environ["MONDAY_API_TOKEN"]
        
    with pytest.raises(ValidationError):
        MondaySettings()
