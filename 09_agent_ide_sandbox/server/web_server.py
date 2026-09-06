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

        elif path == "/api/settings":
            updated_status = self.session_manager.update_settings(payload)
            self._send_json(updated_status)

        elif path == "/api/clear":
            result = self.session_manager.clear_session()
            self._send_json(result)

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
        server_address = (self.host, self.port)
        self.httpd = ThreadingHTTPServer(server_address, AgentIDERequestHandler)
        print(f"\n[SERVER] Agent-IDE Sandbox Web UI active at: http://{self.host}:{self.port}")
        print("[SERVER] Press Ctrl+C to stop.\n")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
            self.httpd.shutdown()


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = AgentIDEServer(host=host, port=port)
    server.start()
