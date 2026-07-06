"""Schema package — re-exports for convenience."""

from promptstackbench.schema.config import GlobalConfig
from promptstackbench.schema.run import (
    Output,
    Run,
    RunConfig,
    Score,
    Trace,
)
from promptstackbench.schema.task import Task, TaskClass, TaskSuite
from promptstackbench.schema.taxonomy import (
    AgentSpec,
    HarnessSpec,
    LensSpec,
    PersonaSpec,
    SkillSpec,
    TreatmentSpec,
)

__all__ = [
    "AgentSpec",
    "GlobalConfig",
    "HarnessSpec",
    "LensSpec",
    "Output",
    "PersonaSpec",
    "Run",
    "RunConfig",
    "Score",
    "SkillSpec",
    "Task",
    "TaskClass",
    "TaskSuite",
    "Trace",
    "TreatmentSpec",
]
