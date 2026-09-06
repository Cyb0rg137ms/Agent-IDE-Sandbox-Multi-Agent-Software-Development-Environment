"""
run_web_ui.py
=============
One-command launcher for the Agent-IDE Sandbox Web Chatbot UI.
Hosts the threaded HTTP server and opens the browser interface.
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from server.web_server import AgentIDEServer
from server.handlers import ChatSessionManager


def main():
    parser = argparse.ArgumentParser(description="Agent-IDE Sandbox & LOGOS Web Chatbot UI")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--provider", type=str, default="mock", help="Initial LLM provider (default: mock)")
    parser.add_argument("--model", type=str, default=None, help="Initial model name")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")

    args = parser.parse_args()

    # Pre-configure session manager defaults
    server = AgentIDEServer(host=args.host, port=args.port)
    if args.provider != "mock" or args.model:
        server.httpd_cls = None  # standard setup
        AgentIDEServer.session_manager = ChatSessionManager()
        AgentIDEServer.session_manager.update_settings({
            "provider": args.provider,
            "model": args.model,
        })

    url = f"http://{args.host}:{args.port}"
    print("=" * 65)
    print("   AGENT-IDE SANDBOX — LOGOS ULTRA CHATBOT INTERFACE")
    print(f"   Server listening at: {url}")
    print("   Press Ctrl+C to terminate.")
    print("=" * 65)

    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    server.start()


if __name__ == "__main__":
    main()
