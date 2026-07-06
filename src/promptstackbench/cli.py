"""CLI entry point for PromptStackBench."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from promptstackbench import __version__
from promptstackbench.errors import PromptStackBenchError
from promptstackbench.evaluators.pipeline import evaluate_all
from promptstackbench.loaders.loader import (
    compute_spec_hash,
    generate_prompt,
    load_task_suite,
    load_treatment_specs,
)
from promptstackbench.reports.generator import build_report_data, write_report
from promptstackbench.runners.llm_runner import LLMProvider, MockProvider, run_single
from promptstackbench.schema.config import GlobalConfig
from promptstackbench.schema.run import Run
from promptstackbench.store.db import (
    get_outputs_for_run,
    get_scores_for_run,
    init_db,
    insert_output,
    insert_run,
    insert_score,
    insert_task,
    insert_treatment,
)

app = typer.Typer(no_args_is_help=True)
console = Console()
config = GlobalConfig()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version"),
):
    """PromptStackBench — taxonomy evaluation harness."""
    if version:
        console.print(f"PromptStackBench v{__version__}")
        raise typer.Exit()


@app.command()
def init(
    path: str = typer.Option(".", help="Target directory"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
):
    """Initialize a new PromptStackBench workspace."""
    root = Path(path).resolve()
    _create_dirs(root, force)
    _write_example_specs(root, force)
    _write_example_dataset(root, force)
    _write_config(root, force)
    console.print(f"[green]Initialized PromptStackBench workspace at {root}[/green]")
    console.print("Next steps:")
    console.print(f"  1. Set your API key in {root}/config.yaml")
    console.print(f"  2. Review specs in {root}/specs/")
    console.print(
        "  3. Run: promptstackbench run --suite architecture_review --treatments persona,lens,skill --mock"
    )


@app.command()
def run(
    suite: str = typer.Option(..., "--suite", "-s", help="Task suite ID to run"),
    model: str = typer.Option("gpt-4.1", "--model", "-m", help="Model to test"),
    treatments: str = typer.Option(
        "persona,lens,skill", "--treatments", "-t", help="Comma-separated treatments"
    ),
    repetitions: int = typer.Option(
        3, "--repetitions", "-r", help="Repetitions per variant"
    ),
    paraphrases: int = typer.Option(
        5, "--paraphrases", "-p", help="Paraphrase variants"
    ),
    mock: bool = typer.Option(False, "--mock", help="Use mock provider (no API calls)"),
    api_key: str = typer.Option(
        "", "--api-key", envvar="OPENAI_API_KEY", help="API key"
    ),
    data_dir: str = typer.Option("datasets", help="Datasets directory"),
    specs_dir: str = typer.Option("specs", help="Specs directory"),
    traces_dir: str = typer.Option("traces", help="Traces directory"),
):
    """Run a benchmark suite."""
    data_path = Path(data_dir)
    specs_path = Path(specs_dir)
    traces_path = Path(traces_dir)

    # Load task suite
    suite_file = data_path / f"{suite}.yaml"
    if not suite_file.exists():
        console.print(f"[red]Suite not found: {suite_file}[/red]")
        raise typer.Exit(1)

    task_suite = load_task_suite(suite_file)
    console.print(f"Loaded suite: {task_suite.name} ({len(task_suite.tasks)} tasks)")

    # Load treatment specs
    all_specs = load_treatment_specs(specs_path)
    treatment_list = [t.strip() for t in treatments.split(",")]
    selected_specs = []
    for ttype in treatment_list:
        specs = all_specs.get(ttype, [])
        if specs:
            selected_specs.extend(specs)
        else:
            console.print(
                f"[yellow]Warning: no specs found for treatment type '{ttype}'[/yellow]"
            )

    if not selected_specs:
        console.print(
            "[red]No treatment specs loaded. Run 'promptstackbench init' first.[/red]"
        )
        raise typer.Exit(1)

    console.print(f"Treatments: {len(selected_specs)} specs across {treatment_list}")

    # Init DB
    traces_path.mkdir(parents=True, exist_ok=True)
    db_path = traces_path / "runs.sqlite"
    conn = init_db(db_path)

    # Create run record
    run_record = Run(suite_id=suite, model=model)
    insert_run(conn, run_record)
    run_id = run_record.id
    console.print(f"Run ID: {run_id}")

    # Init provider
    if mock:
        provider = MockProvider()
        judge_provider = MockProvider()
        console.print("[yellow]Using mock provider — no real API calls[/yellow]")
    else:
        key = api_key or config.api_key
        if not key:
            console.print("[red]No API key. Set OPENAI_API_KEY or --api-key.[/red]")
            raise typer.Exit(1)
        provider = LLMProvider(
            api_key=key, base_url=config.api_base_url, timeout=config.request_timeout
        )
        judge_provider = provider

    # Insert tasks
    for task in task_suite.tasks:
        import json

        insert_task(
            conn,
            task.id,
            suite,
            task.task_class.value,
            task.input,
            json.dumps(task.expected_properties),
        )

    # Insert treatments
    for spec in selected_specs:
        insert_treatment(conn, spec.id, spec.type, "", compute_spec_hash(spec))

    # Run all combinations
    total = len(selected_specs) * len(task_suite.tasks) * repetitions * paraphrases
    console.print(f"Running {total} evaluations...")
    count = 0
    errors = 0

    for spec in selected_specs:
        for task in task_suite.tasks:
            prompt = generate_prompt(task, spec)
            for rep in range(repetitions):
                for para in range(paraphrases):
                    try:
                        output = run_single(
                            provider=provider,
                            prompt=prompt,
                            model=model,
                            run_id=run_id,
                            task_id=task.id,
                            treatment_id=spec.id,
                            treatment_type=spec.type,
                            paraphrase_index=para,
                            repetition_index=rep,
                        )
                        output_id = insert_output(conn, output)
                        output.id = str(output_id)

                        # Evaluate
                        scores = evaluate_all(
                            output=output,
                            task_properties={
                                "input": task.input,
                                "expected_properties": task.expected_properties,
                            },
                            provider=judge_provider,
                            judge_model=config.judge_model,
                        )
                        for score in scores:
                            insert_score(conn, score)

                        count += 1
                        if count % 10 == 0:
                            console.print(f"  {count}/{total} complete...")
                    except PromptStackBenchError as e:
                        errors += 1
                        console.print(
                            f"[red]Error on {task.id}/{spec.id} r{rep}p{para}: {e}[/red]"
                        )

    conn.close()
    console.print(
        f"\n[green]Run complete: {count} evaluations, {errors} errors[/green]"
    )
    console.print(f"Run ID: {run_id}")
    console.print(
        f"Generate report: promptstackbench report --run-id {run_id} --format html"
    )


@app.command()
def report(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to report on"),
    fmt: str = typer.Option("html", "--format", "-f", help="Output format: html or md"),
    output: str = typer.Option("", "--output", "-o", help="Output path"),
    traces_dir: str = typer.Option("traces", help="Traces directory"),
):
    """Generate a comparison report from a run."""
    db_path = Path(traces_dir) / "runs.sqlite"
    if not db_path.exists():
        console.print(f"[red]No database found at {db_path}[/red]")
        raise typer.Exit(1)

    conn = init_db(db_path)
    scores = get_scores_for_run(conn, run_id)
    outputs = get_outputs_for_run(conn, run_id)
    conn.close()

    if not scores:
        console.print(f"[red]No scores found for run {run_id}[/red]")
        raise typer.Exit(1)

    data = build_report_data(run_id, "", "", scores, outputs)
    out_path = Path(output) if output else Path(f"report_{run_id}")
    result = write_report(data, out_path, fmt)
    console.print(f"[green]Report written to {result}[/green]")


@app.command()
def promote(
    suite: str = typer.Option(..., "--suite", "-s", help="Task suite ID"),
    from_: str = typer.Option(..., "--from", help="Source treatment type"),
    to: str = typer.Option(..., "--to", help="Target treatment type"),
    traces_dir: str = typer.Option("traces", help="Traces directory"),
):
    """Check whether one treatment type outperforms another enough to justify promotion."""
    db_path = Path(traces_dir) / "runs.sqlite"
    if not db_path.exists():
        console.print(f"[red]No database found at {db_path}[/red]")
        raise typer.Exit(1)

    conn = init_db(db_path)

    # Find the most recent run for this suite
    row = conn.execute(
        "SELECT id FROM runs WHERE suite_id = ? ORDER BY started_at DESC LIMIT 1",
        (suite,),
    ).fetchone()
    if not row:
        console.print(f"[red]No runs found for suite '{suite}'[/red]")
        conn.close()
        raise typer.Exit(1)

    run_id = row[0]
    scores = get_scores_for_run(conn, run_id)
    outputs = get_outputs_for_run(conn, run_id)
    conn.close()

    # Filter by treatment type
    from_scores = [s["score"] for s in scores if s["treatment_type"] == from_]
    to_scores = [s["score"] for s in scores if s["treatment_type"] == to]

    from_costs = [o["cost_estimate"] for o in outputs if o["treatment_type"] == from_]
    to_costs = [o["cost_estimate"] for o in outputs if o["treatment_type"] == to]

    from_mean = sum(from_scores) / len(from_scores) if from_scores else 0
    to_mean = sum(to_scores) / len(to_scores) if to_scores else 0
    from_cost = sum(from_costs) / len(from_costs) if from_costs else 0
    to_cost = sum(to_costs) / len(to_costs) if to_costs else 0

    improvement = to_mean - from_mean
    improvement_pct = (improvement / from_mean * 100) if from_mean > 0 else 0
    cost_increase = to_cost - from_cost
    cost_increase_pct = (cost_increase / from_cost * 100) if from_cost > 0 else 0
    signal = improvement / cost_increase if cost_increase > 0 else improvement

    table = Table(title=f"Promotion: {from_} → {to}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row(f"Mean score ({from_})", f"{from_mean:.2f}")
    table.add_row(f"Mean score ({to})", f"{to_mean:.2f}")
    table.add_row("Quality improvement", f"{improvement_pct:.1f}%")
    table.add_row("Cost increase", f"{cost_increase_pct:.1f}%")
    table.add_row("Promotion signal", f"{signal:.4f}")
    console.print(table)

    if signal > 0.5:
        console.print(f"[green]✓ Promotion from {from_} to {to} is justified[/green]")
    elif signal > 0:
        console.print(
            f"[yellow]Marginal: promotion from {from_} to {to} may not justify cost[/yellow]"
        )
    else:
        console.print(f"[red]✗ Promotion from {from_} to {to} is not justified[/red]")


def _create_dirs(root: Path, force: bool) -> None:
    """Create workspace directories."""
    dirs = [
        "datasets",
        "specs/personas",
        "specs/lenses",
        "specs/skills",
        "specs/agents",
        "specs/harnesses",
        "traces",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)


def _write_example_specs(root: Path, force: bool) -> None:
    """Write example treatment specs."""
    import yaml

    persona = {
        "id": "senior_architect_persona",
        "type": "persona",
        "role": "senior software architect",
        "style": {
            "tone": "direct",
            "depth": "high",
            "audience": "experienced engineers",
        },
    }
    path = root / "specs" / "personas" / "senior_architect.yaml"
    if force or not path.exists():
        path.write_text(yaml.dump(persona, default_flow_style=False, sort_keys=False))

    lens = {
        "id": "production_readiness_lens",
        "type": "lens",
        "viewpoint": "production-readiness reviewer",
        "focus": [
            "failure modes",
            "hidden coupling",
            "observability",
            "rollback",
            "cost",
        ],
        "avoid": ["rewriting the design", "inventing requirements"],
    }
    path = root / "specs" / "lenses" / "production_readiness.yaml"
    if force or not path.exists():
        path.write_text(yaml.dump(lens, default_flow_style=False, sort_keys=False))

    skill = {
        "id": "architecture_review_skill",
        "type": "skill",
        "goal": "assess whether a design is production-ready",
        "inputs": ["design_doc", "constraints", "target_scale"],
        "procedure": [
            "extract explicit assumptions",
            "identify hidden coupling",
            "inspect security, observability, rollback, cost",
            "identify blocking issues",
            "recommend smallest safe next step",
        ],
        "output_schema": {
            "verdict": "string",
            "blocking_issues": "list",
            "non_blocking_concerns": "list",
            "recommended_sequence": "list",
            "open_questions": "list",
        },
        "checks": [
            "every blocking issue must cite input evidence",
            "do not invent requirements",
        ],
    }
    path = root / "specs" / "skills" / "architecture_review.yaml"
    if force or not path.exists():
        path.write_text(yaml.dump(skill, default_flow_style=False, sort_keys=False))


def _write_example_dataset(root: Path, force: bool) -> None:
    """Write an example task suite."""
    import yaml

    suite = {
        "id": "architecture_review",
        "name": "Architecture Review Tasks",
        "description": "Tasks that require reviewing a system design for production readiness.",
        "task_class": "architecture_review",
        "tasks": [
            {
                "id": "arch_review_001",
                "suite_id": "architecture_review",
                "task_class": "architecture_review",
                "input": "Review this architecture: A team reads Slack messages to trigger operational workflows. Evaluate whether this is a sound architecture for a business automation system.",
                "expected_properties": {
                    "required_keys": [
                        "event bus",
                        "coupling",
                        "failure mode",
                        "source of truth",
                    ],
                    "forbidden_patterns": ["perfectly fine", "no issues"],
                },
            },
            {
                "id": "arch_review_002",
                "suite_id": "architecture_review",
                "task_class": "architecture_review",
                "input": "Review this design: A single PostgreSQL instance handles all reads, writes, analytics queries, and audit logging for a payment processing system with 10K TPS.",
                "expected_properties": {
                    "required_keys": [
                        "read replica",
                        "caching",
                        "separation",
                        "bottleneck",
                    ],
                },
            },
        ],
    }
    path = root / "datasets" / "architecture_review.yaml"
    if force or not path.exists():
        path.write_text(yaml.dump(suite, default_flow_style=False, sort_keys=False))


def _write_config(root: Path, force: bool) -> None:
    """Write default config.yaml."""
    import yaml

    cfg = {
        "default_model": "gpt-4.1",
        "default_provider": "openai",
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "",
        "judge_model": "gpt-4.1",
        "judge_temperature": 0.0,
        "max_retries": 3,
        "request_timeout": 120,
    }
    path = root / "config.yaml"
    if force or not path.exists():
        path.write_text(yaml.dump(cfg, default_flow_style=False, sort_keys=False))
