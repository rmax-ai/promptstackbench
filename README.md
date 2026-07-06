# PromptStackBench

Evaluate when a persona should become a skill, when a skill should become an
agent, and when an agent needs a harness.

## What

PromptStackBench runs the same task through five control abstractions —
persona, lens, skill, agent, harness — then compares outputs on correctness,
clarity, groundedness, stability, cost, latency, and promotion value.

It answers the practical engineering question: **at what task complexity does
each abstraction stop being enough?**

Today the runnable benchmark focuses on persona, lens, and skill. Distinct
agent and harness runtimes are planned, but not yet implemented beyond
spec/prompt support.

## Quickstart

```bash
# Install
cd promptstackbench
uv sync --extra dev

# Create a fresh benchmark workspace inside the repo-local scratch area
mkdir -p workspace/readme-example
uv run promptstackbench init --path workspace/readme-example

# Set your API key for non-mock runs
export OPENAPI_API_KEY=<api-key>

# Run a benchmark suite without API calls
uv run promptstackbench run \
  --suite architecture_review \
  --treatments persona,lens,skill \
  --repetitions 1 \
  --paraphrases 1 \
  --mock \
  --data-dir workspace/readme-example/datasets \
  --specs-dir workspace/readme-example/specs \
  --traces-dir workspace/readme-example/traces

# Generate a report for the latest scored run
uv run promptstackbench report \
  --latest \
  --format html \
  --traces-dir workspace/readme-example/traces

# Check promotion value for the latest run of a suite
uv run promptstackbench promote \
  --suite architecture_review \
  --from persona \
  --to skill \
  --traces-dir workspace/readme-example/traces
```

## Architecture

PromptStackBench is a Python CLI tool backed by SQLite. It loads task suites
and taxonomy specs from YAML, runs them through LLM providers, scores outputs
for answer quality, groundedness, schema validity, and instruction adherence,
then generates comparison reports with robustness and operational summaries.

```
datasets/         Task suite fixtures and examples
docs/             Static docs website
src/              Python source
tests/            Pytest suite
```

`promptstackbench init` expects a new target directory. This repository keeps an
ignored scratch area at `workspace/`; the examples above create
`workspace/readme-example/` and let `init` populate it with `specs/`,
`datasets/`, `traces/`, and `config.yaml`. For real model runs, the CLI reads
`OPENAPI_API_KEY` by default and falls back to `OPENAI_API_KEY`, `config.yaml`,
or `--api-key`.

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

## Taxonomy Layers

| Layer | What it controls | Best for |
|-------|-----------------|----------|
| Persona | Role, tone, style | Low-risk tasks where voice matters |
| Lens | Constrained viewpoint | Tasks needing a stable perspective |
| Skill | Procedure + output schema | Repeatable, reviewable tasks |
| Agent | Planned richer runtime with tools, state, multi-step execution | Tasks requiring search, tools, branching |
| Harness | Planned control layer with guards, retry, audit behavior | Compliance, safety, production actions |

## Metrics

- **Answer quality:** correctness, completeness, clarity, relevance
- **Grounding and structure:** hallucination score, schema validity, instruction adherence
- **Robustness:** paraphrase stability, run variance
- **Operational:** tokens, latency, cost

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design
- [DECISIONS.md](DECISIONS.md) — design rationale
- [ROADMAP.md](ROADMAP.md) — phased delivery plan
- [SPEC.md](SPEC.md) — feature specification

## License

MIT
