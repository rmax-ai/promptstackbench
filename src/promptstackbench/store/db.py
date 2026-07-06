"""SQLite trace store — schema init and CRUD operations."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptstackbench.schema.run import Output, Run, Score, Trace

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    suite_id TEXT NOT NULL,
    model TEXT NOT NULL,
    started_at TEXT NOT NULL,
    git_sha TEXT DEFAULT '',
    config_hash TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    suite_id TEXT NOT NULL,
    task_class TEXT NOT NULL,
    input TEXT NOT NULL,
    expected_properties TEXT DEFAULT '{}',
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS treatments (
    id TEXT NOT NULL,
    type TEXT NOT NULL,
    spec_path TEXT DEFAULT '',
    spec_hash TEXT DEFAULT '',
    PRIMARY KEY (id, type)
);

CREATE TABLE IF NOT EXISTS outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    treatment_id TEXT NOT NULL,
    treatment_type TEXT NOT NULL,
    paraphrase_index INTEGER DEFAULT 0,
    repetition_index INTEGER DEFAULT 0,
    raw_output TEXT DEFAULT '',
    parsed_output TEXT DEFAULT '{}',
    latency_ms INTEGER DEFAULT 0,
    token_input INTEGER DEFAULT 0,
    token_output INTEGER DEFAULT 0,
    cost_estimate REAL DEFAULT 0.0,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL,
    step_index INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    content TEXT DEFAULT '',
    tool_name TEXT DEFAULT '',
    tool_args TEXT DEFAULT '{}',
    tool_result TEXT DEFAULT '',
    FOREIGN KEY (output_id) REFERENCES outputs(id)
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL,
    metric TEXT NOT NULL,
    score REAL NOT NULL,
    rationale TEXT DEFAULT '',
    evaluator_model TEXT DEFAULT '',
    evaluator_version TEXT DEFAULT '',
    FOREIGN KEY (output_id) REFERENCES outputs(id)
);

CREATE INDEX IF NOT EXISTS idx_outputs_run ON outputs(run_id);
CREATE INDEX IF NOT EXISTS idx_outputs_task ON outputs(task_id);
CREATE INDEX IF NOT EXISTS idx_outputs_treatment ON outputs(treatment_id);
CREATE INDEX IF NOT EXISTS idx_scores_output ON scores(output_id);
CREATE INDEX IF NOT EXISTS idx_scores_metric ON scores(metric);
CREATE INDEX IF NOT EXISTS idx_traces_output ON traces(output_id);
"""


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize the SQLite database and return a connection."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def insert_run(conn: sqlite3.Connection, run: Run) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO runs (id, suite_id, model, started_at, git_sha, config_hash) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            run.id,
            run.suite_id,
            run.model,
            run.started_at.isoformat(),
            run.git_sha,
            run.config_hash,
        ),
    )
    conn.commit()


def insert_task(
    conn: sqlite3.Connection,
    task_id: str,
    suite_id: str,
    task_class: str,
    input_text: str,
    expected_properties: str = "{}",
    metadata: str = "{}",
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO tasks (id, suite_id, task_class, input, expected_properties, metadata) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (task_id, suite_id, task_class, input_text, expected_properties, metadata),
    )
    conn.commit()


def insert_treatment(
    conn: sqlite3.Connection,
    treatment_id: str,
    treatment_type: str,
    spec_path: str = "",
    spec_hash: str = "",
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO treatments (id, type, spec_path, spec_hash) "
        "VALUES (?, ?, ?, ?)",
        (treatment_id, treatment_type, spec_path, spec_hash),
    )
    conn.commit()


def insert_output(conn: sqlite3.Connection, output: Output) -> int:
    import json

    cursor = conn.execute(
        "INSERT INTO outputs (run_id, task_id, treatment_id, treatment_type, "
        "paraphrase_index, repetition_index, raw_output, parsed_output, "
        "latency_ms, token_input, token_output, cost_estimate) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            output.run_id,
            output.task_id,
            output.treatment_id,
            output.treatment_type,
            output.paraphrase_index,
            output.repetition_index,
            output.raw_output,
            json.dumps(output.parsed_output),
            output.latency_ms,
            output.token_input,
            output.token_output,
            output.cost_estimate,
        ),
    )
    conn.commit()
    return cursor.lastrowid or 0


def insert_trace(conn: sqlite3.Connection, trace: Trace) -> int:
    import json

    cursor = conn.execute(
        "INSERT INTO traces (output_id, step_index, event_type, content, tool_name, tool_args, tool_result) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            trace.output_id,
            trace.step_index,
            trace.event_type,
            trace.content,
            trace.tool_name,
            json.dumps(trace.tool_args),
            trace.tool_result,
        ),
    )
    conn.commit()
    return cursor.lastrowid or 0


def insert_score(conn: sqlite3.Connection, score: Score) -> int:
    cursor = conn.execute(
        "INSERT INTO scores (output_id, metric, score, rationale, evaluator_model, evaluator_version) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            score.output_id,
            score.metric,
            score.score,
            score.rationale,
            score.evaluator_model,
            score.evaluator_version,
        ),
    )
    conn.commit()
    return cursor.lastrowid or 0


def get_scores_for_run(conn: sqlite3.Connection, run_id: str) -> list[dict]:
    """Get all scores for a run, joined with output metadata."""
    rows = conn.execute(
        "SELECT s.metric, s.score, s.rationale, o.task_id, o.treatment_id, o.treatment_type, "
        "o.paraphrase_index, o.repetition_index "
        "FROM scores s JOIN outputs o ON s.output_id = o.id "
        "WHERE o.run_id = ? ORDER BY o.task_id, o.treatment_id, s.metric",
        (run_id,),
    ).fetchall()
    return [
        {
            "metric": r[0],
            "score": r[1],
            "rationale": r[2],
            "task_id": r[3],
            "treatment_id": r[4],
            "treatment_type": r[5],
            "paraphrase_index": r[6],
            "repetition_index": r[7],
        }
        for r in rows
    ]


def get_outputs_for_run(conn: sqlite3.Connection, run_id: str) -> list[dict]:
    """Get all outputs for a run."""
    rows = conn.execute(
        "SELECT id, task_id, treatment_id, treatment_type, paraphrase_index, "
        "repetition_index, raw_output, latency_ms, token_input, token_output, cost_estimate "
        "FROM outputs WHERE run_id = ? ORDER BY task_id, treatment_id, paraphrase_index",
        (run_id,),
    ).fetchall()
    return [
        {
            "id": r[0],
            "task_id": r[1],
            "treatment_id": r[2],
            "treatment_type": r[3],
            "paraphrase_index": r[4],
            "repetition_index": r[5],
            "raw_output": r[6],
            "latency_ms": r[7],
            "token_input": r[8],
            "token_output": r[9],
            "cost_estimate": r[10],
        }
        for r in rows
    ]


def get_latest_run_id(
    conn: sqlite3.Connection, suite_id: str = ""
) -> str | None:
    """Return the most recent run ID, optionally filtered by suite."""
    if suite_id:
        row = conn.execute(
            "SELECT id FROM runs WHERE suite_id = ? ORDER BY started_at DESC LIMIT 1",
            (suite_id,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()

    return row[0] if row else None


def get_latest_scored_run_id(
    conn: sqlite3.Connection, suite_id: str = ""
) -> str | None:
    """Return the most recent run ID that has at least one score."""
    if suite_id:
        row = conn.execute(
            "SELECT r.id "
            "FROM runs r "
            "JOIN outputs o ON o.run_id = r.id "
            "JOIN scores s ON s.output_id = o.id "
            "WHERE r.suite_id = ? "
            "GROUP BY r.id "
            "ORDER BY r.started_at DESC LIMIT 1",
            (suite_id,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT r.id "
            "FROM runs r "
            "JOIN outputs o ON o.run_id = r.id "
            "JOIN scores s ON s.output_id = o.id "
            "GROUP BY r.id "
            "ORDER BY r.started_at DESC LIMIT 1"
        ).fetchone()

    return row[0] if row else None
