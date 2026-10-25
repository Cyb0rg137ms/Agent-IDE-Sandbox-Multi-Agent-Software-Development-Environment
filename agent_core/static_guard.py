"""AST-based pre-execution guard for generated Python code.

This is a *defence-in-depth filter*, not a sandbox: Python is too dynamic for static
analysis to be complete (e.g. ``getattr(__builtins__, "ev" + "al")``). It catches the
common direct forms of process spawning, shell access, destructive filesystem calls,
dynamic code execution and raw network/FFI access that a substring blocklist misses
(different spacing, aliases, ``from x import y``). Real isolation still requires a
container or VM.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

#: Modules whose import alone is rejected (process / network / FFI access).
BLOCKED_MODULES: frozenset[str] = frozenset(
    {"subprocess", "socket", "ctypes", "multiprocessing", "pty", "signal", "_thread"}
)
#: Builtins that execute dynamic code.
BLOCKED_BUILTINS: frozenset[str] = frozenset({"eval", "exec", "compile", "__import__"})
#: Dangerous attributes per module (call or reference).
BLOCKED_ATTRS: dict[str, frozenset[str]] = {
    "os": frozenset(
        {
            "system",
            "popen",
            "execv",
            "execve",
            "execl",
            "execlp",
            "execvp",
            "execvpe",
            "spawnl",
            "spawnv",
            "spawnve",
            "fork",
            "forkpty",
            "kill",
            "killpg",
            "remove",
            "unlink",
            "rmdir",
            "removedirs",
            "rename",
            "replace",
            "chmod",
            "chown",
            "putenv",
            "unsetenv",
        }
    ),
    "shutil": frozenset({"rmtree", "move", "chown", "copytree", "make_archive"}),
    "importlib": frozenset({"import_module", "__import__"}),
    "builtins": BLOCKED_BUILTINS,
    "pathlib": frozenset(),
}
#: Methods that are destructive regardless of receiver (``Path(...).unlink()``).
BLOCKED_METHODS: frozenset[str] = frozenset({"unlink", "rmdir", "rmtree", "chmod", "write_bytes"})


@dataclass(frozen=True)
class Violation:
    line: int
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"line {self.line}: {self.rule}: {self.detail}"


class _Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[Violation] = []
        self.aliases: dict[str, str] = {}  # local name -> module or module.attr

    def _add(self, node: ast.AST, rule: str, detail: str) -> None:
        self.violations.append(Violation(getattr(node, "lineno", 0), rule, detail))

    def visit_Import(self, node: ast.Import) -> None:
        for a in node.names:
            root = a.name.split(".")[0]
            self.aliases[a.asname or root] = a.name if a.asname else root
            if root in BLOCKED_MODULES:
                self._add(node, "blocked-import", a.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = (node.module or "").split(".")[0]
        if mod in BLOCKED_MODULES:
            self._add(node, "blocked-import", node.module or "")
        for a in node.names:
            if a.name in BLOCKED_ATTRS.get(mod, frozenset()) or (
                mod == "builtins" and a.name in BLOCKED_BUILTINS
            ):
                self._add(node, "blocked-attr", f"{mod}.{a.name}")
            self.aliases[a.asname or a.name] = f"{mod}.{a.name}"
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        target = self.aliases.get(node.id, node.id)
        if node.id in BLOCKED_BUILTINS and node.id not in self.aliases:
            self._add(node, "dynamic-exec", node.id)
        elif "." in target:
            mod, attr = target.split(".", 1)
            if attr in BLOCKED_ATTRS.get(mod, frozenset()):
                self._add(node, "blocked-attr", target)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name):
            mod = self.aliases.get(node.value.id, node.value.id).split(".")[0]
            if node.attr in BLOCKED_ATTRS.get(mod, frozenset()):
                self._add(node, "blocked-attr", f"{mod}.{node.attr}")
        if node.attr in BLOCKED_METHODS:
            self._add(node, "destructive-method", node.attr)
        if node.attr in {"__builtins__", "__subclasses__", "__globals__", "__code__"}:
            self._add(node, "introspection-escape", node.attr)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # getattr(obj, "system") style lookups with literal names
        if isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2:
            arg = node.args[1]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if any(arg.value in names for names in BLOCKED_ATTRS.values()):
                    self._add(node, "getattr-escape", arg.value)
        # open(..., "w"/"a") outside the sandbox cwd is not decidable statically; allowed.
        self.generic_visit(node)


def scan(code: str) -> list[Violation]:
    """Return guard violations for ``code``. Syntax errors are not violations (the
    interpreter will report them); an empty list means *no known-dangerous pattern*."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    v = _Visitor()
    v.visit(tree)
    return v.violations
