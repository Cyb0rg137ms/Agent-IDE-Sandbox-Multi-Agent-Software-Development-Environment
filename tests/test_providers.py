"""
test_providers.py
=================
Unit tests for universal LLM providers in Agent-IDE Sandbox:
  - MockLLMProvider
  - OllamaProvider (local GGUF integration)
  - OpenAICompatibleProvider, AnthropicProvider, GrokProvider, GeminiProvider
  - LLMRegistry discovery and auto-detection
"""

import os
from unittest.mock import MagicMock, patch
import pytest

from agent_core.llm import (
    BaseLLMProvider,
    LLMResponse,
    MockLLMProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    AnthropicProvider,
    GrokProvider,
    GeminiProvider,
    LLMRegistry,
)


class TestMockLLMProvider:
    def test_mock_generation(self):
        provider = MockLLMProvider("mock-v1")
        assert provider.provider_name == "mock"
        assert provider.is_available() is True

        resp = provider.generate("Write a divide function")
        assert isinstance(resp, LLMResponse)
        assert "def divide" in resp.content
        assert resp.model == "mock-v1"

    def test_mock_chat(self):
        provider = MockLLMProvider()
        messages = [
            {"role": "system", "content": "You are a tester."},
            {"role": "user", "content": "Generate tests for divide."},
        ]
        resp = provider.chat(messages)
        assert "assert divide" in resp.content

    def test_extract_code_block(self):
        provider = MockLLMProvider()
        markdown = "Here is the code:\n```python\nx = 10\n```\nDone."
        extracted = provider.extract_code_block(markdown)
        assert extracted == "x = 10"


class TestOllamaProvider:
    def test_ollama_init(self):
        provider = OllamaProvider(model_name="qwen2.5-coder:7b", host="http://localhost:11434")
        assert provider.provider_name == "ollama"
        assert provider.host == "http://localhost:11434"

    @patch("urllib.request.urlopen")
    def test_ollama_availability_true(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OllamaProvider()
        assert provider.is_available() is True

    @patch("urllib.request.urlopen")
    def test_ollama_generate_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"response": "def test(): pass", "eval_count": 5, "prompt_eval_count": 3, "done": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OllamaProvider()
        res = provider.generate("test prompt")
        assert res.content == "def test(): pass"
        assert res.completion_tokens == 5
        assert res.prompt_tokens == 3


class TestCloudProviders:
    def test_openai_compatible_init(self):
        p = OpenAICompatibleProvider(model_name="gpt-4o", api_key="sk-test")
        assert p.provider_name == "openai"
        assert p.is_available() is True

    def test_anthropic_init(self):
        p = AnthropicProvider(model_name="claude-3-7-sonnet-20250219", api_key="ant-test")
        assert p.provider_name == "anthropic"
        assert p.is_available() is True

    def test_grok_init(self):
        p = GrokProvider(model_name="grok-2-latest", api_key="xai-test")
        assert p.provider_name == "grok"
        assert p.is_available() is True

    def test_gemini_init(self):
        p = GeminiProvider(model_name="gemini-1.5-flash", api_key="gem-test")
        assert p.provider_name == "gemini"
        assert p.is_available() is True


class TestLLMRegistry:
    def test_get_mock_provider(self):
        p = LLMRegistry.get_provider("mock")
        assert isinstance(p, MockLLMProvider)

    def test_get_ollama_provider(self):
        p = LLMRegistry.get_provider("ollama", model_name="deepseek-r1:14b")
        assert isinstance(p, OllamaProvider)
        assert p.model_name == "deepseek-r1:14b"

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError):
            LLMRegistry.get_provider("nonexistent-provider")

    def test_auto_detect_fallback(self):
        # Without any keys or ollama, falls back to Mock
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(OllamaProvider, "is_available", return_value=False):
                p = LLMRegistry.auto_detect()
                assert isinstance(p, MockLLMProvider)
