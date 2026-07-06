"""Unit tests for evaluator pipeline."""

from promptstackbench.evaluators.pipeline import (
    _evaluate_schema,
    compute_paraphrase_stability,
    compute_promotion_signal,
    compute_run_variance,
)
from promptstackbench.schema.run import Output, Score


def test_evaluate_schema_all_present():
    output = Output(
        run_id="r1",
        task_id="t1",
        treatment_id="tr1",
        treatment_type="persona",
        raw_output="The system needs an event bus, read replica, and better caching.",
    )
    task_props = {
        "expected_properties": {
            "required_keys": ["event bus", "read replica", "caching"],
        },
    }
    score = _evaluate_schema(output, task_props, "0.1.0")
    assert score.metric == "schema_validity"
    assert score.score == 10.0


def test_evaluate_schema_missing_keys():
    output = Output(
        run_id="r1",
        task_id="t1",
        treatment_id="tr1",
        treatment_type="persona",
        raw_output="The system is basically fine as-is.",
    )
    task_props = {
        "expected_properties": {
            "required_keys": ["event bus", "read replica", "caching"],
        },
    }
    score = _evaluate_schema(output, task_props, "0.1.0")
    assert score.score < 10.0


def test_evaluate_schema_forbidden_patterns():
    output = Output(
        run_id="r1",
        task_id="t1",
        treatment_id="tr1",
        treatment_type="persona",
        raw_output="This architecture has no issues and is perfectly fine.",
    )
    task_props = {
        "expected_properties": {
            "forbidden_patterns": ["no issues", "perfectly fine"],
        },
    }
    score = _evaluate_schema(output, task_props, "0.1.0")
    assert score.score < 10.0


def test_evaluate_schema_empty_props():
    output = Output(
        run_id="r1",
        task_id="t1",
        treatment_id="tr1",
        treatment_type="persona",
        raw_output="Anything goes.",
    )
    score = _evaluate_schema(output, {}, "0.1.0")
    assert score.score == 10.0


def test_paraphrase_stability_identical():
    scores = {
        0: [Score(metric="m", score=8.0)],
        1: [Score(metric="m", score=8.0)],
        2: [Score(metric="m", score=8.0)],
    }
    stability = compute_paraphrase_stability(scores)
    assert stability >= 9.9


def test_paraphrase_stability_different():
    scores = {
        0: [Score(metric="m", score=3.0)],
        1: [Score(metric="m", score=7.0)],
        2: [Score(metric="m", score=9.0)],
    }
    stability = compute_paraphrase_stability(scores)
    assert stability < 8.0


def test_promotion_signal_good():
    signal = compute_promotion_signal(
        from_scores=[5.0, 5.0, 5.0],
        to_scores=[8.0, 8.0, 8.0],
        from_cost=0.01,
        to_cost=0.02,
    )
    assert signal["improvement_pct"] > 50
    assert signal["promotion_signal"] > 0


def test_promotion_signal_bad():
    signal = compute_promotion_signal(
        from_scores=[5.0, 5.0, 5.0],
        to_scores=[5.1, 5.1, 5.1],
        from_cost=0.01,
        to_cost=2.00,
    )
    assert signal["improvement_pct"] < 5
    assert signal["promotion_signal"] < 0.1


def test_run_variance_stable():
    scores = {
        0: [Score(metric="m", score=7.0)],
        1: [Score(metric="m", score=7.0)],
        2: [Score(metric="m", score=7.0)],
    }
    var = compute_run_variance(scores)
    assert var >= 9.9
