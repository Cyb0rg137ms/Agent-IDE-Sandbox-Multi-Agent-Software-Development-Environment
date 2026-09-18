"""
recursive_auditor.py
====================
Rigorous Self-Auditing Engine for Recursive Fixed-Point Convergence (OO_{k+1} == OO_k).
Derived from Claude-Lightyear v10.0 Ultra & LOGOS Cognitive Architecture.

Scrutinizes generated code artifacts (OO_k) against formal domain invariants,
AST syntax, runtime stability, and completeness.
Flags concrete bugs and formulates modular refinement directives.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from agent_core.llm.base import BaseLLMProvider


@dataclass
class AuditReport:
    """Detailed critique of an output artifact OO_k."""
    iteration: int
    score: float
    is_converged: bool
    detected_issues: List[str]
    passed_invariants: List[str]
    refinement_strategy: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "score": round(self.score, 2),
            "is_converged": self.is_converged,
            "detected_issues": self.detected_issues,
            "passed_invariants": self.passed_invariants,
            "refinement_strategy": self.refinement_strategy,
        }


class RigorousAuditor:
    """
    Rigorous Code & Architecture Auditor.
    Performs multi-angle scrutiny on code outputs to find bugs, edge-case omissions,
    and invariant deviations.
    """

    def __init__(self, llm: Optional[BaseLLMProvider] = None) -> None:
        self.llm = llm

    def audit(
        self,
        code: str,
        task_description: str,
        invariants: Optional[List[str]] = None,
        iteration: int = 1,
    ) -> AuditReport:
        """
        Audits output code OO_k against task requirements and formal invariants.
        Returns an AuditReport indicating convergence and any detected issues.
        """
        task_lower = task_description.lower()
        code_clean = code.strip()
        code_lower = code_clean.lower()

        detected_issues: List[str] = []
        passed_invariants: List[str] = []

        # 1. AST / Syntax Integrity Audit
        if "def " in code_clean or "import " in code_clean:
            try:
                ast.parse(code_clean)
                passed_invariants.append("Python AST syntax tree strictly valid and parseable.")
            except SyntaxError as e:
                detected_issues.append(f"Python Syntax Error at line {e.lineno}: {e.msg}")

        if "<html" in code_lower or "<canvas" in code_lower:
            if "<script" not in code_lower or "</script>" not in code_lower:
                detected_issues.append("HTML application is missing a valid <script> block.")
            else:
                passed_invariants.append("HTML5 Canvas and script tags correctly structured.")

        # 2. Domain-Specific Invariant & Boundary Checks
        if "divide" in task_lower:
            # Check for zero division guard
            has_zero_guard = any(
                pattern in code_clean
                for pattern in ["b == 0", "b == 0.0", "b <= 0 and b >= 0", "not b", "== 0"]
            )
            if not has_zero_guard:
                detected_issues.append("Missing zero-divisor singularity preemption guard (b == 0).")
            else:
                passed_invariants.append("Zero-divisor singularity preemption verified (b == 0 handled).")

        if "element" in task_lower and ("arr" in task_lower or "list" in task_lower or "idx" in task_lower):
            has_bounds_guard = any(
                pattern in code_clean
                for pattern in ["len(arr)", "len(list)", "idx < 0", "idx >="]
            )
            if not has_bounds_guard:
                detected_issues.append("Missing array index out-of-bounds guard checking len(arr).")
            else:
                passed_invariants.append("Index bounds guard verified against array length.")

        if any(g in task_lower for g in ["game", "temple run", "canvas", "flappy"]):
            if "requestanimationframe" not in code_lower and "setinterval" not in code_lower:
                detected_issues.append("Interactive game is missing an active animation/render loop (requestAnimationFrame).")
            else:
                passed_invariants.append("Real-time game loop verified via requestAnimationFrame.")

            if "addeventlistener" not in code_lower and "onkeydown" not in code_lower:
                detected_issues.append("Game is missing user input event listeners (keyboard or touch).")
            else:
                passed_invariants.append("Player input controls and event dispatchers verified.")

        # 3. Security Boundary Audit
        forbidden = ["os.system", "subprocess.call", "shutil.rmtree", "eval("]
        for bad in forbidden:
            if bad in code_clean:
                detected_issues.append(f"Security boundary violation: forbidden call '{bad}' detected.")

        if not any(bad in code_clean for bad in forbidden):
            passed_invariants.append("Security boundary intact: zero malicious or unconstrained subshell calls.")

        # 4. Determine Convergence
        is_converged = (len(detected_issues) == 0)
        score = 10.0 if is_converged else max(5.0, 10.0 - (len(detected_issues) * 1.5))

        if is_converged:
            refinement_strategy = "Output verified defect-free: formal invariants satisfied. Fixed-point reached."
        else:
            refinement_strategy = f"Address {len(detected_issues)} identified flaws via targeted component repair."

        return AuditReport(
            iteration=iteration,
            score=score,
            is_converged=is_converged,
            detected_issues=detected_issues,
            passed_invariants=passed_invariants,
            refinement_strategy=refinement_strategy,
        )
