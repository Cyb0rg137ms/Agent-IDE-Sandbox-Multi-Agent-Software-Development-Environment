import json

import pytest

from agent_core import bench
from agent_core.sandbox import CodeExecutionSandbox
from agent_core.static_guard import scan


@pytest.mark.parametrize("name", sorted(bench.ATTACKS))
def test_guard_blocks_attack_corpus(name):
    ok, logs = CodeExecutionSandbox().execute_script(bench.ATTACKS[name])
    assert not ok and "Security Violation" in logs


@pytest.mark.parametrize("name", sorted(bench.BENIGN))
def test_guard_allows_benign_corpus(name):
    assert scan(bench.BENIGN[name]) == []


def test_benign_code_still_runs():
    ok, logs = CodeExecutionSandbox().execute_script(bench.BENIGN["function + assert"])
    assert ok, logs


def test_known_bypass_is_documented_not_hidden():
    """Static analysis is incomplete: computed attribute names are NOT caught."""
    assert scan("import os\ngetattr(os, 'sys' + 'tem')('id')") == []


def test_guard_can_be_disabled_for_trusted_code():
    ok, _ = CodeExecutionSandbox(static_guard=False).execute_script("import socket\nprint(1)")
    assert ok


def test_syntax_error_is_not_a_violation():
    assert scan("def (") == []


def test_timeout_kills_infinite_loop():
    res = bench.run_sandbox_bench(runs=2, timeout_s=0.5)
    assert res["infinite_loop_reported_failure"]
    assert res["infinite_loop_killed_after_s"] < 3.0


def test_guard_bench_counts():
    g = bench.run_guard_bench()
    assert g["v2_attacks_blocked"] == g["attacks"]
    assert g["v2_false_positives"] == 0
    assert g["v1_attacks_blocked"] < g["attacks"]


def test_bench_cli(tmp_path):
    out, png = tmp_path / "b.json", tmp_path / "b.png"
    args = ["--requests", "3", "--sandbox-runs", "2", "--pipeline-repeats", "1"]
    assert bench.main([*args, "--json", str(out), "--plot", str(png)]) == 0
    d = json.loads(out.read_text())
    assert set(d) == {"environment", "guard", "sandbox", "pipeline", "http"}
    assert png.stat().st_size > 10_000


def test_cli_provider_flags_configure_runtime(monkeypatch):
    import run_web_ui
    from server.web_server import AgentIDERequestHandler, AgentIDEServer

    monkeypatch.setattr(AgentIDEServer, "start", lambda self: None)
    mgr = AgentIDERequestHandler.session_manager
    old = (mgr.provider_name, mgr.model_name)
    try:
        assert run_web_ui.main(["--no-browser", "--provider", "mock", "--model", "m-1"]) == 0
        assert (mgr.provider_name, mgr.model_name) == ("mock", "m-1")
    finally:
        mgr.update_settings({"provider": old[0], "model": old[1]})
