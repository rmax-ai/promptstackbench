"""Unit tests for task schema models."""

from promptstackbench.schema.task import Task, TaskClass, TaskSuite


def test_task_creation():
    task = Task(
        id="test_task",
        suite_id="test_suite",
        task_class=TaskClass.ARCHITECTURE_REVIEW,
        input="Review this design.",
    )
    assert task.id == "test_task"
    assert task.task_class == TaskClass.ARCHITECTURE_REVIEW


def test_task_suite_creation():
    tasks = [
        Task(
            id="t1", suite_id="s1", task_class=TaskClass.EXPLANATION, input="Explain X"
        ),
        Task(
            id="t2", suite_id="s1", task_class=TaskClass.EXPLANATION, input="Explain Y"
        ),
    ]
    suite = TaskSuite(
        id="test_suite",
        name="Test Suite",
        task_class=TaskClass.EXPLANATION,
        tasks=tasks,
    )
    assert len(suite) == 2
    assert len(suite.tasks) == 2


def test_task_class_enum():
    assert TaskClass.EXPLANATION.value == "explanation"
    assert TaskClass.ARCHITECTURE_REVIEW.value == "architecture_review"
