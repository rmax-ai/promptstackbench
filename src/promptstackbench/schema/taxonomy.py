"""Taxonomy specification models — the five control abstractions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PersonaSpec(BaseModel):
    """A persona is only role and interaction style.

    Expected strength: easy to write, good UX.
    Expected weakness: hidden assumptions, weak reproducibility, role drift.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    type: str = Field(default="persona", frozen=True)
    role: str = Field(..., min_length=1)
    style: dict[str, str] = Field(default_factory=dict)


class LensSpec(BaseModel):
    """A lens is a constrained viewpoint, not a fake identity.

    Expected strength: sharper than persona, less theatrical.
    Expected weakness: still does not define a full procedure.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    type: str = Field(default="lens", frozen=True)
    viewpoint: str = Field(..., min_length=1)
    focus: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)


class SkillSpec(BaseModel):
    """A skill is the default useful abstraction.

    Expected strength: interpretable, testable, reusable.
    Expected weakness: limited when external tools, memory, or multi-step
    recovery are required.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    type: str = Field(default="skill", frozen=True)
    goal: str = Field(..., min_length=1)
    inputs: list[str] = Field(default_factory=list)
    procedure: list[str] = Field(default_factory=list)
    output_schema: dict[str, str] = Field(default_factory=dict)
    checks: list[str] = Field(default_factory=list)


class AgentSpec(BaseModel):
    """An agent is a skill-bearing runtime with tools and state.

    Expected strength: useful for multi-step, tool-using tasks.
    Expected weakness: more moving parts, more failure modes, more trace
    complexity.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    type: str = Field(default="agent", frozen=True)
    purpose: str = Field(..., min_length=1)
    skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    policies: list[str] = Field(default_factory=list)
    termination: dict[str, str] = Field(default_factory=dict)


class HarnessSpec(BaseModel):
    """The harness is the evaluation and control layer around agents.

    Expected strength: auditability, regression testing, production realism.
    Expected weakness: highest implementation complexity.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    type: str = Field(default="harness", frozen=True)
    orchestration: dict[str, object] = Field(default_factory=dict)
    guards: list[str] = Field(default_factory=list)
    tracing: dict[str, bool] = Field(default_factory=dict)
    evals: list[str] = Field(default_factory=list)


TreatmentSpec = PersonaSpec | LensSpec | SkillSpec | AgentSpec | HarnessSpec
