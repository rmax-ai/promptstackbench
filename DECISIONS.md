# Decisions

## Major Assumptions

1. LLM-as-judge can produce useful comparative scores when calibrated with
   golden checks and schema validation.
2. Task complexity correlates with taxonomy layer value — simple factual tasks
   may show no benefit from agents/harnesses; tool-using tasks will.
3. A single model backend (OpenAI-compatible API) is sufficient for MVP.
   Multi-provider support adds complexity without changing the core question.
4. SQLite is adequate for the run volume: ~1,500 LLM calls per full suite run,
   single-user, no concurrent writes.

## Key Decisions

### SQLite over Postgres
**Chosen:** SQLite via aiosqlite (in-process file DB).
**Rejected:** PostgreSQL + Docker.
**Why:** Zero infrastructure. The data model is simple (6 tables, no
concurrent writers). Migrate to Postgres only when multi-user or production
persistence is needed.

### Pydantic v2 frozen models for specs
**Chosen:** All taxonomy specs (PersonaSpec, LensSpec, SkillSpec, etc.) are
`frozen=True`.
**Why:** Immutable config prevents accidental mutation when specs are shared
across multiple runner threads or reused across runs. The spec IS the source
of truth — it should not change during execution.

### YAML for datasets and specs
**Chosen:** YAML files in `datasets/` and `specs/`.
**Rejected:** JSON (less human-readable for prompts) and SQLite for config
(tighter coupling between data and execution).
**Why:** YAML is diffable, supports multi-line strings (prompts), and doesn't
require a database for curation. Task suites are authored by humans; YAML is
the right format.

### LLM-as-judge with calibration
**Chosen:** Use a judge model (same or different from the tested model) for
qualitative metrics — clarity, completeness, relevance, instruction adherence.
**Rejected:** Human-only evaluation, rule-based scoring.
**Why:** Human evaluation doesn't scale. Rule-based scoring (regex, keyword
matching) can't assess clarity or instruction adherence. The cost of
LLM-as-judge variance is acceptable when calibrated with:
- Golden answer checks (known-correct reference outputs)
- Schema validity checks (structural, not semantic)
- Paraphrase perturbation tests (same task, different wording)

### Single process, no async for MVP
**Chosen:** Synchronous execution with httpx for HTTP calls.
**Rejected:** asyncio event loop, background task workers.
**Why:** The MVP runs ~1,500 sequential LLM calls per suite. Async adds
complexity without throughput gain until we need concurrent provider calls or
parallel task execution. Revisit when Phase 3 (harness evaluation) needs
concurrent agent runs.

### Typer CLI over web UI
**Chosen:** Single Typer CLI with `init`, `run`, `report`, `promote`.
**Rejected:** FastAPI + React, Streamlit, Gradio.
**Why:** The primary user is a researcher running experiments. A CLI with
`--suite`, `--treatments`, `--repetitions` is the right interface. A web UI
can come later if the project outgrows the evaluation-lab phase.

## Known Limitations

- LLM-as-judge produces evaluator variance that may mask small (2-3%) quality
  differences between treatments. Accept this as a known limitation — the
  interesting signals are the 10-20% jumps where a taxonomy promotion clearly
  pays off.
- Paraphrase stability scoring requires generating P paraphrases per task
  variant, which multiplies LLM call volume. Start with P=5 and measure
  whether P=3 is sufficient.
- No real tool integration in Phase 1 (persona, lens, skill only). Agent and
  harness treatment columns will show "not applicable" until Phase 2-3.
- The promote command (`promptstackbench promote --from persona --to skill`)
  relies on having run data in the SQLite store. It cannot compute promotion
  signals without prior runs.
