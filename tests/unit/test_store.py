"""Unit tests for SQLite store."""

import tempfile
from pathlib import Path

from promptstackbench.schema.run import Output, Run, Score
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


def test_init_db_creates_tables():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "test.db"
        conn = init_db(db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        assert "runs" in table_names
        assert "outputs" in table_names
        assert "scores" in table_names
        assert "traces" in table_names
        assert "tasks" in table_names
        assert "treatments" in table_names
        conn.close()


def test_insert_and_retrieve_run():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "test.db"
        conn = init_db(db_path)
        run = Run(suite_id="test_suite", model="gpt-4.1")
        insert_run(conn, run)
        rows = conn.execute("SELECT id, suite_id, model FROM runs").fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "test_suite"
        conn.close()


def test_insert_output_and_scores():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "test.db"
        conn = init_db(db_path)
        run = Run(suite_id="test_suite", model="gpt-4.1")
        insert_run(conn, run)
        insert_task(conn, "t1", "test_suite", "explanation", "Explain X")
        insert_treatment(conn, "tr1", "persona")

        output = Output(
            run_id=run.id,
            task_id="t1",
            treatment_id="tr1",
            treatment_type="persona",
            raw_output="The answer",
            latency_ms=500,
        )
        output_id = insert_output(conn, output)

        score = Score(metric="correctness", score=8.5, output_id=str(output_id))
        insert_score(conn, score)

        scores = get_scores_for_run(conn, run.id)
        assert len(scores) == 1
        assert scores[0]["metric"] == "correctness"
        assert scores[0]["score"] == 8.5

        outputs = get_outputs_for_run(conn, run.id)
        assert len(outputs) == 1
        assert outputs[0]["raw_output"] == "The answer"

        conn.close()
