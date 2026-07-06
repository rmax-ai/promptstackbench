"""Task definition models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TaskClass(StrEnum):
    """Task complexity classes matching the benchmark design."""

    EXPLANATION = "explanation"
    ARCHITECTURE_REVIEW = "architecture_review"
    ADVISORY = "advisory"
    TOOL_USE = "tool_use"
    SAFETY = "safety"
    STATEFUL = "stateful"
    RESEARCH = "research"


class Task(BaseModel):
    """A single benchmark task with its input and expected properties."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9_-]+$")
    suite_id: str = Field(..., min_length=1)
    task_class: TaskClass
    input: str = Field(..., min_length=1)
    expected_properties: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)


class TaskSuite(BaseModel):
    """A collection of tasks for a single suite."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    name: str = Field(..., min_length=1)
    description: str = ""
    task_class: TaskClass
    tasks: list[Task] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.tasks)
