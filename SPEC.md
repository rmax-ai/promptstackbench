# PromptStackBench — Specification

## Scope

PromptStackBench is a taxonomy evaluation harness that runs the same task
through five prompt/control abstractions — persona, lens, skill, agent,
harness — then compares outputs on correctness, clarity, stability, safety,
tool-use quality, cost, latency, and trace quality.

The goal is not to find the best prompt. The goal is to measure when a
lightweight role instruction stops being enough, when a task should become a
skill, when a skill needs tools/state, and when an agent requires
harness-level supervision.

## Features

### Core Runner
- Load task suites from YAML datasets
- Load taxonomy specs from YAML (persona, lens, skill, agent, harness)
- Generate prompt variants for each task × treatment combination
- Execute N repetitions and P paraphrase variants per combination
- Capture raw output, latency, token counts, and traces in SQLite
- Model-agnostic provider adapter

### Evaluator Pipeline
- Final-answer metrics: correctness, completeness, clarity, relevance
- Schema validity: output matches expected schema
- Factual grounding: hallucinated claims, unsupported assertions
- Instruction adherence: does the output follow the treatment's procedure
- Robustness: paraphrase stability, run-to-run variance
- (Phase 2) Trajectory quality: tool-call correctness, unnecessary calls
- (Phase 3) Safety: prompt-injection resistance, role drift

### Reports
- Markdown comparison report with per-treatment scores
- HTML report with sortable tables and treatment comparison
- Promotion signal: improvement_from_next_layer / added_operational_cost

### CLI
- `init` — scaffold a benchmark workspace
- `run` — execute a benchmark suite with configurable treatments
- `report` — generate comparison report from run data
- `promote` — compute promotion signal between two taxonomy layers

## Acceptance Criteria

### v0.1.0 — MVP (Static Prompt Comparison)

- [ ] AC-1: CLI `init` creates default directory structure with example specs
  and dataset
- [ ] AC-2: CLI `run --suite architecture_review --treatments
  persona,lens,skill --repetitions 3 --paraphrases 5` executes all
  combinations without error
- [ ] AC-3: Each run produces entries in SQLite (runs, tasks, treatments,
  outputs, scores tables)
- [ ] AC-4: Evaluator pipeline scores all outputs on: correctness,
  completeness, clarity, relevance, schema validity, hallucinated claims,
  instruction adherence
- [ ] AC-5: Robustness evaluator computes paraphrase stability score per
  treatment
- [ ] AC-6: CLI `report --run-id <id> --format html` produces a valid HTML
  report with treatment comparison table
- [ ] AC-7: CLI `promote --suite <suite> --from persona --to skill` reports
  whether skill outperforms persona enough to justify added structure
- [ ] AC-8: 3 task suites exist: architecture_review (7 tasks), explanation (6
  tasks), advisory (7 tasks) = 20 tasks total
- [ ] AC-9: All tests pass (unit + integration)
- [ ] AC-10: Lint and type-check clean

### v0.2.0 — Agent/Tool Evaluation

- [ ] AC-11: Agent runner executes tool-using tasks with mock tools
- [ ] AC-12: Trajectory evaluator scores tool-call correctness
- [ ] AC-13: Research synthesis and tool-use task suites exist

### v0.3.0 — Harness Evaluation

- [ ] AC-14: Harness runner applies guard policies and retry
- [ ] AC-15: Safety evaluator detects prompt injection and role drift
- [ ] AC-16: Full 5-treatment comparison report with promotion signals
