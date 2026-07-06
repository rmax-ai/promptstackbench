# PromptStackBench

Evaluate when a persona should become a skill, when a skill should become an
agent, and when an agent needs a harness.

## What

PromptStackBench runs the same task through five control abstractions —
persona, lens, skill, agent, harness — then compares outputs on correctness,
clarity, stability, safety, tool-use quality, cost, latency, and trace quality.

It answers the practical engineering question: **at what task complexity does
each abstraction stop being enough?**

## Quickstart

```bash
# Install
cd promptstackbench
uv sync --extra dev

# Initialize a benchmark workspace
uv run promptstackbench init

# Run a benchmark suite
uv run promptstackbench run \
  --suite architecture_review \
  --model gpt-4.1 \
  --treatments persona,lens,skill \
  --repetitions 3 \
  --paraphrases 5

# Generate a report
uv run promptstackbench report \
  --run-id 2026-07-06-arch-review \
  --format html

# Check promotion value
uv run promptstackbench promote \
  --suite architecture_review \
  --from persona \
  --to skill
```

## Architecture

PromptStackBench is a Python CLI tool backed by SQLite. It loads task suites
and taxonomy specs from YAML, runs them through LLM providers, scores outputs
with a multi-dimensional evaluator pipeline, and generates comparison reports.

```
datasets/         Task suites (YAML)
specs/            Taxonomy specs (YAML)
src/              Python source
tests/            Test suite
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

## Taxonomy Layers

| Layer | What it controls | Best for |
|-------|-----------------|----------|
| Persona | Role, tone, style | Low-risk tasks where voice matters |
| Lens | Constrained viewpoint | Tasks needing a stable perspective |
| Skill | Procedure + output schema | Repeatable, reviewable tasks |
| Agent | Tools + state + multi-step | Tasks requiring search, tools, branching |
| Harness | Guards + retry + audit | Compliance, safety, production actions |

## Metrics

- **Final-answer:** correctness, completeness, clarity, relevance, hallucinated claims, schema validity
- **Robustness:** paraphrase stability, run variance
- **Operational:** tokens, latency, cost

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design
- [DECISIONS.md](DECISIONS.md) — design rationale
- [ROADMAP.md](ROADMAP.md) — phased delivery plan
- [SPEC.md](SPEC.md) — feature specification

## License

MIT
