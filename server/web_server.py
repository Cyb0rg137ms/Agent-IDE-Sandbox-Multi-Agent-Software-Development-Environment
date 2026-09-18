"""
web_server.py
=============
Multi-threaded HTTP Server for Agent-IDE Sandbox Web UI.
Serves static frontend assets and REST API endpoints without external dependencies.
"""

from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
import urllib.parse

from server.handlers import ChatSessionManager


class AgentIDERequestHandler(BaseHTTPRequestHandler):
    """HTTP Request handler routing static assets and REST API endpoints."""

    session_manager = ChatSessionManager()
    static_dir = Path(__file__).parent.parent / "web"
    timeout = 300.0

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        """Helper to send JSON responses."""
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def _send_file(self, file_path: Path) -> None:
        """Helper to serve static files with correct MIME types."""
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "File not found")
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def do_OPTIONS(self) -> None:
        """Handles CORS preflight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Handles static file serving and GET API routes."""
        path = self.path.split("?")[0].rstrip("/")

        # API Endpoints
        if path == "/api/status":
            self._send_json(self.session_manager.get_status())
            return
        elif path == "/api/models":
            self._send_json(self.session_manager.get_models())
            return
        elif path == "/api/chats":
            self._send_json(self.session_manager.get_chats())
            return
        elif path == "/api/chats/load":
            query = self.path.split("?")[1] if "?" in self.path else ""
            chat_id = ""
            for param in query.split("&"):
                if param.startswith("id="):
                    chat_id = param.split("=")[1]
            chat_data = self.session_manager.load_chat(chat_id)
            if chat_data:
                self._send_json(chat_data)
            else:
                self._send_json({"error": "Chat not found"}, status=404)
            return
        elif path == "/api/projects":
            self._send_json(self.session_manager.get_projects())
            return
        elif path == "/api/artifacts":
            self._send_json(self.session_manager.get_artifacts())
            return
        elif path == "/api/mcp/presets":
            self._send_json(self.session_manager.get_mcp_presets())
            return
        elif path == "/api/ollama/status":
            self._send_json(self.session_manager.get_ollama_status())
            return
        elif path == "/api/ollama/gallery":
            self._send_json(self.session_manager.get_ollama_gallery())
            return
        elif path == "/api/ollama/pull":
            query = self.path.split("?")[1] if "?" in self.path else ""
            model_name = ""
            for param in query.split("&"):
                if param.startswith("model="):
                    model_name = urllib.parse.unquote(param.split("=")[1])
            if not model_name:
                self._send_json({"error": "Missing model parameter"}, status=400)
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            try:
                for event in self.session_manager.pull_ollama_model(model_name):
                    data = json.dumps(event)
                    self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    if event.get("done"):
                        break
            except Exception as e:
                err_data = json.dumps({"status": "error", "error": str(e), "done": True})
                try:
                    self.wfile.write(f"data: {err_data}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    pass
            return

        # Static Assets
        if path == "" or path == "/":
            self._send_file(self.static_dir / "index.html")
            return

        rel_path = path.lstrip("/")
        target_file = self.static_dir / rel_path
        if target_file.exists() and target_file.is_file():
            self._send_file(target_file)
        else:
            # Fallback to index.html for SPA routing
            self._send_file(self.static_dir / "index.html")

    def do_POST(self) -> None:
        """Handles API POST routes."""
        path = self.path.split("?")[0].rstrip("/")

        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            payload = json.loads(post_body)
        except Exception:
            payload = {}

        if path == "/api/chat":
            prompt = payload.get("prompt", "").strip()
            if not prompt:
                self._send_json({"error": "Prompt cannot be empty"}, status=400)
                return
            result = self.session_manager.process_chat(prompt)
            self._send_json(result)

        elif path == "/api/chat/stream":
            prompt = payload.get("prompt", "").strip()
            if not prompt:
                self._send_json({"error": "Prompt cannot be empty"}, status=400)
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.close_connection = True

            def on_progress(evt):
                try:
                    payload_evt = json.dumps({"type": "progress", "event": evt.to_dict() if hasattr(evt, "to_dict") else evt})
                    self.wfile.write(f"data: {payload_evt}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    pass

            try:
                result = self.session_manager.process_chat(prompt, progress_callback=on_progress)
                final_payload = json.dumps({"type": "final", "data": result})
                self.wfile.write(f"data: {final_payload}\n\n".encode("utf-8"))
                self.wfile.flush()
            except Exception as e:
                err_payload = json.dumps({"type": "error", "error": str(e)})
                try:
                    self.wfile.write(f"data: {err_payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    pass
            return

        elif path == "/api/settings":
            updated_status = self.session_manager.update_settings(payload)
            self._send_json(updated_status)

        elif path == "/api/clear":
            result = self.session_manager.clear_session()
            self._send_json(result)

        elif path == "/api/chats/save":
            res = self.session_manager.save_chat(payload)
            self._send_json(res)

        elif path == "/api/projects/create":
            res = self.session_manager.create_project(payload)
            self._send_json(res)

        elif path == "/api/mcp/generate":
            res = self.session_manager.generate_mcp_server(payload)
            self._send_json(res)

        elif path == "/api/mcp/test":
            res = self.session_manager.test_mcp_tool(payload)
            self._send_json(res)

        elif path == "/api/jev/decide":
            prompt = payload.get("prompt", "")
            res = self.session_manager.evaluate_jev(prompt)
            self._send_json(res)

        elif path == "/api/models/test":
            res = self.session_manager.test_connection()
            self._send_json(res)

        elif path == "/api/ollama/launch":
            res = self.session_manager.start_ollama_daemon()
            self._send_json(res)

        elif path == "/api/ollama/connect":
            model = payload.get("model", "gemma2:2b")
            res = self.session_manager.connect_ollama_model(model)
            self._send_json(res)

        else:
            self.send_error(404, "Endpoint not found")

    def log_message(self, format: str, *args: Any) -> None:
        """Suppresses default noisy access logs unless error."""
        try:
            if args and len(args) > 1 and str(args[1]) in ["404", "500"]:
                super().log_message(format, *args)
        except Exception:
            pass


class AgentIDEServer:
    """Server wrapper for ThreadingHTTPServer."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self.httpd: Optional[ThreadingHTTPServer] = None

    def start(self) -> None:
        import socket
        server_address = (self.host, self.port)
        self.httpd = ThreadingHTTPServer(server_address, AgentIDERequestHandler)
        
        # Probe local Ollama status
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        port_open = s.connect_ex(("127.0.0.1", 11434)) == 0
        s.close()
        status_str = "OPEN - Running" if port_open else "CLOSED"
        model_str = "qwen2.5-coder:1.5b" if port_open else "mock-developer-v1"

        print("============================================================")
        print("FINAL FIXED - Ollama Pipeline Attached")
        print(f"URL: http://{self.host}:{self.port}")
        print(f"Ollama Port 11434: {status_str}")
        print(f"Active Model: {model_str}")
        print("============================================================")
        print("[SERVER] Press Ctrl+C to stop.\n")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
            self.httpd.shutdown()


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = AgentIDEServer(host=host, port=port)
    server.start()


Server = AgentIDEServer
