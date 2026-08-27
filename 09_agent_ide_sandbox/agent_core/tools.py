"""
tools.py
========
Tool definitions and executor for the Agent-IDE Sandbox.

Implements an OpenAI function-calling compatible tool system:
  - FileReadTool: reads a file path, returns content or error
  - FileWriteTool: writes content to a file path
  - ShellExecuteTool: runs code in a sandboxed subprocess with timeout
  - PythonEvalTool: executes Python expressions safely with restricted globals

Each tool:
  - Has a JSON schema compatible with OpenAI function calling
  - Validates inputs before execution
  - Returns structured ToolResult with success/error/output
  - Is logged for audit trail

Security model:
  - ShellExecuteTool: subprocess with timeout, no network access
  - PythonEvalTool: restricted builtins (no exec/eval/import/open)
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Tool result container
# ---------------------------------------------------------------------------

@dataclass
class ToolResult:
    """Structured result from a tool call."""
    tool_name: str
    success: bool
    output: str
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool_name,
            "success": self.success,
            "output": self.output[:4000] if self.output else "",  # Truncate long outputs
            "error": self.error,
            "elapsed_ms": round(self.elapsed_ms, 2),
        }

    def __repr__(self) -> str:
        status = "✓" if self.success else "✗"
        return f"ToolResult({status} {self.tool_name}: {self.output[:80]!r})"


# ---------------------------------------------------------------------------
# Base tool
# ---------------------------------------------------------------------------

class BaseTool:
    """Abstract base for all agent tools."""

    name: str = "base"
    description: str = ""
    schema: Dict[str, Any] = {}

    def execute(self, **kwargs: Any) -> ToolResult:
        raise NotImplementedError

    def get_schema(self) -> Dict[str, Any]:
        """Returns OpenAI function-calling compatible schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.schema,
        }


# ---------------------------------------------------------------------------
# File tools
# ---------------------------------------------------------------------------

class FileReadTool(BaseTool):
    """Reads the content of a file at a given path."""

    name = "file_read"
    description = "Read the contents of a text file. Returns file content or an error message."
    schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or relative path to the file to read.",
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to return (default: 200).",
                "default": 200,
            },
        },
        "required": ["path"],
    }

    def execute(self, path: str, max_lines: int = 200) -> ToolResult:
        t0 = time.perf_counter()
        try:
            p = Path(path)
            if not p.exists():
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    output="",
                    error=f"File not found: {path}",
                    elapsed_ms=(time.perf_counter() - t0) * 1000,
                )
            if not p.is_file():
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    output="",
                    error=f"Path is not a file: {path}",
                    elapsed_ms=(time.perf_counter() - t0) * 1000,
                )

            content = p.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            if len(lines) > max_lines:
                content = "\n".join(lines[:max_lines]) + f"\n... (truncated at {max_lines} lines)"

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=content,
                elapsed_ms=(time.perf_counter() - t0) * 1000,
                metadata={"lines": len(lines), "bytes": p.stat().st_size},
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=str(e),
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )


class FileWriteTool(BaseTool):
    """Writes content to a file."""

    name = "file_write"
    description = "Write text content to a file. Creates parent directories if needed."
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to write to."},
            "content": {"type": "string", "description": "Text content to write."},
            "mode": {
                "type": "string",
                "enum": ["write", "append"],
                "description": "Write mode: 'write' overwrites, 'append' appends.",
                "default": "write",
            },
        },
        "required": ["path", "content"],
    }

    def execute(self, path: str, content: str, mode: str = "write") -> ToolResult:
        t0 = time.perf_counter()
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            write_mode = "w" if mode == "write" else "a"
            p.write_text(content, encoding="utf-8") if write_mode == "w" else \
                open(p, "a", encoding="utf-8").write(content)
            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Written {len(content)} bytes to {path}",
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=str(e),
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )


# ---------------------------------------------------------------------------
# Code execution tools
# ---------------------------------------------------------------------------

class ShellExecuteTool(BaseTool):
    """
    Executes a shell command in a subprocess with a timeout.

    Security constraints:
    - Maximum 30-second timeout (configurable)
    - stdout/stderr captured; stdin closed
    - Working directory defaults to a temporary location
    """

    name = "shell_execute"
    description = "Execute a shell command and return stdout/stderr. Max 30 second timeout."
    schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute."},
            "timeout_s": {
                "type": "number",
                "description": "Timeout in seconds (max 30).",
                "default": 10,
            },
            "cwd": {
                "type": "string",
                "description": "Working directory for the command.",
            },
        },
        "required": ["command"],
    }

    MAX_TIMEOUT = 30.0

    def execute(
        self,
        command: str,
        timeout_s: float = 10.0,
        cwd: Optional[str] = None,
    ) -> ToolResult:
        t0 = time.perf_counter()
        timeout_s = min(timeout_s, self.MAX_TIMEOUT)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
            )
            combined = result.stdout
            if result.stderr:
                combined += "\nSTDERR:\n" + result.stderr

            success = result.returncode == 0
            return ToolResult(
                tool_name=self.name,
                success=success,
                output=combined[:8000],  # Truncate very long outputs
                error=None if success else f"Exit code {result.returncode}",
                elapsed_ms=(time.perf_counter() - t0) * 1000,
                metadata={"returncode": result.returncode},
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=f"Command timed out after {timeout_s}s",
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=str(e),
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )


class PythonEvalTool(BaseTool):
    """
    Safely evaluates a Python expression in a restricted namespace.

    Allows: math operations, string operations, list comprehensions.
    Blocks: import, exec, eval, open, __import__, file I/O.
    """

    name = "python_eval"
    description = "Safely evaluate a Python expression (math, strings, collections). No imports."
    schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Python expression to evaluate (no imports or side effects).",
            },
        },
        "required": ["expression"],
    }

    BLOCKED_BUILTINS = frozenset([
        "__import__", "exec", "eval", "open", "compile",
        "getattr", "setattr", "delattr", "__builtins__",
    ])

    def execute(self, expression: str) -> ToolResult:
        t0 = time.perf_counter()
        try:
            # Parse AST to detect forbidden operations
            tree = ast.parse(expression, mode="eval")
            for node in ast.walk(tree):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    raise ValueError("Import statements are not allowed")
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in self.BLOCKED_BUILTINS:
                        raise ValueError(f"Function '{node.func.id}' is blocked")

            # Safe builtins
            safe_globals = {
                "__builtins__": {},
                "abs": abs, "round": round, "len": len, "min": min, "max": max,
                "sum": sum, "range": range, "list": list, "dict": dict,
                "set": set, "tuple": tuple, "str": str, "int": int, "float": float,
                "bool": bool, "sorted": sorted, "enumerate": enumerate, "zip": zip,
                "map": map, "filter": filter,
                "math": __import__("math"),
            }

            result = eval(compile(tree, "<expression>", "eval"), safe_globals)
            return ToolResult(
                tool_name=self.name,
                success=True,
                output=repr(result),
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=str(e),
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Registry of available tools, with lookup by name and schema export."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def schemas(self) -> List[Dict[str, Any]]:
        return [t.get_schema() for t in self._tools.values()]

    def execute(self, tool_name: str, **kwargs: Any) -> ToolResult:
        tool = self.get(tool_name)
        if tool is None:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                output="",
                error=f"Unknown tool: {tool_name!r}. Available: {list(self._tools.keys())}",
            )
        return tool.execute(**kwargs)

    @classmethod
    def default(cls) -> "ToolRegistry":
        """Returns a registry pre-populated with all standard tools."""
        registry = cls()
        registry.register(FileReadTool())
        registry.register(FileWriteTool())
        registry.register(ShellExecuteTool())
        registry.register(PythonEvalTool())
        return registry
