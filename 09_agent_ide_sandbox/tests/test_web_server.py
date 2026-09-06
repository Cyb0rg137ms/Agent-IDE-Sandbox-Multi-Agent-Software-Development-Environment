"""
test_web_server.py
==================
Unit and integration tests for Agent-IDE Sandbox Web UI and backend server:
  - ChatSessionManager status, model catalog, and settings update
  - Chat processing for code execution & conversational queries
  - Live HTTP server endpoint tests (/api/status, /api/models, /api/settings, /api/chat, static files)
"""

import json
import threading
import time
import urllib.error
import urllib.request
import pytest

from server.handlers import ChatSessionManager
from server.web_server import AgentIDEServer, AgentIDERequestHandler
from http.server import ThreadingHTTPServer


class TestChatSessionManager:
    def test_initial_status(self):
        manager = ChatSessionManager()
        status = manager.get_status()
        assert status["active_provider"] == "mock"
        assert "holographic_memory" in status
        assert status["conversation_turns"] == 0

    def test_get_models_catalog(self):
        manager = ChatSessionManager()
        models = manager.get_models()
        assert "presets" in models
        assert "mock" in models["presets"]
        assert "openai" in models["presets"]
        assert "claude" in models["presets"]

    def test_update_settings_dynamic(self):
        manager = ChatSessionManager()
        updated = manager.update_settings({
            "provider": "mock",
            "model": "custom-mock-test-v1",
            "enable_logos": True,
            "max_retries": 2,
        })
        assert updated["active_provider"] == "mock"
        assert updated["active_model"] == "custom-mock-test-v1"
        assert manager.max_retries == 2

    def test_process_chat_coding_task(self):
        manager = ChatSessionManager()
        res = manager.process_chat("Write a safe division function 'divide(a, b)' that handles zero divisor.")
        assert res["type"] == "code_execution"
        assert res["status"] == "success"
        assert res["code"] is not None
        assert "divide" in res["code"]
        assert res["thinking"] is not None
        assert "qualified_properties" in res["thinking"]
        assert len(res["thinking"]["qualified_properties"]) >= 3

    def test_process_chat_conversational_task(self):
        manager = ChatSessionManager()
        res = manager.process_chat("What is the principle of non-Archimedean ultrametric geometry?")
        assert res["type"] == "conversational"
        assert res["status"] == "success"
        assert res["content"] is not None
        assert "thinking" in res

    def test_clear_session(self):
        manager = ChatSessionManager()
        manager.process_chat("Sample query")
        assert len(manager.history) == 1
        clear_res = manager.clear_session()
        assert clear_res["status"] == "cleared"
        assert len(manager.history) == 0


class TestWebServerLiveEndpoints:
    @classmethod
    def setup_class(cls):
        """Starts a live HTTP server on localhost on a free port in a background thread."""
        cls.port = 8899
        cls.host = "127.0.0.1"
        cls.server_address = (cls.host, cls.port)
        cls.httpd = ThreadingHTTPServer(cls.server_address, AgentIDERequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.3)  # Allow server to bind

    @classmethod
    def teardown_class(cls):
        """Stops the background HTTP server."""
        try:
            cls.httpd.shutdown()
        except Exception:
            pass

    def test_get_index_html(self):
        url = f"http://{self.host}:{self.port}/"
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            assert resp.status == 200
            content = resp.read().decode("utf-8")
            assert "Agent-IDE" in content
            assert "LOGOS" in content

    def test_get_static_css(self):
        url = f"http://{self.host}:{self.port}/css/style.css"
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            assert resp.status == 200
            content = resp.read().decode("utf-8")
            assert ":root" in content
            assert "--bg-app" in content

    def test_api_status_endpoint(self):
        url = f"http://{self.host}:{self.port}/api/status"
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert "active_provider" in data

    def test_api_models_endpoint(self):
        url = f"http://{self.host}:{self.port}/api/models"
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert "presets" in data

    def test_api_chat_post_endpoint(self):
        url = f"http://{self.host}:{self.port}/api/chat"
        payload = json.dumps({"prompt": "Write a safe division function 'divide(a, b)'"}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "success"
            assert "code" in data

    def test_api_settings_post_endpoint(self):
        url = f"http://{self.host}:{self.port}/api/settings"
        payload = json.dumps({
            "provider": "mock",
            "model": "endpoint-test-model",
            "enable_logos": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["active_model"] == "endpoint-test-model"
