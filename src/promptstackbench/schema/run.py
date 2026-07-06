"""Run, output, trace, and score data models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RunConfig(BaseModel):
    """Configuration for a benchmark run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    suite_id: str
    model: str
    treatments: list[str]
    repetitions: int = Field(default=3, ge=1)
    paraphrases: int = Field(default=5, ge=1)
    api_key: str = Field(default="")


class Run(BaseModel):
    """A benchmark run record."""

    id: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%d-%H%M%S")
    )
    suite_id: str
    model: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    git_sha: str = ""
    config_hash: str = ""


class Output(BaseModel):
    """A single model output from a treatment+task combination."""

    id: str | None = None
    run_id: str
    task_id: str
    treatment_id: str
    treatment_type: str
    paraphrase_index: int = 0
    repetition_index: int = 0
    raw_output: str = ""
    parsed_output: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0
    token_input: int = 0
    token_output: int = 0
    cost_estimate: float = 0.0


class Trace(BaseModel):
    """A single trace event from an agent/harness execution."""

    id: str | None = None
    output_id: str
    step_index: int
    event_type: str  # "tool_call", "tool_result", "guard_check", "retry"
    content: str = ""
    tool_name: str = ""
    tool_args: dict[str, Any] = Field(default_factory=dict)
    tool_result: str = ""


class Score(BaseModel):
    """An evaluation score for a single metric on a single output."""

    id: str | None = None
    output_id: str = ""
    metric: str
    score: float
    rationale: str = ""
    evaluator_model: str = ""
    evaluator_version: str = ""
