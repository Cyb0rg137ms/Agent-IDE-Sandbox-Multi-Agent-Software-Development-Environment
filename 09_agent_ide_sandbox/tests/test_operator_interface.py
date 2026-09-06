"""
test_operator_interface.py
===========================
Tests for SandboxOperatorInterface coupling LLMs to the execution sandbox.
Verifies tool execution, self-repair loops, session reporting, and holographic tracing.
"""

import pytest
from agent_core.operator_interface import SandboxOperatorInterface, SandboxSessionReport
from agent_core.llm import MockLLMProvider


class TestSandboxOperatorInterface:
    def test_solve_task_success_loop(self):
        operator = SandboxOperatorInterface(provider_name="mock", enable_logos=True)
        report = operator.solve_task("Write a safe division function 'divide(a, b)' that handles zero divisor inputs.")

        assert isinstance(report, SandboxSessionReport)
        assert report.status == "success"
        assert report.provider == "mock"
        assert "def divide" in report.final_code
        assert "if b == 0" in report.final_code
        assert report.iterations >= 1
        assert report.review["security_check"] == "passed"
        assert report.qualified_properties_count >= 3
        assert report.holographic_stats["total_records"] >= 2

    def test_execute_tool_via_interface(self):
        operator = SandboxOperatorInterface(provider_name="mock", enable_logos=True)
        res = operator.execute_tool("python_eval", expression="1 + 1")
        assert res.success is True
        assert res.output == "2"

    def test_switch_llm_provider(self):
        operator = SandboxOperatorInterface(provider_name="mock")
        assert operator.llm.provider_name == "mock"

        # Rebind to another mock instance or provider
        operator.set_llm("mock", model_name="custom-mock-v2")
        assert operator.llm.model_name == "custom-mock-v2"

    def test_report_serialization(self):
        operator = SandboxOperatorInterface(provider_name="mock")
        report = operator.solve_task("Write an element lookup function 'get_element(arr, idx)'")
        data = report.to_dict()

        assert "task" in data
        assert "status" in data
        assert "final_code" in data
        assert "holographic_compression" in data

    def test_temple_run_interactive_generation(self):
        operator = SandboxOperatorInterface(provider_name="mock", enable_logos=True)
        report = operator.solve_task("build a full working temple run game")
        assert report.status == "success"
        assert "<canvas" in report.final_code
        assert "requestanimationframe" in report.final_code.lower()
        assert "addeventlistener" in report.final_code.lower()
        assert "temple" in report.final_code.lower()
        assert report.convergence_rounds == 2

    def test_general_prompt_synthesis(self):
        operator = SandboxOperatorInterface(provider_name="mock", enable_logos=True)
        report = operator.solve_task("write a fibonacci function")
        assert report.status == "success"
        assert "def fibonacci" in report.final_code
        assert "return" in report.final_code
        assert "solve():" not in report.final_code
