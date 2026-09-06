"""
agents.py
=========
Defines the Developer, Tester, Reviewer, and LOGOS Cognitive agents.
Supports both deterministic baseline simulation (for zero-dependency testing)
and real LLM execution via local Ollama GGUF or Cloud APIs.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from agent_core.llm.base import BaseLLMProvider


class BaseAgent:
    """Base Agent class representing an LLM assistant."""

    def __init__(
        self,
        role: str,
        model_name: str = "gpt-4-mock",
        llm: Optional[BaseLLMProvider] = None,
    ) -> None:
        self.role = role
        self.model = model_name
        self.llm = llm

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generates a text completion based on role and prompt."""
        if self.llm:
            resp = self.llm.generate(prompt, system_prompt=f"Role: {self.role}\nContext: {context}")
            return resp.content
        return f"Simulation response from {self.role} for prompt: {prompt[:40]}"


class CoderAgent(BaseAgent):
    """Responsible for writing and fixing code files."""

    def __init__(self, llm: Optional[BaseLLMProvider] = None) -> None:
        super().__init__(role="Senior Software Engineer", llm=llm)

    def generate_code(self, task_description: str, error_logs: str = "") -> str:
        """
        Generates Python code to solve a task.
        If error logs are provided, it generates a corrected script.
        """
        if self.llm:
            if error_logs:
                prompt = (
                    f"Task: {task_description}\n"
                    f"Execution Failure Logs:\n{error_logs}\n"
                    "Fix the bug and provide the complete corrected Python code."
                )
            else:
                prompt = f"Task: {task_description}\nWrite clean, documented Python code to solve this task."
            resp = self.llm.generate(prompt, system_prompt=f"Role: {self.role}")
            code = self.llm.extract_code_block(resp.content, "python")
            return code if code else resp.content.strip()

        # Deterministic simulation fallback
        if error_logs:
            if "ZeroDivisionError" in error_logs:
                return (
                    "def divide(a, b):\n"
                    "    \"\"\"Divide a by b safely.\"\"\"\n"
                    "    if b == 0:\n"
                    "        return 0\n"
                    "    return a / b\n"
                )
            elif "IndexError" in error_logs:
                return (
                    "def get_element(arr, idx):\n"
                    "    \"\"\"Get element at index with bounds checking.\"\"\"\n"
                    "    if idx < 0 or idx >= len(arr):\n"
                    "        return None\n"
                    "    return arr[idx]\n"
                )
            else:
                return "def solve():\n    \"\"\"Solve task.\"\"\"\n    return 'Fixed generic error'"

        if "divide" in task_description.lower():
            return (
                "def divide(a, b):\n"
                "    \"\"\"Divide two numbers.\"\"\"\n"
                "    return a / b\n"
            )
        elif "element" in task_description.lower():
            return (
                "def get_element(arr, idx):\n"
                "    \"\"\"Get element at index.\"\"\"\n"
                "    return arr[idx]\n"
            )
        else:
            return "def solve():\n    return 'Hello World'"


class TesterAgent(BaseAgent):
    """Responsible for generating test scripts to validate code."""
    __test__ = False

    def __init__(self, llm: Optional[BaseLLMProvider] = None) -> None:
        super().__init__(role="Senior QA Engineer", llm=llm)

    def generate_tests(self, code_to_test: str, task_description: str) -> str:
        """Generates an executable python script to verify code functionality."""
        if self.llm:
            prompt = (
                f"Task: {task_description}\n"
                f"Code:\n```python\n{code_to_test}\n```\n"
                "Generate an executable test script asserting correctness. Include edge cases. Print 'All tests passed' on success."
            )
            resp = self.llm.generate(prompt, system_prompt=f"Role: {self.role}")
            tests = self.llm.extract_code_block(resp.content, "python")
            test_content = tests if tests else resp.content.strip()
            if code_to_test and ("def " not in test_content and "class " not in test_content):
                return f"{code_to_test}\n\n{test_content}"
            return test_content

        # Deterministic simulation fallback
        if "divide" in task_description.lower():
            return (
                f"{code_to_test}\n"
                "assert divide(6, 2) == 3\n"
                "assert divide(5, 0) == 0\n"
                "print('All tests passed')"
            )
        elif "element" in task_description.lower():
            return (
                f"{code_to_test}\n"
                "assert get_element([1, 2], 1) == 2\n"
                "assert get_element([1, 2], 5) is None\n"
                "print('All tests passed')"
            )
        else:
            return "print('No tests written')"


class ReviewerAgent(BaseAgent):
    """Responsible for auditing code quality and security."""

    def __init__(self, llm: Optional[BaseLLMProvider] = None) -> None:
        super().__init__(role="Principal Architect", llm=llm)

    def review_code(self, code: str) -> Dict[str, Any]:
        """Audits security and style parameters."""
        is_safe = "os.system" not in code and "eval" not in code
        has_docstring = '"""' in code or "'''" in code or "#" in code

        if self.llm:
            prompt = (
                f"Review this code for safety and style:\n```python\n{code}\n```\n"
                "Return JSON with: approved (bool), security_check (passed/failed), style_score (float)."
            )
            resp = self.llm.generate(prompt, system_prompt=f"Role: {self.role}")
            try:
                raw = resp.content
                if "{" in raw and "}" in raw:
                    raw = raw[raw.find("{"):raw.rfind("}") + 1]
                data = json.loads(raw)
                return {
                    "approved": bool(data.get("approved", is_safe and has_docstring)),
                    "security_check": data.get("security_check", "passed" if is_safe else "failed"),
                    "style_score": float(data.get("style_score", 9.0 if has_docstring else 5.0)),
                }
            except Exception:
                pass

        return {
            "approved": is_safe and has_docstring,
            "security_check": "passed" if is_safe else "failed",
            "style_score": 9.0 if has_docstring else 5.0,
        }


class PonderingAgent(BaseAgent):
    """LOGOS Agent specialized in horizontal thinking across 5 orthogonal angles."""

    def __init__(self, llm: Optional[BaseLLMProvider] = None) -> None:
        super().__init__(role="LOGOS Pondering Strategist", llm=llm)

    def ponder(self, task: str) -> Dict[str, Any]:
        from agent_core.logos.pondering_engine import PonderingEngine
        engine = PonderingEngine()
        synthesis = engine.evaluate_multi_angle(task)
        return {
            "summary": synthesis.synthesis_summary,
            "qualified_invariants": [p.to_dict() for p in synthesis.qualified_properties],
            "rejected_hypotheses": [p.to_dict() for p in synthesis.rejected_properties],
            "remaining_space_fraction": synthesis.remaining_search_space_fraction,
        }


class LogosArchitectAgent(BaseAgent):
    """LOGOS Cognitive Architect orchestrating MERA coarse-graining and Dual-Framework convergence."""

    def __init__(self, llm: Optional[BaseLLMProvider] = None) -> None:
        super().__init__(role="LOGOS Chief Cognitive Architect", llm=llm)

    def plan_architecture(self, task: str) -> Dict[str, Any]:
        from agent_core.logos.decomposition import MasterIndexDecomposer
        from agent_core.logos.convergence import DualFrameworkConvergenceEngine
        from agent_core.logos.nas_topology import NASTopologyEngine

        decomposer = MasterIndexDecomposer()
        convergence = DualFrameworkConvergenceEngine()
        nas = NASTopologyEngine()

        subquestions = decomposer.decompose(task)
        f1 = convergence.analyze_framework_1_classical(task)
        f2 = convergence.analyze_framework_2_theory2(task)
        alignment = convergence.construct_property_alignment_matrix(f1, f2, task)
        topology = nas.search_optimal_topology(task)

        return {
            "topology": topology.to_dict(),
            "subquestions": [sq.to_dict() for sq in subquestions],
            "framework_1": f1.to_dict(),
            "framework_2": f2.to_dict(),
            "alignment_matrix": [
                {
                    "dimension": e.dimension,
                    "synthesized_property": e.synthesized_property,
                    "congruence": e.congruence_score,
                }
                for e in alignment
            ],
        }
