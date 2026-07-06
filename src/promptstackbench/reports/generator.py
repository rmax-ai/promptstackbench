"""Markdown and HTML report generation."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Any

from jinja2 import Template

MARKDOWN_TEMPLATE = """# PromptStackBench Report
**Run ID:** {{ run_id }}
**Suite:** {{ suite_id }}
**Model:** {{ model }}
**Generated:** {{ generated_at }}

---

## Summary

{% for treatment in treatments %}
### {{ treatment.type }}: {{ treatment.id }}

| Metric | Mean Score |
|--------|------------|
{% for metric_name, mean_score in treatment.metrics.items() %}
| {{ metric_name }} | {{ "%.2f"|format(mean_score) }} |
{% endfor %}

**Avg tokens:** {{ treatment.avg_tokens }} | **Avg latency:** {{ treatment.avg_latency_ms }}ms | **Avg cost:** ${{ "%.4f"|format(treatment.avg_cost) }}

{% endfor %}

---

## Promotion Signals

| From | To | Quality Δ | Cost Δ | Signal |
|------|----|-----------|--------|--------|
{% for signal in promotion_signals %}
| {{ signal.from_type }} | {{ signal.to_type }} | {{ "%.1f"|format(signal.improvement_pct) }}% | {{ "%.1f"|format(signal.cost_increase_pct) }}% | {{ "%.3f"|format(signal.promotion_signal) }} |
{% endfor %}

---

## Per-Task Scores

{% for task in tasks %}
### {{ task.id }}

| Treatment | Mean Score | Paraphrase Stability | Run Variance |
|-----------|------------|---------------------|--------------|
{% for tr in task.treatments %}
| {{ tr.type }} | {{ "%.2f"|format(tr.mean_score) }} | {{ "%.2f"|format(tr.paraphrase_stability) }} | {{ "%.2f"|format(tr.run_variance) }} |
{% endfor %}

{% endfor %}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PromptStackBench Report — {{ run_id }}</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem; background: #0d1117; color: #c9d1d9; }
  h1, h2, h3 { color: #58a6ff; }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
  th, td { padding: 0.5rem 0.75rem; text-align: left; border: 1px solid #30363d; }
  th { background: #161b22; }
  tr:nth-child(even) { background: #161b22; }
  .good { color: #3fb950; }
  .bad { color: #f85149; }
  .neutral { color: #d2991d; }
</style>
</head>
<body>
<h1>PromptStackBench Report</h1>
<p><strong>Run ID:</strong> {{ run_id }} | <strong>Suite:</strong> {{ suite_id }} | <strong>Model:</strong> {{ model }}</p>

<h2>Summary</h2>
{% for treatment in treatments %}
<h3>{{ treatment.type }}: {{ treatment.id }}</h3>
<table>
<tr><th>Metric</th><th>Mean Score</th></tr>
{% for metric_name, mean_score in treatment.metrics.items() %}
<tr><td>{{ metric_name }}</td><td class="{% if mean_score >= 8 %}good{% elif mean_score >= 5 %}neutral{% else %}bad{% endif %}">{{ "%.2f"|format(mean_score) }}</td></tr>
{% endfor %}
</table>
<p>Avg tokens: {{ treatment.avg_tokens }} | Avg latency: {{ treatment.avg_latency_ms }}ms | Avg cost: ${{ "%.4f"|format(treatment.avg_cost) }}</p>
{% endfor %}

<h2>Promotion Signals</h2>
<table>
<tr><th>From</th><th>To</th><th>Quality Δ</th><th>Cost Δ</th><th>Signal</th></tr>
{% for signal in promotion_signals %}
<tr><td>{{ signal.from_type }}</td><td>{{ signal.to_type }}</td><td class="{% if signal.improvement_pct > 0 %}good{% else %}bad{% endif %}">{{ "%.1f"|format(signal.improvement_pct) }}%</td><td>{{ "%.1f"|format(signal.cost_increase_pct) }}%</td><td>{{ "%.3f"|format(signal.promotion_signal) }}</td></tr>
{% endfor %}
</table>

<h2>Per-Task Scores</h2>
{% for task in tasks %}
<h3>{{ task.id }}</h3>
<table>
<tr><th>Treatment</th><th>Mean Score</th><th>Paraphrase Stability</th><th>Run Variance</th></tr>
{% for tr in task.treatments %}
<tr><td>{{ tr.type }}</td><td class="{% if tr.mean_score >= 8 %}good{% elif tr.mean_score >= 5 %}neutral{% else %}bad{% endif %}">{{ "%.2f"|format(tr.mean_score) }}</td><td>{{ "%.2f"|format(tr.paraphrase_stability) }}</td><td>{{ "%.2f"|format(tr.run_variance) }}</td></tr>
{% endfor %}
</table>
{% endfor %}

<p><small>Generated: {{ generated_at }}</small></p>
</body>
</html>"""


def build_report_data(
    run_id: str,
    suite_id: str,
    model: str,
    scores: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the structured report data from raw scores and outputs."""
    from collections import defaultdict
    from datetime import UTC, datetime

    # Group scores by treatment + metric
    treatment_metrics: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    treatment_costs: dict[str, list[float]] = defaultdict(list)
    treatment_tokens: dict[str, list[int]] = defaultdict(list)
    treatment_latencies: dict[str, list[int]] = defaultdict(list)

    for s in scores:
        key = f"{s['treatment_type']}:{s['treatment_id']}"
        treatment_metrics[key][s["metric"]].append(s["score"])

    for o in outputs:
        key = f"{o['treatment_type']}:{o['treatment_id']}"
        treatment_costs[key].append(o["cost_estimate"])
        treatment_tokens[key].append(o["token_input"] + o["token_output"])
        treatment_latencies[key].append(o["latency_ms"])

    treatments = []
    for key in sorted(treatment_metrics):
        ttype, tid = key.split(":", 1)
        metrics = {m: sum(v) / len(v) for m, v in treatment_metrics[key].items()}
        costs = treatment_costs.get(key, [0.0])
        tokens = treatment_tokens.get(key, [0])
        latencies = treatment_latencies.get(key, [0])
        treatments.append(
            {
                "type": ttype,
                "id": tid,
                "metrics": metrics,
                "avg_cost": sum(costs) / len(costs),
                "avg_tokens": int(sum(tokens) / len(tokens)),
                "avg_latency_ms": int(sum(latencies) / len(latencies)),
            }
        )

    # Per-task scores with real stability/variance
    task_scores: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    # Group scores by task + treatment + paraphrase for stability
    task_tr_para: dict[str, dict[str, dict[int, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    # Group scores by task + treatment + repetition for variance
    task_tr_rep: dict[str, dict[str, dict[int, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for s in scores:
        task_key = s["task_id"]
        tr_key = s["treatment_type"]
        task_scores[task_key][tr_key].append(s["score"])
        task_tr_para[task_key][tr_key][s.get("paraphrase_index", 0)].append(s["score"])
        task_tr_rep[task_key][tr_key][s.get("repetition_index", 0)].append(s["score"])

    tasks = []
    for task_id in sorted(task_scores):
        tr_list = []
        for tr_type in sorted(task_scores[task_id]):
            vals = task_scores[task_id][tr_type]

            # Compute paraphrase stability
            para_scores = task_tr_para[task_id][tr_type]
            para_means = [
                sum(pl) / len(pl) for pl in para_scores.values() if pl
            ]
            if len(para_means) >= 2:
                import statistics
                para_std = statistics.stdev(para_means)
                stability = max(0.0, 10.0 - (para_std * 2))
            else:
                stability = 10.0

            # Compute run variance
            rep_scores = task_tr_rep[task_id][tr_type]
            rep_means = [
                sum(rl) / len(rl) for rl in rep_scores.values() if rl
            ]
            if len(rep_means) >= 2:
                import statistics
                rep_std = statistics.stdev(rep_means)
                variance = max(0.0, 10.0 - (rep_std * 2))
            else:
                variance = 10.0

            tr_list.append(
                {
                    "type": tr_type,
                    "mean_score": sum(vals) / len(vals),
                    "paraphrase_stability": round(stability, 2),
                    "run_variance": round(variance, 2),
                }
            )
        tasks.append({"id": task_id, "treatments": tr_list})

    # Promotion signals
    promotion_signals = _compute_all_promotions(treatments)

    return {
        "run_id": run_id,
        "suite_id": suite_id,
        "model": model,
        "generated_at": datetime.now(UTC).isoformat(),
        "treatments": treatments,
        "tasks": tasks,
        "promotion_signals": promotion_signals,
    }


def _compute_all_promotions(treatments: list[dict]) -> list[dict]:
    """Compute promotion signals between adjacent treatment types."""
    order = ["persona", "lens", "skill", "agent", "harness"]
    tr_map = {t["type"]: t for t in treatments}
    signals = []
    for i in range(len(order) - 1):
        fr = order[i]
        to = order[i + 1]
        if fr in tr_map and to in tr_map:
            fr_metrics = tr_map[fr]["metrics"]
            to_metrics = tr_map[to]["metrics"]
            fr_vals = list(fr_metrics.values()) if fr_metrics else [5.0]
            to_vals = list(to_metrics.values()) if to_metrics else [5.0]
            fr_mean = sum(fr_vals) / len(fr_vals)
            to_mean = sum(to_vals) / len(to_vals)
            fr_cost = tr_map[fr]["avg_cost"]
            to_cost = tr_map[to]["avg_cost"]
            improvement = to_mean - fr_mean
            improvement_pct = (improvement / fr_mean) * 100 if fr_mean > 0 else 0.0
            cost_increase = to_cost - fr_cost
            cost_increase_pct = (cost_increase / fr_cost) * 100 if fr_cost > 0 else 0.0
            signal = improvement / cost_increase if cost_increase > 0 else improvement
            signals.append(
                {
                    "from_type": fr,
                    "to_type": to,
                    "improvement_pct": round(improvement_pct, 2),
                    "cost_increase_pct": round(cost_increase_pct, 2),
                    "promotion_signal": round(signal, 4),
                }
            )
    return signals


def render_markdown(data: dict[str, Any]) -> str:
    """Render report data as Markdown."""
    return Template(MARKDOWN_TEMPLATE).render(**data)


def render_html(data: dict[str, Any]) -> str:
    """Render report data as HTML."""
    return Template(HTML_TEMPLATE).render(**data)


def write_report(data: dict[str, Any], output_path: Path, fmt: str = "html") -> Path:
    """Write a report to disk."""
    if fmt == "html":
        content = render_html(data)
        path = output_path.with_suffix(".html")
    else:
        content = render_markdown(data)
        path = output_path.with_suffix(".md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path
