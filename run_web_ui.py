from __future__ import annotations
import argparse, sys, webbrowser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from server.web_server import AgentIDEServer, Server

def main():
    parser = argparse.ArgumentParser(description="Agent-IDE Sandbox & LOGOS Web Chatbot UI")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--provider", type=str, default="ollama")
    parser.add_argument("--model", type=str, default="qwen2.5-coder:1.5b")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    server = AgentIDEServer(host=args.host, port=args.port)
    url = f"http://{args.host}:{args.port}"
    print("=" * 65)
    print("   AGENT-IDE SANDBOX — LOGOS ULTRA CHATBOT INTERFACE")
    print(f"   Server listening at: {url}")
    print(f"   Provider: {args.provider} / {args.model}")
    print("   Press Ctrl+C to terminate.")
    print("=" * 65)
    if not args.no_browser:
        try: webbrowser.open(url)
        except: pass
    server.start()

if __name__ == "__main__":
    main()
