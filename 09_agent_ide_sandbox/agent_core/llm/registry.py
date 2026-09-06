"""
registry.py
===========
Provider factory and dynamic resolver for Agent-IDE Sandbox.
Handles auto-detection of available local runtimes (Ollama) and API keys.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Type
from agent_core.llm.base import BaseLLMProvider
from agent_core.llm.mock_provider import MockLLMProvider
from agent_core.llm.ollama_provider import OllamaProvider
from agent_core.llm.cloud_providers import (
    OpenAICompatibleProvider,
    AnthropicProvider,
    GrokProvider,
    GeminiProvider,
)


class LLMRegistry:
    """Registry for discovering, instantiating, and resolving LLM providers."""

    _PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {
        "mock": MockLLMProvider,
        "ollama": OllamaProvider,
        "openai": OpenAICompatibleProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,
        "grok": GrokProvider,
        "gemini": GeminiProvider,
        "local": OpenAICompatibleProvider,  # For LM Studio, llama.cpp server
    }

    DEFAULT_MODELS: Dict[str, str] = {
        "mock": "mock-developer-v1",
        "ollama": "qwen2.5-coder:7b",
        "openai": "gpt-4o",
        "anthropic": "claude-3-7-sonnet-20250219",
        "claude": "claude-3-7-sonnet-20250219",
        "grok": "grok-2-latest",
        "gemini": "gemini-1.5-flash",
        "local": "local-model",
    }

    @classmethod
    def get_provider(
        cls,
        provider_name: str = "mock",
        model_name: Optional[str] = None,
        config_path: Optional[str] = None,
        **kwargs: Any,
    ) -> BaseLLMProvider:
        """Instantiates a provider by name with appropriate model defaults."""
        p_name = provider_name.lower().strip()
        provider_cls = cls._PROVIDERS.get(p_name)
        if not provider_cls:
            raise ValueError(
                f"Unknown LLM provider '{provider_name}'. Supported providers: {list(cls._PROVIDERS.keys())}"
            )

        # Merge config file if present
        merged_kwargs = dict(kwargs)
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    file_conf = json.load(f)
                    p_conf = file_conf.get("providers", {}).get(p_name, {})
                    for k, v in p_conf.items():
                        if k not in merged_kwargs:
                            merged_kwargs[k] = v
            except Exception:
                pass

        model = model_name or merged_kwargs.pop("model", None) or cls.DEFAULT_MODELS.get(p_name, "default-model")
        return provider_cls(model_name=model, **merged_kwargs)

    @classmethod
    def auto_detect(cls, config_path: Optional[str] = None) -> BaseLLMProvider:
        """
        Auto-detects the best available provider in precedence order:
        1. Local Ollama (if active and running)
        2. Anthropic API (if ANTHROPIC_API_KEY present)
        3. OpenAI API (if OPENAI_API_KEY present)
        4. Grok API (if XAI_API_KEY or GROK_API_KEY present)
        5. Gemini API (if GEMINI_API_KEY present)
        6. Mock provider (fallback zero-dependency)
        """
        # 1. Check local Ollama
        try:
            ollama = OllamaProvider()
            if ollama.is_available():
                models = ollama.list_local_models()
                chosen_model = models[0] if models else "qwen2.5-coder:7b"
                return OllamaProvider(model_name=chosen_model)
        except Exception:
            pass

        # 2. Check Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            return AnthropicProvider()

        # 3. Check OpenAI
        if os.getenv("OPENAI_API_KEY"):
            return OpenAICompatibleProvider()

        # 4. Check Grok
        if os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY"):
            return GrokProvider()

        # 5. Check Gemini
        if os.getenv("GEMINI_API_KEY"):
            return GeminiProvider()

        # 6. Fallback to mock
        return MockLLMProvider(model_name="mock-developer-v1")
