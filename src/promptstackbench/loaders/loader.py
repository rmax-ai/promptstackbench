"""Load taxonomy specs and task suites from YAML files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path  # noqa: TC003
from typing import Any

import yaml

from promptstackbench.errors import LoaderError
from promptstackbench.schema.task import Task, TaskSuite
from promptstackbench.schema.taxonomy import (
    AgentSpec,
    HarnessSpec,
    LensSpec,
    PersonaSpec,
    SkillSpec,
    TreatmentSpec,
)

TYPE_MAP: dict[str, type[TreatmentSpec]] = {
    "persona": PersonaSpec,
    "lens": LensSpec,
    "skill": SkillSpec,
    "agent": AgentSpec,
    "harness": HarnessSpec,
}


def _read_yaml(path: Path) -> dict[str, Any]:
    """Read and parse a YAML file."""
    if not path.exists():
        raise LoaderError(f"File not found: {path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise LoaderError(f"Expected YAML mapping in {path}, got {type(data).__name__}")
    return data


def load_treatment_spec(path: Path) -> TreatmentSpec:
    """Load a single treatment spec from a YAML file."""
    data = _read_yaml(path)
    spec_type = data.get("type", "")
    model_cls = TYPE_MAP.get(spec_type)
    if model_cls is None:
        raise LoaderError(f"Unknown treatment type '{spec_type}' in {path}")
    return model_cls(**data)


def load_treatment_specs(specs_dir: Path) -> dict[str, list[TreatmentSpec]]:
    """Load all treatment specs from a directory tree.

    Returns dict keyed by type (persona, lens, skill, agent, harness).
    """
    result: dict[str, list[TreatmentSpec]] = {t: [] for t in TYPE_MAP}
    if not specs_dir.exists():
        return result
    for yaml_path in sorted(specs_dir.rglob("*.yaml")):
        try:
            spec = load_treatment_spec(yaml_path)
            result[spec.type].append(spec)
        except LoaderError:
            continue
    return result


def load_task_suite(path: Path) -> TaskSuite:
    """Load a task suite from a YAML file."""
    data = _read_yaml(path)
    return TaskSuite(**data)


def load_all_task_suites(datasets_dir: Path) -> list[TaskSuite]:
    """Load all task suites from a directory."""
    suites: list[TaskSuite] = []
    if not datasets_dir.exists():
        return suites
    for yaml_path in sorted(datasets_dir.rglob("*.yaml")):
        if yaml_path.name.startswith("_"):
            continue
        try:
            suites.append(load_task_suite(yaml_path))
        except Exception:
            continue
    return suites


def compute_spec_hash(spec: TreatmentSpec) -> str:
    """Compute a content hash for a treatment spec."""
    raw = spec.model_dump(mode="json", exclude={"id"})
    return hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()[:12]


def generate_prompt(task: Task, treatment: TreatmentSpec) -> str:
    """Generate a prompt by combining a task with a treatment spec."""
    if isinstance(treatment, PersonaSpec):
        style_lines = "\n".join(f"- {k}: {v}" for k, v in treatment.style.items())
        return f"You are a {treatment.role}.\nStyle:\n{style_lines}\n\n{task.input}"

    if isinstance(treatment, LensSpec):
        focus_lines = "\n".join(f"- {f}" for f in treatment.focus)
        avoid_lines = (
            "\n".join(f"- {a}" for a in treatment.avoid) if treatment.avoid else ""
        )
        avoid_section = f"\nDo NOT:\n{avoid_lines}\n" if avoid_lines else ""
        return (
            f"You are reviewing this from the viewpoint of: {treatment.viewpoint}.\n"
            f"Focus on:\n{focus_lines}\n"
            f"{avoid_section}\n"
            f"{task.input}"
        )

    if isinstance(treatment, SkillSpec):
        proc_lines = "\n".join(
            f"{i + 1}. {step}" for i, step in enumerate(treatment.procedure)
        )
        schema_lines = "\n".join(
            f"- {k}: {v}" for k, v in treatment.output_schema.items()
        )
        checks_lines = (
            "\n".join(f"- {c}" for c in treatment.checks) if treatment.checks else ""
        )
        checks_section = f"\nChecks:\n{checks_lines}\n" if checks_lines else ""
        return (
            f"Goal: {treatment.goal}\n\n"
            f"Procedure:\n{proc_lines}\n\n"
            f"Output schema:\n{schema_lines}\n"
            f"{checks_section}\n"
            f"{task.input}"
        )

    if isinstance(treatment, AgentSpec):
        tools_str = ", ".join(treatment.tools) if treatment.tools else "none"
        policies_str = (
            "\n".join(f"- {p}" for p in treatment.policies)
            if treatment.policies
            else ""
        )
        return (
            f"Purpose: {treatment.purpose}\n\n"
            f"Available tools: {tools_str}\n"
            f"Policies:\n{policies_str}\n\n"
            f"{task.input}"
        )

    if isinstance(treatment, HarnessSpec):
        guards_str = ", ".join(treatment.guards) if treatment.guards else "none"
        return (
            f"Running with harness supervision.\n"
            f"Active guards: {guards_str}\n\n"
            f"{task.input}"
        )

    return task.input
