"""Unit tests for taxonomy schema models."""

from promptstackbench.schema.taxonomy import (
    AgentSpec,
    HarnessSpec,
    LensSpec,
    PersonaSpec,
    SkillSpec,
)


def test_persona_spec_creation():
    spec = PersonaSpec(
        id="test_persona",
        role="senior architect",
        style={"tone": "direct"},
    )
    assert spec.type == "persona"
    assert spec.role == "senior architect"
    assert spec.style["tone"] == "direct"


def test_lens_spec_creation():
    spec = LensSpec(
        id="test_lens",
        viewpoint="security reviewer",
        focus=["injection", "auth"],
        avoid=["rewriting"],
    )
    assert spec.type == "lens"
    assert len(spec.focus) == 2
    assert len(spec.avoid) == 1


def test_skill_spec_creation():
    spec = SkillSpec(
        id="test_skill",
        goal="review architecture",
        procedure=["step 1", "step 2"],
        output_schema={"verdict": "string"},
        checks=["cite evidence"],
    )
    assert spec.type == "skill"
    assert len(spec.procedure) == 2


def test_agent_spec_creation():
    spec = AgentSpec(
        id="test_agent",
        purpose="research synthesis",
        tools=["web_search", "calculator"],
        policies=["prefer primary sources"],
    )
    assert spec.type == "agent"
    assert "web_search" in spec.tools


def test_harness_spec_creation():
    spec = HarnessSpec(
        id="test_harness",
        guards=["prompt_injection_check"],
        evals=["final_answer_quality"],
    )
    assert spec.type == "harness"


def test_spec_is_frozen():
    spec = PersonaSpec(id="frozen_test", role="engineer")
    try:
        spec.role = "architect"
        raise AssertionError("Should have raised")
    except Exception:
        pass
