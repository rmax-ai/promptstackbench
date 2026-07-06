"""Unit tests for loader module."""

import tempfile
from pathlib import Path

import yaml

from promptstackbench.loaders.loader import (
    generate_prompt,
    load_task_suite,
    load_treatment_spec,
)
from promptstackbench.schema.task import Task, TaskClass
from promptstackbench.schema.taxonomy import LensSpec, PersonaSpec, SkillSpec


def test_load_treatment_spec_persona():
    data = {
        "id": "test_persona",
        "type": "persona",
        "role": "senior architect",
        "style": {"tone": "direct", "depth": "high"},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(data, f)
        path = Path(f.name)
    try:
        spec = load_treatment_spec(path)
        assert isinstance(spec, PersonaSpec)
        assert spec.role == "senior architect"
    finally:
        path.unlink()


def test_generate_persona_prompt():
    task = Task(
        id="t1",
        suite_id="s1",
        task_class=TaskClass.ARCHITECTURE_REVIEW,
        input="Review this design.",
    )
    treatment = PersonaSpec(
        id="p1",
        role="senior architect",
        style={"tone": "direct"},
    )
    prompt = generate_prompt(task, treatment)
    assert "senior architect" in prompt
    assert "Review this design." in prompt
    assert "tone: direct" in prompt


def test_generate_skill_prompt():
    task = Task(
        id="t1",
        suite_id="s1",
        task_class=TaskClass.ARCHITECTURE_REVIEW,
        input="Review this design.",
    )
    treatment = SkillSpec(
        id="s1",
        goal="assess production readiness",
        procedure=["extract assumptions", "identify coupling"],
        output_schema={"verdict": "string"},
        checks=["cite evidence"],
    )
    prompt = generate_prompt(task, treatment)
    assert "Goal: assess production readiness" in prompt
    assert "1. extract assumptions" in prompt
    assert "Output schema:" in prompt


def test_generate_lens_prompt():
    task = Task(
        id="t1",
        suite_id="s1",
        task_class=TaskClass.ARCHITECTURE_REVIEW,
        input="Review this design.",
    )
    treatment = LensSpec(
        id="l1",
        viewpoint="security reviewer",
        focus=["injection", "auth"],
        avoid=["rewriting"],
    )
    prompt = generate_prompt(task, treatment)
    assert "viewpoint of: security reviewer" in prompt
    assert "injection" in prompt
    assert "Do NOT:" in prompt


def test_load_task_suite():
    data = {
        "id": "test_suite",
        "name": "Test Suite",
        "task_class": "architecture_review",
        "tasks": [
            {
                "id": "t1",
                "suite_id": "test_suite",
                "task_class": "architecture_review",
                "input": "Review this.",
            }
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(data, f)
        path = Path(f.name)
    try:
        suite = load_task_suite(path)
        assert suite.name == "Test Suite"
        assert len(suite.tasks) == 1
    finally:
        path.unlink()
