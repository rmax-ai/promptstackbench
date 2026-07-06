"""Domain exception hierarchy."""

from __future__ import annotations


class PromptStackBenchError(Exception):
    """Base error for all PromptStackBench exceptions."""


class ConfigError(PromptStackBenchError):
    """Configuration error — missing or invalid config."""


class RunnerError(PromptStackBenchError):
    """Runner error — model unavailable, timeout, bad response."""


class EvalError(PromptStackBenchError):
    """Evaluator error — missing data, invalid score shape."""


class LoaderError(PromptStackBenchError):
    """Loader error — file not found, malformed YAML."""


class StoreError(PromptStackBenchError):
    """Database error — connection, query, migration failure."""
