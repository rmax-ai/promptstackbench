"""LLM runner — sends prompts to model APIs and collects outputs."""

from __future__ import annotations

import time

import httpx

from promptstackbench.errors import RunnerError
from promptstackbench.schema.run import Output


class LLMProvider:
    """OpenAI-compatible API provider adapter."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 120,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(
        self, prompt: str, model: str, temperature: float = 0.2
    ) -> tuple[str, int, int]:
        """Send a completion request and return (text, input_tokens, output_tokens)."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        try:
            response = httpx.post(
                url, json=payload, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            input_tokens = data.get("usage", {}).get("prompt_tokens", 0)
            output_tokens = data.get("usage", {}).get("completion_tokens", 0)
            return text, input_tokens, output_tokens
        except httpx.HTTPStatusError as e:
            raise RunnerError(
                f"API error {e.response.status_code}: {e.response.text[:500]}"
            ) from e
        except httpx.RequestError as e:
            raise RunnerError(f"Request failed: {e}") from e


class MockProvider:
    """Mock provider for testing — returns fixed responses."""

    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or {}
        self.call_count = 0

    def complete(
        self, prompt: str, model: str, temperature: float = 0.2
    ) -> tuple[str, int, int]:
        self.call_count += 1
        text = self.responses.get(str(self.call_count), "Mock response.")
        return text, 10, 5


def run_single(
    provider: LLMProvider | MockProvider,
    prompt: str,
    model: str,
    run_id: str,
    task_id: str,
    treatment_id: str,
    treatment_type: str,
    paraphrase_index: int = 0,
    repetition_index: int = 0,
) -> Output:
    """Run a single prompt through the provider and return an Output."""
    t0 = time.monotonic()
    raw_output, token_input, token_output = provider.complete(prompt, model)
    latency_ms = int((time.monotonic() - t0) * 1000)
    cost = _estimate_cost(model, token_input, token_output)

    return Output(
        run_id=run_id,
        task_id=task_id,
        treatment_id=treatment_id,
        treatment_type=treatment_type,
        paraphrase_index=paraphrase_index,
        repetition_index=repetition_index,
        raw_output=raw_output,
        latency_ms=latency_ms,
        token_input=token_input,
        token_output=token_output,
        cost_estimate=cost,
    )


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost based on model pricing (approximate)."""
    if "gpt-4" in model:
        input_price = 2.50 / 1_000_000
        output_price = 10.00 / 1_000_000
    elif "gpt-3.5" in model:
        input_price = 0.50 / 1_000_000
        output_price = 1.50 / 1_000_000
    else:
        input_price = 1.00 / 1_000_000
        output_price = 2.00 / 1_000_000
    return input_tokens * input_price + output_tokens * output_price
