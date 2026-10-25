import pytest

from agent_core.llm.ollama_provider import OllamaProvider


@pytest.fixture(autouse=True)
def _fresh_ollama_availability_cache():
    """Each test sees a cold availability cache, so results never leak between tests."""
    OllamaProvider.clear_availability_cache()
    yield
    OllamaProvider.clear_availability_cache()
