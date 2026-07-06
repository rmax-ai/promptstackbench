# AGENTS.md — Guidelines for PromptStackBench

This document captures the conventions and guidelines that all contributors
and AI coding agents should follow when working on **PromptStackBench**.

---

## 1. Project DNA

PromptStackBench is a **taxonomy evaluation harness** — it runs the same task
through five control abstractions (persona, lens, skill, agent, harness) and
compares outputs on correctness, clarity, stability, safety, tool-use quality,
cost, latency, and trace quality.

It is NOT an agent platform. It is NOT a production governance UI.
It is an evaluation lab for answering: at what task complexity does each
abstraction stop being enough?

## 2. Code Organisation

- `src/promptstackbench/` — all source code
  - `specs/` — taxonomy configuration objects (persona, lens, skill, agent, harness)
  - `runners/` — LLM runner, agent runner, harness runner
  - `evaluators/` — metric evaluators (final-answer, schema, grounding, trajectory, safety, robustness)
  - `reports/` — HTML and markdown report generation
  - `cli.py` — Typer CLI entry point
- `datasets/` — benchmark task suites (YAML)
- `tests/` — mirrors src layout
- `docs/` — user-facing documentation

Single responsibility per module. No module over 500 lines without explicit
justification.

## 3. Error Handling

- All domain errors inherit from `PromptStackBenchError` in `errors.py`
- Runner errors: `RunnerError` (model unavailable, timeout, bad config)
- Evaluator errors: `EvalError` (missing data, invalid score shape)
- Never swallow exceptions silently — log and propagate or wrap

## 4. Python Conventions

- Python 3.12+ with PEP 695 inline generics
- Pydantic v2 for all data models (`model_config = {"extra": "forbid", "frozen": True}`)
- Typer for CLI (`no_args_is_help=True`, ctx.obj for shared state)
- `datetime.now(UTC)` — never `datetime.utcnow()`
- `from __future__ import annotations` everywhere
- Structured logging with `structlog` (key-value, never f-strings in log calls)

## 5. Testing

- Tests in `tests/` mirroring `src/promptstackbench/`
- pytest only (no unittest.TestCase)
- Unit tests for pure logic and schemas
- Integration tests for runner + evaluator pipelines
- Contract tests for YAML spec format
- Coverage target: >80% on evaluators and schemas
- Test names: `test_<what>_when_<condition>`

## 6. Documentation

- Docstrings on all public API (module-level, class, function)
- README.md kept current with CLI commands
- ARCHITECTURE.md updated for any architectural change
- ROADMAP.md checked off as phases complete

## 7. Dependencies

- `pydantic>=2.0` — data models
- `typer>=0.12` — CLI
- `rich>=13.0` — terminal output
- `pyyaml>=6.0` — dataset and spec loading
- `jinja2>=3.1` — HTML/Markdown reports
- `httpx>=0.27` — LLM API calls
- Dev: `pytest`, `ruff`

No new dependencies without explicit justification. Prefer stdlib where
sufficient.

## 8. Formatting and Linting

- Ruff: format + lint with `src/promptstackbench/ tests/`
- 88 char line limit
- Double quotes
- Import order: stdlib, third-party, first-party (I rule)

## 9. CI / CD

Not yet configured — add GitHub Actions for lint + test on push when the MVP
is stable.

## 10. References

- `ARCHITECTURE.md` — system design and component layout
- `DECISIONS.md` — design rationale
- `ROADMAP.md` — phased delivery plan
- `SPEC.md` — feature specification and acceptance criteria
