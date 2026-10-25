from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from server.web_server import AgentIDERequestHandler, AgentIDEServer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent-IDE Sandbox & LOGOS Web Chatbot UI")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--provider", type=str, default=None, help="e.g. ollama, openai, anthropic, mock"
    )
    parser.add_argument("--model", type=str, default=None, help="model tag for the provider")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    manager = AgentIDERequestHandler.session_manager
    # Previously --provider/--model were only printed; they now configure the runtime.
    settings = {k: v for k, v in (("provider", args.provider), ("model", args.model)) if v}
    if settings:
        manager.update_settings(settings)
    server = AgentIDEServer(host=args.host, port=args.port)
    url = f"http://{args.host}:{args.port}"
    print("=" * 65)
    print("   AGENT-IDE SANDBOX — LOGOS ULTRA CHATBOT INTERFACE")
    print(f"   Server listening at: {url}")
    print(f"   Provider: {manager.provider_name} / {manager.model_name}")
    print("   Press Ctrl+C to terminate.")
    print("=" * 65)
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    server.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
