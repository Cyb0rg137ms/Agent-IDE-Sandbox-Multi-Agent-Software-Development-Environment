"""
Agentic IDE Sandbox core package.
Integrates the Claude-Lightyear v10.0 Ultra / LOGOS cognitive architecture
with universal local (Ollama GGUF) and cloud frontier API provider support.
"""

from agent_core.agents import (
    BaseAgent,
    CoderAgent,
    TesterAgent,
    ReviewerAgent,
    PonderingAgent,
    LogosArchitectAgent,
)
from agent_core.sandbox import CodeExecutionSandbox
from agent_core.orchestrator import AgenticIDEOrchestrator
from agent_core.operator_interface import SandboxOperatorInterface, SandboxSessionReport
from agent_core.llm import LLMRegistry, BaseLLMProvider, OllamaProvider, MockLLMProvider

__all__ = [
    "BaseAgent",
    "CoderAgent",
    "TesterAgent",
    "ReviewerAgent",
    "PonderingAgent",
    "LogosArchitectAgent",
    "CodeExecutionSandbox",
    "AgenticIDEOrchestrator",
    "SandboxOperatorInterface",
    "SandboxSessionReport",
    "LLMRegistry",
    "BaseLLMProvider",
    "OllamaProvider",
    "MockLLMProvider",
]
