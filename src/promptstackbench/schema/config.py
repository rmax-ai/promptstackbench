"""Global configuration model."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class GlobalConfig(BaseModel):
    """Global PromptStackBench configuration."""

    model_config = ConfigDict(frozen=False, extra="forbid")

    default_model: str = "gpt-4.1"
    default_provider: str = "openai"
    api_base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    data_dir: Path = Field(default_factory=lambda: Path("datasets"))
    specs_dir: Path = Field(default_factory=lambda: Path("specs"))
    traces_dir: Path = Field(default_factory=lambda: Path("traces"))
    db_path: Path = Field(default_factory=lambda: Path("traces/runs.sqlite"))
    judge_model: str = "gpt-4.1"
    judge_temperature: float = 0.0
    max_retries: int = 3
    request_timeout: int = 120
