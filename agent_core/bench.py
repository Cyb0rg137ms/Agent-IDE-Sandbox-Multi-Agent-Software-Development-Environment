"""Offline, reproducible benchmarks for Agent-IDE Sandbox (no model provider needed).

Measured:

1. **Code guard coverage**: a fixed corpus of dangerous and benign snippets is checked by
   the v1 substring blocklist alone and by v1 + the AST guard (``static_guard``).
2. **Sandbox execution**: wall time of ``CodeExecutionSandbox.execute_script`` for a trivial
   script (process spawn cost) and how quickly an infinite loop is killed by the timeout.
3. **Pipeline overhead**: ``SandboxOperatorInterface.solve_task`` with the deterministic
   *mock* provider. This is orchestration + sandbox time only. The mock returns canned
   answers, so its "success" says nothing about model quality and is not reported as such.
4. **HTTP control-plane latency** of the local server on an ephemeral loopback port.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import statistics
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

from agent_core.sandbox import LEGACY_BLOCKLIST, CodeExecutionSandbox
from agent_core.static_guard import scan

log = logging.getLogger("agent_ide.bench")

ATTACKS: dict[str, str] = {
    "os.system newline": "import os\nos.system('echo pwned')",
    "os.system v1 form": "import os; os.system('echo pwned')",
    "os alias": "import os as o\no.system('id')",
    "from os import system": "from os import system\nsystem('id')",
    "os.popen": "import os\nos.popen('id').read()",
    "subprocess.run": "import subprocess\nsubprocess.run(['id'])",
    "subprocess.call": "import subprocess\nsubprocess.call(['id'])",
    "from subprocess import Popen": "from subprocess import Popen\nPopen(['id'])",
    "shutil.rmtree": "import shutil\nshutil.rmtree('/tmp/x')",
    "os.remove": "import os\nos.remove('important.txt')",
    "Path.unlink": "from pathlib import Path\nPath('important.txt').unlink()",
    "eval": "eval('1+1')",
    "eval spaced": "eval ('1+1')",
    "exec": "exec('print(1)')",
    "__import__": "__import__('os').system('id')",
    "importlib": "import importlib\nimportlib.import_module('os').system('id')",
    "socket": "import socket\nsocket.create_connection(('example.com', 80))",
    "ctypes": "import ctypes\nctypes.CDLL(None)",
    "getattr literal": "import os\ngetattr(os, 'system')('id')",
    "subclasses escape": "().__class__.__base__.__subclasses__()",
    "os.fork": "import os\nos.fork()",
    "os.kill": "import os\nos.kill(1, 9)",
}

BENIGN: dict[str, str] = {
    "arithmetic": "print(sum(range(10)))",
    "function + assert": "def add(a, b):\n    return a + b\nassert add(2, 3) == 5",
    "os.path join": "import os\nprint(os.path.join('a', 'b'))",
    "os.getcwd": "import os\nprint(os.getcwd())",
    "pathlib read": "from pathlib import Path\nprint(Path('.').resolve().name)",
    "json": "import json\nprint(json.dumps({'a': 1}))",
    "math": "import math\nprint(math.sqrt(2))",
    "dataclass": "from dataclasses import dataclass\n@dataclass\nclass P:\n    x: int\nprint(P(1))",
    "unittest": "import unittest\nclass T(unittest.TestCase):\n    def test(self):\n        self.assertEqual(1, 1)\nunittest.main(exit=False)",
    "write temp file": "open('out.txt', 'w').write('hi')\nprint(open('out.txt').read())",
    "string 'evaluate'": "def evaluate(x):\n    return x * 2\nprint(evaluate(3))",
    "collections": "from collections import Counter\nprint(Counter('hello'))",
}

ENDPOINTS: tuple[str, ...] = ("/", "/api/status", "/api/models", "/api/chats", "/api/mcp/presets")


def _legacy_blocks(code: str) -> bool:
    return any(bad in code for bad in LEGACY_BLOCKLIST)


def run_guard_bench() -> dict[str, Any]:
    rows = []
    for kind, corpus in (("attack", ATTACKS), ("benign", BENIGN)):
        for name, code in corpus.items():
            t0 = time.perf_counter()
            v2 = _legacy_blocks(code) or bool(scan(code))
            dt = (time.perf_counter() - t0) * 1e6
            rows.append(
                {
                    "name": name,
                    "kind": kind,
                    "v1_blocked": _legacy_blocks(code),
                    "v2_blocked": v2,
                    "check_us": round(dt, 1),
                }
            )
    att = [r for r in rows if r["kind"] == "attack"]
    ben = [r for r in rows if r["kind"] == "benign"]
    return {
        "cases": rows,
        "attacks": len(att),
        "v1_attacks_blocked": sum(r["v1_blocked"] for r in att),
        "v2_attacks_blocked": sum(r["v2_blocked"] for r in att),
        "benign": len(ben),
        "v1_false_positives": sum(r["v1_blocked"] for r in ben),
        "v2_false_positives": sum(r["v2_blocked"] for r in ben),
    }


def run_sandbox_bench(runs: int = 20, timeout_s: float = 1.0) -> dict[str, Any]:
    sb = CodeExecutionSandbox(timeout_seconds=10.0)
    lat = []
    for _ in range(runs):
        t0 = time.perf_counter()
        ok, _ = sb.execute_script("print('ok')")
        lat.append((time.perf_counter() - t0) * 1e3)
        assert ok
    slow = CodeExecutionSandbox(timeout_seconds=timeout_s)
    t0 = time.perf_counter()
    ok, logs = slow.execute_script("while True:\n    pass")
    killed_after = time.perf_counter() - t0
    return {
        "runs": runs,
        "spawn_p50_ms": round(statistics.median(lat), 2),
        "spawn_max_ms": round(max(lat), 2),
        "timeout_s": timeout_s,
        "infinite_loop_killed_after_s": round(killed_after, 3),
        "infinite_loop_reported_failure": (not ok) and "timed out" in logs,
    }


PIPELINE_TASKS = (
    "Write a safe division function divide(a, b) that handles zero.",
    "Write a function fib(n) returning the nth Fibonacci number.",
    "Write a palindrome checker is_palindrome(s).",
    "Build a snake game in HTML canvas.",
)


def run_pipeline_bench(repeats: int = 3) -> dict[str, Any]:
    from agent_core.operator_interface import SandboxOperatorInterface

    op = SandboxOperatorInterface(provider_name="mock", enable_logos=True)
    out = {}
    for task in PIPELINE_TASKS:
        times, iters = [], []
        for _ in range(repeats):
            t0 = time.perf_counter()
            rep = op.solve_task(task)
            times.append((time.perf_counter() - t0) * 1e3)
            iters.append(rep.iterations)
        out[task] = {"median_ms": round(statistics.median(times), 2), "iterations": iters[-1]}
    return {"provider": "mock (canned responses)", "repeats": repeats, "tasks": out}


def run_http_bench(requests: int = 100) -> dict[str, Any]:
    from http.server import ThreadingHTTPServer

    from server.web_server import AgentIDERequestHandler

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), AgentIDERequestHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"

    def hit(p: str) -> float:
        t0 = time.perf_counter()
        with urllib.request.urlopen(base + p, timeout=10) as r:
            r.read()
        return (time.perf_counter() - t0) * 1e3

    res = {}
    try:
        for ep in ENDPOINTS:
            for _ in range(3):
                hit(ep)
            lat = sorted(hit(ep) for _ in range(requests))
            res[ep] = {
                "n": requests,
                "p50_ms": round(statistics.median(lat), 3),
                "p95_ms": round(lat[int(0.95 * (len(lat) - 1))], 3),
            }
    finally:
        httpd.shutdown()
        httpd.server_close()
    return res


def run_all(
    requests: int = 100, sandbox_runs: int = 20, pipeline_repeats: int = 3
) -> dict[str, Any]:
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)  # keep any runtime state out of the caller's directory
        try:
            return {
                "environment": {
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                    "cpu_count": os.cpu_count(),
                },
                "guard": run_guard_bench(),
                "sandbox": run_sandbox_bench(runs=sandbox_runs),
                "pipeline": run_pipeline_bench(repeats=pipeline_repeats),
                "http": run_http_bench(requests=requests),
            }
        finally:
            os.chdir(cwd)


def plot(res: dict[str, Any], out: str | Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    g = res["guard"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [3, 2]})
    att = [c for c in g["cases"] if c["kind"] == "attack"]
    names = [c["name"] for c in att]
    y = range(len(att))
    a1.barh(
        [i - 0.2 for i in y], [c["v1_blocked"] for c in att], 0.4, label="v1 substring blocklist"
    )
    a1.barh([i + 0.2 for i in y], [c["v2_blocked"] for c in att], 0.4, label="v2 (+ AST guard)")
    a1.set_yticks(list(y), names, fontsize=7)
    a1.invert_yaxis()
    a1.set_xticks([0, 1], ["allowed", "blocked"])
    a1.set_title(
        f"Dangerous snippets blocked: v1 {g['v1_attacks_blocked']}/{g['attacks']}, "
        f"v2 {g['v2_attacks_blocked']}/{g['attacks']}  "
        f"(benign false positives v1 {g['v1_false_positives']}/{g['benign']}, "
        f"v2 {g['v2_false_positives']}/{g['benign']})",
        fontsize=9,
    )
    a1.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2)
    h = res["http"]
    s = res["sandbox"]
    eps = list(h)
    a2.bar(range(len(eps)), [h[e]["p50_ms"] for e in eps], label="HTTP p50")
    a2.bar(
        range(len(eps)),
        [h[e]["p95_ms"] - h[e]["p50_ms"] for e in eps],
        bottom=[h[e]["p50_ms"] for e in eps],
        alpha=0.5,
        label="to p95",
    )
    a2.set_xticks(range(len(eps)), eps, rotation=25, ha="right", fontsize=8)
    a2.set_ylabel("ms")
    a2.set_title(
        f"Local API latency\nsandbox spawn p50 {s['spawn_p50_ms']} ms; "
        f"loop killed after {s['infinite_loop_killed_after_s']} s (limit {s['timeout_s']} s)",
        fontsize=8,
    )
    a2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="agent-ide-bench", description="Offline Agent-IDE benchmark")
    p.add_argument("--requests", type=int, default=100)
    p.add_argument("--sandbox-runs", type=int, default=20)
    p.add_argument("--pipeline-repeats", type=int, default=3)
    p.add_argument("--json", dest="json_out")
    p.add_argument("--plot")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING)
    res = run_all(a.requests, a.sandbox_runs, a.pipeline_repeats)
    text = json.dumps(res, indent=2)
    if a.json_out:
        Path(a.json_out).write_text(text + "\n")
    else:
        print(text)
    if a.plot:
        plot(res, a.plot)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
