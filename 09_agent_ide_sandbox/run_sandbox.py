"""
run_sandbox.py
==============
Runs the multi-agent developer loop and sandbox execution pipeline.
Supports both standard baseline mode and the Claude-Lightyear v10.0 Ultra / LOGOS
cognitive architecture powered by local models (Ollama GGUF) or Frontier APIs (OpenAI, Claude, Grok).
"""

from __future__ import annotations

import argparse
import sys
from agent_core.orchestrator import AgenticIDEOrchestrator
from agent_core.operator_interface import SandboxOperatorInterface
from agent_core.llm.registry import LLMRegistry


def run_agentic_loop_demo(
    provider: str = "mock",
    model: str = None,
    task: str = None,
    use_logos: bool = False,
    retries: int = 3,
):
    task = task or "Write a safe division function 'divide(a, b)' that handles zero divisor inputs."

    print("==================================================")
    print("      AGENT-IDE-SANDBOX DEVELOPMENT PIPELINE      ")
    print(f"      Provider: {provider.upper()} | LOGOS: {'ENABLED' if use_logos else 'DISABLED'} ")
    print("==================================================")

    # Initialize LLM provider
    llm = LLMRegistry.get_provider(provider, model_name=model)
    print(f"[BOOT] Initialized LLM Provider: {llm.provider_name} (model: {llm.model_name})")

    if use_logos:
        operator = SandboxOperatorInterface(llm=llm, enable_logos=True)
        report = operator.solve_task(task, max_retries=retries)

        print("\n--------------------------------------------------")
        print("      DEVELOPMENT CYCLE EXECUTION METRICS (LOGOS) ")
        print("--------------------------------------------------")
        print(f"Status:             {report.status.upper()}")
        print(f"Total loop retries: {report.iterations}")
        print(f"Selected Topology:  {report.topology_used}")
        print(f"Pondering Invariants: {report.qualified_properties_count} (>=95% confidence)")
        print(f"Holographic Memory: {report.holographic_stats['total_records']} traces, {report.holographic_stats['compression_ratio']}x compression")
        print(f"Elapsed Time:       {report.elapsed_time_s}s")

        if report.status == "success":
            print(f"Reviewer Audit:     APPROVED (Security: {report.review.get('security_check')}, Style Score: {report.review.get('style_score')})")
            print("\nFinal Synthesized Script:")
            print("-" * 35)
            print(report.final_code.strip())
            print("-" * 35)
            print("\nTest Execution Logs:")
            print(report.test_logs.strip())
        else:
            print(f"Error Logs:         {report.test_logs}")
    else:
        orchestrator = AgenticIDEOrchestrator(max_retries=retries, llm=llm, enable_logos=False)
        results = orchestrator.run_development_cycle(task)

        print("\n--------------------------------------------------")
        print("      DEVELOPMENT CYCLE EXECUTION METRICS         ")
        print("--------------------------------------------------")
        print(f"Status:             {results['status'].upper()}")
        print(f"Total loop retries: {results['attempts']}")

        if results["status"] == "success":
            print(f"Reviewer Audit:     APPROVED (Security: {results['reviewer_audit']['security_check']}, Style Score: {results['reviewer_audit']['style_score']})")
            print("\nFinal Synthesized Script:")
            print("-" * 35)
            print(results["final_code"].strip())
            print("-" * 35)
            print("\nTest Execution Logs:")
            print(results["test_logs"].strip())
        else:
            print(f"Error Logs:         {results['error_logs']}")

    print("==================================================")


def main():
    parser = argparse.ArgumentParser(description="Agent IDE Sandbox Developer Loop")
    parser.add_argument("--provider", type=str, default="mock", choices=["mock", "ollama", "openai", "anthropic", "claude", "grok", "gemini", "local"], help="LLM Provider")
    parser.add_argument("--model", type=str, default=None, help="Model name (e.g. qwen2.5-coder:7b, gpt-4o, claude-3-7-sonnet)")
    parser.add_argument("--task", type=str, default=None, help="Task description")
    parser.add_argument("--logos", action="store_true", help="Enable Claude-Lightyear v10.0 Ultra / LOGOS cognitive stack")
    parser.add_argument("--retries", type=int, default=3, help="Max retry attempts in sandbox loop")

    args = parser.parse_args()
    run_agentic_loop_demo(
        provider=args.provider,
        model=args.model,
        task=args.task,
        use_logos=args.logos,
        retries=args.retries,
    )


if __name__ == "__main__":
    main()
