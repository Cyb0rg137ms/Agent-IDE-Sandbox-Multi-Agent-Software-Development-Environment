from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Dict, Optional
from agent_core.llm.base import BaseLLMProvider
from agent_core.llm.mock_provider import MockLLMProvider
from agent_core.llm.ollama_provider import OllamaProvider

try:
    from agent_core.llm.cloud_providers import (
        OpenAICompatibleProvider,
        AnthropicProvider,
        GrokProvider,
        GeminiProvider,
    )
    _CLOUD_AVAILABLE = True
except ImportError:
    _CLOUD_AVAILABLE = False
    class _MissingProvider(BaseLLMProvider):
        @property
        def provider_name(self): return "missing"
        def generate(self, *args, **kwargs): raise ImportError("Cloud providers not installed")
        def chat(self, *args, **kwargs): raise ImportError("Cloud providers not installed")
    OpenAICompatibleProvider = _MissingProvider
    AnthropicProvider = _MissingProvider
    GrokProvider = _MissingProvider
    GeminiProvider = _MissingProvider

class LLMRegistry:
    _PROVIDERS = {
        "mock": MockLLMProvider,
        "ollama": OllamaProvider,
    }
    if _CLOUD_AVAILABLE:
        _PROVIDERS.update({
            "openai": OpenAICompatibleProvider,
            "anthropic": AnthropicProvider,
            "claude": AnthropicProvider,
            "grok": GrokProvider,
            "gemini": GeminiProvider,
            "local": OpenAICompatibleProvider,
        })
    DEFAULT_MODELS = {
        "mock": "mock-developer-v1",
        "ollama": "qwen2.5-coder:1.5b",
        "openai": "gpt-4o",
        "anthropic": "claude-3-7-sonnet-20250219",
        "claude": "claude-3-7-sonnet-20250219",
        "grok": "grok-2-latest",
        "gemini": "gemini-1.5-flash",
        "local": "local-model",
    }
    @classmethod
    def get_provider(cls, provider_name="mock", model_name=None, config_path=None, **kwargs):
        p_name = provider_name.lower().strip()
        provider_cls = cls._PROVIDERS.get(p_name)
        if not provider_cls:
            raise ValueError(f"Unknown provider '{provider_name}'. Available: {list(cls._PROVIDERS.keys())}")
        merged_kwargs = dict(kwargs)
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    file_conf = json.load(f)
                    p_conf = file_conf.get("providers", {}).get(p_name, {})
                    for k, v in p_conf.items():
                        if k not in merged_kwargs:
                            merged_kwargs[k] = v
            except: pass
        model = model_name or merged_kwargs.pop("model", None) or cls.DEFAULT_MODELS.get(p_name, "default-model")
        return provider_cls(model_name=model, **merged_kwargs)
    @classmethod
    def auto_detect(cls, config_path=None):
        try:
            ollama = OllamaProvider()
            if ollama.is_available():
                models = ollama.list_local_models()
                chosen_model = models[0] if models else "qwen2.5-coder:1.5b"
                return OllamaProvider(model_name=chosen_model)
        except: pass
        if _CLOUD_AVAILABLE:
            if os.getenv("ANTHROPIC_API_KEY"):
                try: return AnthropicProvider()
                except: pass
            if os.getenv("OPENAI_API_KEY"):
                try: return OpenAICompatibleProvider()
                except: pass
            if os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY"):
                try: return GrokProvider()
                except: pass
            if os.getenv("GEMINI_API_KEY"):
                try: return GeminiProvider()
                except: pass
        return MockLLMProvider(model_name="mock-developer-v1")
