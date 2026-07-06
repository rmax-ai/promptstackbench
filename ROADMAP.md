# Roadmap

## v0.1.0 — MVP: Static Prompt Comparison

Phase 1 of the benchmark — persona, lens, and skill treatments only.

- [x] Core schema models (taxonomy specs, task definitions, data model)
- [ ] Task loading from YAML datasets
- [ ] LLM runner with provider adapter
- [ ] CLI: `init`, `run`, `report`
- [ ] Evaluators: final-answer (correctness, completeness, clarity, relevance),
  schema validity, hallucinated claims, instruction adherence
- [ ] Robustness: paraphrase stability
- [ ] Markdown and HTML comparison reports
- [ ] 3 task suites: architectural review, conceptual explanation, advisory
- [ ] 20 tasks total across suites

## v0.2.0 — Agent/Tool Evaluation

Phase 2 — add agent specs with tools: web/file retrieval, calculator, local
document search.

- [ ] Agent runner with tool execution
- [ ] Task suites: research synthesis, document-grounded QA, tool-use planning
- [ ] Evaluators: correct tool choice, unnecessary tool calls, evidence grounding,
  trajectory quality
- [ ] Agent-specific metrics in reports

## v0.3.0 — Harness Evaluation

Phase 3 — add harness behaviors: retry, critic pass, schema repair,
prompt-injection check, tool-permission check, trace scoring.

- [ ] Harness runner with guard and recovery policies
- [ ] Task suites: adversarial retrieval, malformed tool results, ambiguous
  requests, conflicting sources
- [ ] Evaluators: recovery rate, safety violations, trace completeness,
  auditability, cost increase
- [ ] Full promotion signal computation across all 5 layers

## Future

- [ ] Multi-provider support (Anthropic, Google, local models)
- [ ] Parallel task execution with asyncio
- [ ] Web dashboard for run history and comparison
- [ ] Export to LangSmith / W&B for hosted eval tracking
- [ ] Human-in-the-loop calibration for LLM-as-judge scores
- [ ] CI integration — run benchmark on PR to agent platform
