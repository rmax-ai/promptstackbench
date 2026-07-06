# PromptStackBench Architecture

## Problem Statement

Teams compare prompt styles informally: "this persona works better", "this
agent feels smarter", "this skill prompt is cleaner." That is not evaluation.
It is prompt folklore.

PromptStackBench evaluates whether a taxonomy of control abstractions —
persona, lens, skill, agent, harness — has operational value. It shows, with
traces and metrics, that different layers behave differently under controlled
task conditions.

## Design Goals

1. **Reproducibility** — every run is traceable, re-runnable, and auditable
2. **Task-conditional evaluation** — not "which layer is best" but "when does
   each layer pay for itself"
3. **Model-agnostic** — works with any LLM provider behind a consistent adapter
4. **Minimal infrastructure** — SQLite, single process, zero containers
5. **Report-first** — the report is the product; runs feed reports

## Component Diagram

```
┌──────────┐    ┌───────────┐    ┌──────────────┐    ┌──────────┐
│  CLI     │───▶│  Runner   │───▶│  LLM Provider │───▶│  Model   │
│  (Typer) │    │  Engine   │    │  (httpx)      │    │  API     │
└──────────┘    └───────────┘    └──────────────┘    └──────────┘
       │              │
       ▼              ▼
┌──────────┐    ┌───────────┐    ┌──────────────┐
│  Report  │◀───│ Evaluator │◀───│  Trace Store  │
│  (HTML)  │    │  Pipeline │    │  (SQLite)     │
└──────────┘    └───────────┘    └──────────────┘
```

## Data Flow

1. CLI loads task suite + taxonomy specs from YAML
2. Runner generates prompt variants (persona, lens, skill, agent, harness)
3. Each variant sent to LLM provider N times (repetitions) + P paraphrases
4. Raw outputs + traces captured in SQLite
5. Evaluator pipeline scores each output on 7+ metrics
6. Report generator produces comparison HTML/Markdown with promotion signals

## Module Layout

```
src/promptstackbench/
├── __init__.py
├── cli.py              # Typer app entry point
├── errors.py           # Domain exception hierarchy
├── schema/
│   ├── __init__.py
│   ├── taxonomy.py     # PersonaSpec, LensSpec, SkillSpec, AgentSpec, HarnessSpec
│   ├── task.py         # TaskSuite, Task, TaskClass
│   ├── run.py          # RunConfig, Run, Output, Trace, Score
│   └── config.py       # Global config (model, API keys, paths)
├── runners/
│   ├── __init__.py
│   ├── llm_runner.py   # LLMProvider adapter, completion calls
│   ├── agent_runner.py # Agent execution (future phase)
│   └── harness_runner.py # Harness execution (future phase)
├── evaluators/
│   ├── __init__.py
│   ├── final_answer.py # Correctness, completeness, clarity, relevance
│   ├── schema.py       # Output schema validity
│   ├── grounding.py    # Factual grounding, hallucinated claims
│   ├── trajectory.py   # Tool-use quality (future phase)
│   ├── safety.py       # Injection resistance, role drift (future phase)
│   └── robustness.py   # Paraphrase stability, run variance
├── reports/
│   ├── __init__.py
│   ├── markdown.py     # Markdown report generator
│   └── html.py         # HTML report generator
├── loaders/
│   ├── __init__.py
│   ├── task_loader.py  # Load task suites from YAML
│   └── spec_loader.py  # Load taxonomy specs from YAML
└── store/
    ├── __init__.py
    └── db.py           # SQLite trace store (runs, tasks, outputs, traces, scores)
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SQLite, not Postgres | Zero-infra MVP; single process; no Docker |
| YAML for specs/datasets | Human-readable, diffable, no database dependency for config |
| Pydantic v2 frozen models | Immutable configs prevent accidental mutation across runs |
| LLM-as-judge for eval | Required for qualitative metrics (clarity, relevance); use
  golden checks + schema validation as calibration |
| Single Typer CLI | Simple UX; no web UI in MVP |
| Reports as Jinja2 templates | Separates presentation from data; easy to extend |

## Trade-offs

| Decision | Trade-off |
|----------|-----------|
| SQLite | Single-writer constraint; no concurrent runs. Acceptable for MVP. |
| LLM-as-judge | Evaluator variance; mitigate with golden checks + repeated evals |
| Single process | No horizontal scaling. MVP scope is small — 20 tasks, 5 treatments, 3 reps, 5 paraphrases ≈ 1,500 LLM calls. |
| YAML datasets | No query interface; manual curation. Acceptable for curated benchmark suites. |
