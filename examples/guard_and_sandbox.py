"""Example: run generated code through the guard + sandbox."""

from agent_core.sandbox import CodeExecutionSandbox
from agent_core.static_guard import scan

snippets = {
    "ok": "def sq(x):\n    return x * x\nassert sq(3) == 9\nprint('passed')",
    "spawn": "import subprocess\nsubprocess.run(['id'])",
    "bypass-attempt": "from os import system as s\ns('id')",
}
sb = CodeExecutionSandbox(timeout_seconds=2.0)
for name, code in snippets.items():
    print(name, [str(v) for v in scan(code)])
    ok, logs = sb.execute_script(code)
    print("  ->", "PASS" if ok else "BLOCKED/FAILED", logs.strip()[:80])
