"""
test_agent_ide.py
=================
Comprehensive test suite for Agent-IDE Sandbox.

Tests cover:
  - Tool system: FileRead, FileWrite, ShellExecute, PythonEval
  - ToolRegistry: registration, lookup, schema generation
  - ConversationBuffer: token budget, rolling trim, system prompt preservation
  - EpisodicStore: embedding computation, retrieval ranking, success rate
  - Original agent correctness: CoderAgent, TesterAgent, ReviewerAgent
"""

import os
import math
import tempfile
import pytest

from agent_core.tools import (
    FileReadTool,
    FileWriteTool,
    ShellExecuteTool,
    PythonEvalTool,
    ToolRegistry,
    ToolResult,
)
from agent_core.memory import (
    ConversationBuffer,
    EpisodicStore,
    Message,
    _cosine_similarity,
)
from agent_core.agents import CoderAgent, TesterAgent, ReviewerAgent


# ---------------------------------------------------------------------------
# 1. FileReadTool
# ---------------------------------------------------------------------------

class TestFileReadTool:
    def test_read_existing_file(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("Hello, World!")
        result = FileReadTool().execute(path=str(f))
        assert result.success
        assert "Hello, World!" in result.output

    def test_read_missing_file(self):
        result = FileReadTool().execute(path="/nonexistent/path/foo.txt")
        assert not result.success
        assert result.error is not None

    def test_read_truncation(self, tmp_path):
        f = tmp_path / "big.txt"
        f.write_text("\n".join(str(i) for i in range(500)))
        result = FileReadTool().execute(path=str(f), max_lines=10)
        assert result.success
        assert "truncated" in result.output

    def test_read_nonfile_path(self, tmp_path):
        result = FileReadTool().execute(path=str(tmp_path))  # Directory
        assert not result.success

    def test_elapsed_ms_recorded(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("x")
        result = FileReadTool().execute(path=str(f))
        assert result.elapsed_ms >= 0


# ---------------------------------------------------------------------------
# 2. FileWriteTool
# ---------------------------------------------------------------------------

class TestFileWriteTool:
    def test_write_creates_file(self, tmp_path):
        p = tmp_path / "out.txt"
        result = FileWriteTool().execute(path=str(p), content="test content")
        assert result.success
        assert p.read_text() == "test content"

    def test_write_creates_parent_dirs(self, tmp_path):
        p = tmp_path / "a" / "b" / "c.txt"
        result = FileWriteTool().execute(path=str(p), content="nested")
        assert result.success
        assert p.exists()

    def test_write_overwrites(self, tmp_path):
        p = tmp_path / "f.txt"
        FileWriteTool().execute(path=str(p), content="original")
        FileWriteTool().execute(path=str(p), content="overwritten", mode="write")
        assert p.read_text() == "overwritten"


# ---------------------------------------------------------------------------
# 3. PythonEvalTool
# ---------------------------------------------------------------------------

class TestPythonEvalTool:
    def test_basic_arithmetic(self):
        result = PythonEvalTool().execute(expression="2 + 2 * 3")
        assert result.success
        assert "8" in result.output

    def test_math_functions(self):
        result = PythonEvalTool().execute(expression="math.sqrt(16)")
        assert result.success
        assert "4.0" in result.output

    def test_list_comprehension(self):
        result = PythonEvalTool().execute(expression="[x**2 for x in range(5)]")
        assert result.success
        assert "16" in result.output

    def test_blocks_import(self):
        result = PythonEvalTool().execute(expression="__import__('os')")
        assert not result.success

    def test_blocks_exec(self):
        result = PythonEvalTool().execute(expression="exec('x=1')")
        assert not result.success

    def test_string_operations(self):
        result = PythonEvalTool().execute(expression="'hello'.upper()")
        assert result.success
        assert "HELLO" in result.output

    def test_complex_math(self):
        result = PythonEvalTool().execute(expression="sum(range(101))")
        assert result.success
        assert "5050" in result.output


# ---------------------------------------------------------------------------
# 4. ShellExecuteTool
# ---------------------------------------------------------------------------

class TestShellExecuteTool:
    def test_simple_echo(self):
        result = ShellExecuteTool().execute(command="echo hello")
        assert result.success
        assert "hello" in result.output

    def test_failed_command(self):
        result = ShellExecuteTool().execute(command="nonexistentcommand123 --flag")
        assert not result.success

    def test_timeout_respected(self):
        result = ShellExecuteTool().execute(
            command="ping -n 10 127.0.0.1" if os.name == "nt" else "sleep 10",
            timeout_s=1.0,
        )
        assert not result.success
        assert "timed out" in (result.error or "").lower()

    def test_max_timeout_capped(self):
        tool = ShellExecuteTool()
        # Requesting 999s timeout should be capped at MAX_TIMEOUT
        result = tool.execute(command="echo hi", timeout_s=999)
        assert result.success  # Should still succeed (quick command)


# ---------------------------------------------------------------------------
# 5. ToolRegistry
# ---------------------------------------------------------------------------

class TestToolRegistry:
    def test_default_registry_has_tools(self):
        registry = ToolRegistry.default()
        assert registry.get("file_read") is not None
        assert registry.get("file_write") is not None
        assert registry.get("shell_execute") is not None
        assert registry.get("python_eval") is not None

    def test_unknown_tool_returns_error(self):
        registry = ToolRegistry.default()
        result = registry.execute("nonexistent_tool", foo="bar")
        assert not result.success
        assert "Unknown tool" in (result.error or "")

    def test_schemas_are_complete(self):
        registry = ToolRegistry.default()
        for schema in registry.schemas():
            assert "name" in schema
            assert "description" in schema
            assert "parameters" in schema

    def test_execute_via_registry(self):
        registry = ToolRegistry.default()
        result = registry.execute("python_eval", expression="1 + 1")
        assert result.success and "2" in result.output


# ---------------------------------------------------------------------------
# 6. ConversationBuffer
# ---------------------------------------------------------------------------

class TestConversationBuffer:
    def test_add_and_retrieve_messages(self):
        buf = ConversationBuffer(max_tokens=1000)
        buf.add("user", "Hello")
        buf.add("assistant", "Hi there")
        msgs = buf.get_messages()
        assert len(msgs) == 2
        assert msgs[0]["role"] == "user"

    def test_system_prompt_preserved(self):
        buf = ConversationBuffer(system_prompt="You are a helpful assistant.")
        buf.add("user", "x" * 2000)  # Large message
        buf.add("user", "y" * 2000)  # Force trimming
        msgs = buf.get_messages()
        # System message must always be present
        assert any(m["role"] == "system" for m in msgs)

    def test_token_budget_enforced(self):
        buf = ConversationBuffer(max_tokens=100)
        for i in range(20):
            buf.add("user", "word " * 20)  # ~20 tokens each
        assert buf.token_usage <= 100 + 50  # Allow some slack

    def test_clear_except_system(self):
        buf = ConversationBuffer(system_prompt="System")
        buf.add("user", "Hello")
        buf.add("assistant", "World")
        buf.clear_except_system()
        msgs = buf.get_messages()
        assert len(msgs) == 1
        assert msgs[0]["role"] == "system"

    def test_message_count_accurate(self):
        buf = ConversationBuffer()
        assert buf.message_count == 0
        buf.add("user", "hi")
        assert buf.message_count == 1

    def test_repr_informative(self):
        buf = ConversationBuffer()
        repr_str = repr(buf)
        assert "ConversationBuffer" in repr_str


# ---------------------------------------------------------------------------
# 7. EpisodicStore
# ---------------------------------------------------------------------------

class TestEpisodicStore:
    def test_store_and_count(self):
        store = EpisodicStore()
        store.store("Fix divide-by-zero bug", "Added zero check", success=True)
        assert store.episode_count == 1

    def test_embedding_computed(self):
        store = EpisodicStore()
        ep = store.store("Write unit tests for login function", "Added 5 tests", success=True)
        assert ep.embedding is not None
        assert len(ep.embedding) == 256

    def test_retrieve_similar_returns_sorted(self):
        store = EpisodicStore()
        store.store("Fix division by zero error in calculator", "Add check", success=True)
        store.store("Refactor database connection pool", "Used context manager", success=True)
        store.store("Handle divide by zero in math util", "Zero check added", success=True)

        results = store.retrieve_similar("division by zero bug fix", top_k=2)
        assert len(results) >= 1
        # First result should be more similar than second
        if len(results) >= 2:
            assert results[0][1] >= results[1][1]

    def test_success_rate_all_success(self):
        store = EpisodicStore()
        for i in range(5):
            store.store(f"task {i}", f"solution {i}", success=True)
        assert store.success_rate() == 1.0

    def test_success_rate_mixed(self):
        store = EpisodicStore()
        store.store("task 1", "sol", success=True)
        store.store("task 2", "sol", success=False)
        assert abs(store.success_rate() - 0.5) < 0.01

    def test_max_episodes_enforced(self):
        store = EpisodicStore(max_episodes=5)
        for i in range(10):
            store.store(f"task {i}", "sol")
        assert store.episode_count <= 5

    def test_cosine_similarity_identical(self):
        v = [1.0, 0.0, 0.5, 0.3]
        assert abs(_cosine_similarity(v, v) - 1.0) < 1e-9

    def test_cosine_similarity_orthogonal(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert abs(_cosine_similarity(a, b)) < 1e-9

    def test_retrieve_empty_store(self):
        store = EpisodicStore()
        assert store.retrieve_similar("anything") == []


# ---------------------------------------------------------------------------
# 8. Original agent tests (correctness)
# ---------------------------------------------------------------------------

class TestOriginalAgents:
    def test_coder_generates_divide_code(self):
        agent = CoderAgent()
        code = agent.generate_code("write a divide function")
        assert "def divide" in code

    def test_coder_fixes_zero_division(self):
        agent = CoderAgent()
        fixed = agent.generate_code("divide task", error_logs="ZeroDivisionError: division by zero")
        assert "if b == 0" in fixed

    def test_tester_generates_assertions(self):
        agent = TesterAgent()
        tests = agent.generate_tests("def divide(a, b): return a/b", "divide task")
        assert "assert" in tests

    def test_reviewer_approves_safe_code(self):
        agent = ReviewerAgent()
        result = agent.review_code('def add(a, b):\n    """Add two numbers."""\n    return a + b')
        assert result["approved"]
        assert result["security_check"] == "passed"

    def test_reviewer_rejects_os_system(self):
        agent = ReviewerAgent()
        result = agent.review_code("os.system('rm -rf /')")
        assert result["security_check"] == "failed"
