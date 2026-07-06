"""Evaluator pipeline — scores outputs on multiple dimensions."""

from __future__ import annotations

from typing import Any

from promptstackbench.schema.run import Output, Score


def evaluate_all(
    output: Output,
    task_properties: dict[str, Any],
    provider: Any,  # LLMProvider or MockProvider
    judge_model: str,
    evaluator_version: str = "0.1.0",
) -> list[Score]:
    """Run all Phase 1 evaluators on an output.

    Returns a list of Score objects.
    """
    scores: list[Score] = []
    output_id = output.id or ""

    # Final-answer quality scores (via judge)
    quality_scores = _evaluate_quality(
        output, task_properties, provider, judge_model, evaluator_version
    )
    for s in quality_scores:
        s.output_id = output_id
        scores.append(s)

    # Schema validity (structural, no LLM needed)
    schema_score = _evaluate_schema(output, task_properties, evaluator_version)
    schema_score.output_id = output_id
    scores.append(schema_score)

    # Hallucination check (via judge)
    grounding_score = _evaluate_grounding(
        output, task_properties, provider, judge_model, evaluator_version
    )
    grounding_score.output_id = output_id
    scores.append(grounding_score)

    # Instruction adherence (via judge)
    adherence_score = _evaluate_adherence(
        output, task_properties, provider, judge_model, evaluator_version
    )
    adherence_score.output_id = output_id
    scores.append(adherence_score)

    return scores


def _evaluate_quality(
    output: Output,
    task_properties: dict[str, Any],
    provider: Any,
    judge_model: str,
    version: str,
) -> list[Score]:
    """Evaluate final-answer quality: correctness, completeness, clarity, relevance."""
    prompt = (
        "You are evaluating an AI's response to a task. Score on 1-10 for each dimension:\n"
        f"Task: {task_properties.get('input', '')}\n"
        f"Response: {output.raw_output[:2000]}\n\n"
        "Score these dimensions (1=worst, 10=best):\n"
        "1. Correctness: Does the answer solve the task correctly?\n"
        "2. Completeness: Does it cover all necessary aspects?\n"
        "3. Clarity: Is the response clear and well-structured?\n"
        "4. Relevance: Is every part relevant to the task?\n\n"
        "Output format:\n"
        "correctness: <score>\n"
        "completeness: <score>\n"
        "clarity: <score>\n"
        "relevance: <score>\n"
    )
    try:
        text, _, _ = provider.complete(prompt, judge_model, temperature=0.0)
    except Exception:
        text = "correctness: 5\ncompleteness: 5\nclarity: 5\nrelevance: 5"

    parsed = _parse_score_lines(text)
    return [
        Score(
            metric="correctness",
            score=parsed.get("correctness", 5.0),
            rationale="",
            evaluator_model=judge_model,
            evaluator_version=version,
        ),
        Score(
            metric="completeness",
            score=parsed.get("completeness", 5.0),
            rationale="",
            evaluator_model=judge_model,
            evaluator_version=version,
        ),
        Score(
            metric="clarity",
            score=parsed.get("clarity", 5.0),
            rationale="",
            evaluator_model=judge_model,
            evaluator_version=version,
        ),
        Score(
            metric="relevance",
            score=parsed.get("relevance", 5.0),
            rationale="",
            evaluator_model=judge_model,
            evaluator_version=version,
        ),
    ]


def _evaluate_schema(
    output: Output,
    task_properties: dict[str, Any],
    version: str,
) -> Score:
    """Check if the output contains expected structural elements."""
    expected = task_properties.get("expected_properties", {})
    if not expected:
        return Score(
            metric="schema_validity",
            score=10.0,
            rationale="No schema expected.",
            evaluator_version=version,
        )

    required_keys = expected.get("required_keys", [])
    forbidden_patterns = expected.get("forbidden_patterns", [])

    score = 10.0
    issues: list[str] = []

    for key in required_keys:
        if key.lower() not in output.raw_output.lower():
            score -= 2.0
            issues.append(f"Missing key: {key}")

    for pattern in forbidden_patterns:
        if pattern.lower() in output.raw_output.lower():
            score -= 2.0
            issues.append(f"Forbidden pattern found: {pattern}")

    score = max(0.0, score)
    return Score(
        metric="schema_validity",
        score=score,
        rationale="; ".join(issues) if issues else "All schema checks passed.",
        evaluator_version=version,
    )


def _evaluate_grounding(
    output: Output,
    task_properties: dict[str, Any],
    provider: Any,
    judge_model: str,
    version: str,
) -> Score:
    """Evaluate factual grounding — does the output invent claims?"""
    prompt = (
        "Evaluate whether this AI response makes unsupported or hallucinated claims.\n"
        f"Task: {task_properties.get('input', '')}\n"
        f"Response: {output.raw_output[:2000]}\n\n"
        "Score 1-10: 10 = no hallucinations, all claims grounded. 1 = mostly fabricated.\n"
        "Output ONLY: hallucination_score: <score>\n"
    )
    try:
        text, _, _ = provider.complete(prompt, judge_model, temperature=0.0)
    except Exception:
        text = "hallucination_score: 7"
    parsed = _parse_score_lines(text)
    return Score(
        metric="hallucination_score",
        score=parsed.get("hallucination_score", 7.0),
        rationale="",
        evaluator_model=judge_model,
        evaluator_version=version,
    )


def _evaluate_adherence(
    output: Output,
    task_properties: dict[str, Any],
    provider: Any,
    judge_model: str,
    version: str,
) -> Score:
    """Evaluate instruction adherence — does the output follow the task instructions?"""
    prompt = (
        "Evaluate whether this AI response follows the task instructions precisely.\n"
        f"Task instructions: {task_properties.get('input', '')}\n"
        f"Response: {output.raw_output[:2000]}\n\n"
        "Score 1-10: 10 = perfectly followed all instructions. 1 = completely ignored.\n"
        "Output ONLY: instruction_adherence: <score>\n"
    )
    try:
        text, _, _ = provider.complete(prompt, judge_model, temperature=0.0)
    except Exception:
        text = "instruction_adherence: 7"
    parsed = _parse_score_lines(text)
    return Score(
        metric="instruction_adherence",
        score=parsed.get("instruction_adherence", 7.0),
        rationale="",
        evaluator_model=judge_model,
        evaluator_version=version,
    )


def _parse_score_lines(text: str) -> dict[str, float]:
    """Parse key: value lines into a float dict."""
    result: dict[str, float] = {}
    for line in text.split("\n"):
        line = line.strip().lower()
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().split()[0]  # take first token
            try:
                result[key.strip()] = float(val)
            except ValueError:
                continue
    return result


def compute_paraphrase_stability(
    scores_by_paraphrase: dict[int, list[Score]],
) -> float:
    """Compute stability score across paraphrases.

    Stability = 10 - (std_dev_of_mean_scores * 2), clamped to [0, 10].
    """
    import statistics

    mean_scores: list[float] = []
    for p_idx in sorted(scores_by_paraphrase):
        score_list = scores_by_paraphrase[p_idx]
        if score_list:
            mean_scores.append(sum(s.score for s in score_list) / len(score_list))

    if len(mean_scores) < 2:
        return 10.0

    std_dev = statistics.stdev(mean_scores) if len(mean_scores) > 1 else 0.0
    return max(0.0, 10.0 - (std_dev * 2))


def compute_run_variance(scores_by_repetition: dict[int, list[Score]]) -> float:
    """Compute variance across repetitions.

    Variance = 10 - (std_dev_of_mean_scores * 2), clamped to [0, 10].
    """
    import statistics

    mean_scores: list[float] = []
    for r_idx in sorted(scores_by_repetition):
        score_list = scores_by_repetition[r_idx]
        if score_list:
            mean_scores.append(sum(s.score for s in score_list) / len(score_list))

    if len(mean_scores) < 2:
        return 10.0

    std_dev = statistics.stdev(mean_scores) if len(mean_scores) > 1 else 0.0
    return max(0.0, 10.0 - (std_dev * 2))


def compute_promotion_signal(
    from_scores: list[float],
    to_scores: list[float],
    from_cost: float,
    to_cost: float,
) -> dict[str, float]:
    """Compute the promotion signal: improvement / added_cost.

    Returns dict with improvement_pct, cost_increase_pct, and promotion_signal.
    """
    from_mean = sum(from_scores) / len(from_scores) if from_scores else 5.0
    to_mean = sum(to_scores) / len(to_scores) if to_scores else 5.0
    improvement = to_mean - from_mean
    improvement_pct = (improvement / from_mean) * 100 if from_mean > 0 else 0.0
    cost_increase = to_cost - from_cost
    cost_increase_pct = (cost_increase / from_cost) * 100 if from_cost > 0 else 0.0
    signal = improvement / cost_increase if cost_increase > 0 else improvement
    return {
        "improvement_pct": round(improvement_pct, 2),
        "cost_increase_pct": round(cost_increase_pct, 2),
        "promotion_signal": round(signal, 4),
    }
