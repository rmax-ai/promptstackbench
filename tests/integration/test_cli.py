"""Integration tests for the CLI."""


from typer.testing import CliRunner

from promptstackbench.cli import app

runner = CliRunner()


def test_init_creates_structure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "datasets").exists()
    assert (tmp_path / "specs" / "personas").exists()
    assert (tmp_path / "specs" / "skills").exists()
    assert (tmp_path / "traces").exists()
    assert (tmp_path / "config.yaml").exists()


def test_run_with_mock(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # First init
    result = runner.invoke(app, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Then run with mock
    result = runner.invoke(
        app,
        [
            "run",
            "--suite",
            "architecture_review",
            "--treatments",
            "persona,skill",
            "--repetitions",
            "1",
            "--paraphrases",
            "1",
            "--mock",
            "--data-dir",
            str(tmp_path / "datasets"),
            "--specs-dir",
            str(tmp_path / "specs"),
            "--traces-dir",
            str(tmp_path / "traces"),
        ],
    )
    assert result.exit_code == 0
    assert "Run complete" in result.stdout
    assert "Run ID:" in result.stdout


def test_report_after_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Init and run
    runner.invoke(app, ["init", "--path", str(tmp_path)])
    run_result = runner.invoke(
        app,
        [
            "run",
            "--suite",
            "architecture_review",
            "--treatments",
            "persona,skill",
            "--repetitions",
            "1",
            "--paraphrases",
            "1",
            "--mock",
            "--data-dir",
            str(tmp_path / "datasets"),
            "--specs-dir",
            str(tmp_path / "specs"),
            "--traces-dir",
            str(tmp_path / "traces"),
        ],
    )
    assert run_result.exit_code == 0

    # Extract run ID from output
    import re

    match = re.search(r"Run ID: (\S+)", run_result.stdout)
    assert match, f"No run ID found in: {run_result.stdout}"
    run_id = match.group(1)

    # Generate report
    report_result = runner.invoke(
        app,
        [
            "report",
            "--run-id",
            run_id,
            "--format",
            "html",
            "--output",
            str(tmp_path / "report_test"),
            "--traces-dir",
            str(tmp_path / "traces"),
        ],
    )
    assert report_result.exit_code == 0
    assert (tmp_path / "report_test.html").exists()


def test_promote_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Init and run
    runner.invoke(app, ["init", "--path", str(tmp_path)])
    run_result = runner.invoke(
        app,
        [
            "run",
            "--suite",
            "architecture_review",
            "--treatments",
            "persona,skill",
            "--repetitions",
            "1",
            "--paraphrases",
            "1",
            "--mock",
            "--data-dir",
            str(tmp_path / "datasets"),
            "--specs-dir",
            str(tmp_path / "specs"),
            "--traces-dir",
            str(tmp_path / "traces"),
        ],
    )
    assert run_result.exit_code == 0

    # Promote
    promote_result = runner.invoke(
        app,
        [
            "promote",
            "--suite",
            "architecture_review",
            "--from",
            "persona",
            "--to",
            "skill",
            "--traces-dir",
            str(tmp_path / "traces"),
        ],
    )
    assert promote_result.exit_code == 0
    assert "Promotion" in promote_result.stdout


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "PromptStackBench" in result.stdout
