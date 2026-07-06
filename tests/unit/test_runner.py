"""Unit tests for LLM runner."""

from promptstackbench.runners.llm_runner import MockProvider, run_single


def test_mock_provider_returns_fixed_response():
    provider = MockProvider()
    text, input_tokens, output_tokens = provider.complete("hello", "gpt-4.1")
    assert text == "Mock response."
    assert input_tokens == 10
    assert output_tokens == 5


def test_mock_provider_custom_responses():
    provider = MockProvider(responses={"1": "First", "2": "Second"})
    text1, _, _ = provider.complete("q1", "gpt-4.1")
    text2, _, _ = provider.complete("q2", "gpt-4.1")
    assert text1 == "First"
    assert text2 == "Second"


def test_run_single_with_mock():
    provider = MockProvider()
    output = run_single(
        provider=provider,
        prompt="test prompt",
        model="gpt-4.1",
        run_id="r1",
        task_id="t1",
        treatment_id="tr1",
        treatment_type="persona",
    )
    assert output.raw_output == "Mock response."
    assert output.token_input == 10
    assert output.token_output == 5
    assert output.latency_ms >= 0
    assert output.cost_estimate > 0
    assert output.treatment_type == "persona"
