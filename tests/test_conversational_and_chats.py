"""
test_conversational_and_chats.py
================================
Unit tests for ChatSessionManager extended features:
  - Rich conversational responses for greetings, zeta function, Higgs boson, knot theory
  - Chat history persistence and loading
  - Project management and creation
  - Artifacts cataloging
  - TypeSafe AI Jev evaluation endpoint
"""

import pytest
from server.handlers import ChatSessionManager


class TestChatSessionManagerExtended:
    @pytest.fixture
    def manager(self):
        mgr = ChatSessionManager()
        mgr.update_settings({"provider": "mock", "model": "mock-developer-v1"})
        return mgr

    def test_greeting_conversational_response(self, manager):
        res = manager.process_chat("Hello there, who are you?")
        assert res["type"] == "conversational"
        assert res["status"] == "success"
        assert "Agent-IDE Sandbox" in res["content"]
        assert "TypeSafe AI Jev" in res["content"] or "LOGOS" in res["content"]
        assert res["jev"] is not None
        assert res["jev"]["intent"]["value"] == "CONVERSATIONAL"

    def test_zeta_function_physics_query(self, manager):
        res = manager.process_chat("Explain the Zeta function and spectral physics Hilbert-Pólya conjecture")
        assert res["type"] == "conversational"
        assert "Hilbert-Pólya" in res["content"] or "Riemann" in res["content"]
        assert "Hamiltonian" in res["content"] or "GUE" in res["content"]

    def test_higgs_boson_guac_query(self, manager):
        res = manager.process_chat("What is the Higgs boson mass in the Φ-GUAC framework?")
        assert res["type"] == "conversational"
        assert "125" in res["content"] or "Higgs" in res["content"]

    def test_knot_theory_query(self, manager):
        res = manager.process_chat("Explain 3D knot theory Reidemeister moves")
        assert res["type"] == "conversational"
        assert "Reidemeister" in res["content"] or "Jones" in res["content"]

    def test_get_and_save_chats(self, manager):
        chats = manager.get_chats()
        assert len(chats) >= 0

        # Save a new chat
        save_res = manager.save_chat({
            "id": "chat-new-test",
            "title": "Quantum Error Correction",
            "turns": [{"prompt": "Design surface code lattice", "result": {"content": "Verified"}}]
        })
        assert save_res["status"] == "saved"
        assert manager.load_chat("chat-new-test")["title"] == "Quantum Error Correction"

        # Verify it was added
        chats = manager.get_chats()
        assert len(chats) >= 1

    def test_projects_crud(self, manager):
        projs = manager.get_projects()
        assert len(projs) >= 0

        # Create new project
        new_proj = manager.create_project({
            "title": "Superconductor Design Engine",
            "description": "High-Tc cuprate critical temperature predictor"
        })
        assert new_proj["title"] == "Superconductor Design Engine"
        assert manager.get_projects()[0]["title"] == "Superconductor Design Engine"

    def test_artifacts_tracking(self, manager):
        arts = manager.get_artifacts()
        assert len(arts) >= 2  # Initial starter artifacts
        titles = [a["title"] for a in arts]
        assert any("Temple Run" in t for t in titles)

        # Running a coding task adds an artifact
        manager.process_chat("Write a safe division function 'divide(a, b)' that handles zero divisor.")
        updated_arts = manager.get_artifacts()
        assert len(updated_arts) >= 3

    def test_evaluate_jev_endpoint(self, manager):
        jev_res = manager.evaluate_jev("Write a binary search function")
        assert "intent" in jev_res
        assert jev_res["intent"]["value"] == "CODING"
        assert "total_latency_ms" in jev_res
        assert jev_res["total_latency_ms"] < 25.0

    def test_mcp_api_methods(self, manager):
        presets = manager.get_mcp_presets()
        assert len(presets) >= 3

        gen_res = manager.generate_mcp_server({
            "server_name": "test-calc",
            "description": "Calculator MCP",
            "tools": [{
                "name": "add",
                "description": "Add 2 numbers",
                "parameters": [{"name": "a", "param_type": "number"}, {"name": "b", "param_type": "number"}],
                "handler_code": "return json.dumps({'res': kwargs.get('a', 0) + kwargs.get('b', 0)})"
            }]
        })
        assert gen_res["status"] == "success"
        assert "from mcp.server.fastmcp import FastMCP" in gen_res["python_code"]
        assert "claude_desktop_config" in gen_res

        # Test tool
        test_res = manager.test_mcp_tool({
            "tool": {
                "name": "add",
                "description": "Add 2 numbers",
                "parameters": [{"name": "a", "param_type": "number"}, {"name": "b", "param_type": "number"}],
                "handler_code": "return json.dumps({'res': kwargs.get('a', 0) + kwargs.get('b', 0)})"
            },
            "arguments": {"a": 10, "b": 25}
        })
        assert test_res["status"] == "success"
        assert "35" in test_res["stdout"]
