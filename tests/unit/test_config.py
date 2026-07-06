"""Unit tests for global configuration."""

from promptstackbench.schema.config import GlobalConfig


def test_config_loads_api_key_from_openapi_env(monkeypatch):
    monkeypatch.setenv("OPENAPI_API_KEY", "primary-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    config = GlobalConfig()

    assert config.api_key == "primary-key"


def test_config_falls_back_to_openai_env(monkeypatch):
    monkeypatch.delenv("OPENAPI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-key")

    config = GlobalConfig()

    assert config.api_key == "legacy-key"
