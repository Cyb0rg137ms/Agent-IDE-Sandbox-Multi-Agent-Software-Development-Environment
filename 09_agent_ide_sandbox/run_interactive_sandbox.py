"""
run_interactive_sandbox.py
==========================
Interactive Operator Console for Agent-IDE Sandbox.
Couples local GGUF models (via Ollama / llama.cpp) and Frontier APIs (OpenAI, Claude, Grok, Gemini)
to the Claude-Lightyear v10.0 Ultra / LOGOS cognitive sandbox architecture.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from agent_core.llm import (
    LLMRegistry,
    BaseLLMProvider,
    OllamaProvider,
    MockLLMProvider,
)
from agent_core.operator_interface import SandboxOperatorInterface


def print_banner():
    print(r"""
================================================================================
   _       ___   ____  ____   ____     _____ ___    _   ______  ____  ____ _  __
  | |     / / | / / / / / /  / __ \   / ___//   |  / | / / __ \/ __ )/ __ \ |/ /
  | | /| / / / / / / / / /  / /_/ /   \__ \/ /| | /  |/ / / / / __  / / / /   / 
  | |/ |/ / /_/ / /_/ / /___/ _, _/   ___/ / ___ |/ /|  / /_/ / /_/ / /_/ /   |  
  |__/|__/\____/\____/_____/_/ |_|   /____/_/  |_/_/ |_/_____/_____/\____/_/|_|  
                                                                               
   Claude-Lightyear v10.0 Ultra / LOGOS Cognitive Engine & Universal LLM Sandbox
================================================================================
    """)


def detect_environment_status():
    print("[SYSTEM ENVIRONMENT AUDIT]")
    # Check Ollama
    ollama = OllamaProvider()
    if ollama.is_available():
        models = ollama.list_local_models()
        print(f"  [✓] Local Ollama Runtime: ONLINE at {ollama.host}")
        print(f"      Installed GGUF Models: {models if models else 'None pulled yet'}")
    else:
        print("  [✗] Local Ollama Runtime: OFFLINE (run `ollama serve` to activate)")

    # Check Cloud API Keys
    keys = {
        "OpenAI API": bool(os.getenv("OPENAI_API_KEY")),
        "Anthropic Claude API": bool(os.getenv("ANTHROPIC_API_KEY")),
        "xAI Grok API": bool(os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")),
        "Google Gemini API": bool(os.getenv("GEMINI_API_KEY")),
    }
    for provider, available in keys.items():
        status = "CONFIGURED (Key detected)" if available else "UNCONFIGURED (Key not in env)"
        mark = "✓" if available else "•"
        print(f"  [{mark}] {provider}: {status}")
    print("  [✓] High-Fidelity Mock Engine: ALWAYS AVAILABLE (Zero-key testing)\n")


def prompt_provider_selection() -> BaseLLMProvider:
    print("Select LLM Execution Provider:")
    print("  1. Local Ollama GGUF (e.g. qwen2.5-coder, deepseek-r1, llama3.2)")
    print("  2. OpenAI API (e.g. gpt-4o, o3-mini)")
    print("  3. Anthropic Claude API (e.g. claude-3-7-sonnet, claude-3-5-sonnet)")
    print("  4. xAI Grok API (e.g. grok-2-latest)")
    print("  5. Google Gemini API (e.g. gemini-1.5-flash, gemini-2.0)")
    print("  6. Local OpenAI-compatible server (llama.cpp server / LM Studio)")
    print("  7. High-Fidelity Mock Provider (Deterministic simulation)")
    
    choice = input("\nEnter choice [1-7] (default: 7): ").strip() or "7"

    if choice == "1":
        ollama = OllamaProvider()
        models = ollama.list_local_models()
        default_m = models[0] if models else "qwen2.5-coder:7b"
        model = input(f"Enter Ollama model name (default: {default_m}): ").strip() or default_m
        host = input("Enter Ollama host (default: http://localhost:11434): ").strip() or "http://localhost:11434"
        return OllamaProvider(model_name=model, host=host)

    elif choice == "2":
        model = input("Enter OpenAI model name (default: gpt-4o): ").strip() or "gpt-4o"
        key = input("Enter OPENAI_API_KEY (press enter if already set in environment): ").strip()
        return LLMRegistry.get_provider("openai", model_name=model, api_key=key or None)

    elif choice == "3":
        model = input("Enter Claude model name (default: claude-3-7-sonnet-20250219): ").strip() or "claude-3-7-sonnet-20250219"
        key = input("Enter ANTHROPIC_API_KEY (press enter if already set in environment): ").strip()
        return LLMRegistry.get_provider("claude", model_name=model, api_key=key or None)

    elif choice == "4":
        model = input("Enter Grok model name (default: grok-2-latest): ").strip() or "grok-2-latest"
        key = input("Enter XAI_API_KEY (press enter if already set in environment): ").strip()
        return LLMRegistry.get_provider("grok", model_name=model, api_key=key or None)

    elif choice == "5":
        model = input("Enter Gemini model name (default: gemini-1.5-flash): ").strip() or "gemini-1.5-flash"
        key = input("Enter GEMINI_API_KEY (press enter if already set in environment): ").strip()
        return LLMRegistry.get_provider("gemini", model_name=model, api_key=key or None)

    elif choice == "6":
        url = input("Enter local server base URL (default: http://localhost:8080/v1): ").strip() or "http://localhost:8080/v1"
        model = input("Enter model name (default: local-model): ").strip() or "local-model"
        return LLMRegistry.get_provider("local", model_name=model, base_url=url)

    else:
        return MockLLMProvider(model_name="mock-developer-v1")


def interactive_session():
    print_banner()
    detect_environment_status()

    provider = prompt_provider_selection()
    print(f"\n[ACTIVE] Connected Provider: {provider.provider_name.upper()} | Model: {provider.model_name}")

    logos_toggle = input("Enable Claude-Lightyear v10.0 Ultra / LOGOS cognitive stack? [Y/n]: ").strip().lower()
    enable_logos = (logos_toggle != "n")

    operator = SandboxOperatorInterface(llm=provider, enable_logos=enable_logos)

    sample_tasks = [
        "Write a safe division function 'divide(a, b)' that handles zero divisor inputs.",
        "Write an array index lookup function 'get_element(arr, idx)' that safely returns None if index is out of bounds.",
        "Implement an iterative prime sieve with recursive boundary pruning.",
    ]

    while True:
        print("\n" + "=" * 60)
        print("Choose a task or enter your custom instruction:")
        for idx, t in enumerate(sample_tasks, 1):
            print(f"  {idx}. {t}")
        print("  0. Custom task")
        print("  q. Quit")

        cmd = input("\nSelect [0-3/q]: ").strip()
        if cmd.lower() in ["q", "quit", "exit"]:
            print("Exiting Agent-IDE Sandbox. Goodbye!")
            break

        if cmd in ["1", "2", "3"]:
            task = sample_tasks[int(cmd) - 1]
        elif cmd == "0":
            task = input("Enter custom task description: ").strip()
            if not task:
                continue
        else:
            task = cmd

        print(f"\n[RUNNING TASK] '{task}'")
        report = operator.solve_task(task)

        print("\n" + "-" * 60)
        print(f"SESSION EXECUTION REPORT [{report.status.upper()}]")
        print("-" * 60)
        print(f"Provider / Model:       {report.provider} ({report.model})")
        print(f"Total Loop Iterations:  {report.iterations}")
        print(f"Selected NAS Topology:  {report.topology_used}")
        print(f"Qualified Invariants:   {report.qualified_properties_count} (Confidence >= 95%)")
        print(f"Holographic Memory:     {report.holographic_stats['total_records']} traces, {report.holographic_stats['compression_ratio']}x compression")
        print(f"Execution Latency:      {report.elapsed_time_s}s")
        print(f"Security Audit:         {report.review.get('security_check', 'N/A')}")
        print(f"Style Score:            {report.review.get('style_score', 'N/A')}/10.0")

        print("\n[Synthesized Python Code]:")
        print("```python")
        print(report.final_code.strip())
        print("```")

        print("\n[Sandbox Execution Logs]:")
        print(report.test_logs.strip())
        print("=" * 60)


if __name__ == "__main__":
    interactive_session()
