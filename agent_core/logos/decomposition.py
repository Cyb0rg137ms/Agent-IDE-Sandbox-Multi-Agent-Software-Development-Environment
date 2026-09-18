"""
decomposition.py
================
Level 0: Master Index & Subquestion Taxonomy Engine.
Derived from Claude-Lightyear v10.0 Ultra Framework (Level 0 Meta-Architecture).

Breaks down any meta-task into a structured taxonomy of hierarchical subquestions,
computes dependency topological order, and constructs the Master Index blueprint.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Subquestion:
    """A decomposed subquestion representing an angle of inquiry."""
    id: str
    dimension: str
    question: str
    dependencies: List[str] = field(default_factory=list)
    priority: int = 1
    properties_framework1: List[str] = field(default_factory=list)  # Classical
    properties_framework2: List[str] = field(default_factory=list)  # Theory 2
    confidence: float = 0.0
    resolved: bool = False
    findings: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dimension": self.dimension,
            "question": self.question,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "properties_f1": self.properties_framework1,
            "properties_f2": self.properties_framework2,
            "confidence": round(self.confidence, 4),
            "resolved": self.resolved,
            "findings": self.findings,
        }


class MasterIndexDecomposer:
    """
    Decomposes programming, mathematical, and algorithmic problems
    into the Lightyear v10.0 Level 0 Subquestion Taxonomy:
      - Dimension 1: Information Theory & Atomicity (Kolmogorov incompressibility, entropy)
      - Dimension 2: Complexity Bounds & Space Reducibility (O-bounds, recursivity)
      - Dimension 3: Boundary Invariants & Edge Singularities (zero-divisions, bounds, overflows)
      - Dimension 4: Operator Symmetries & Type Contracts (algebraic properties, interfaces)
      - Dimension 5: Execution Sandbox & Verification Criteria (unit tests, security audit)
    """

    TAXONOMY_DIMENSIONS = [
        ("DIM_INFO", "Information Structure & State Density"),
        ("DIM_COMPLEXITY", "Computational Complexity & Reducibility"),
        ("DIM_BOUNDARY", "Boundary Conditions & Invariant Singularities"),
        ("DIM_OPERATOR", "Operator Algebra & Interface Contract"),
        ("DIM_VERIFICATION", "Sandbox Execution & Formal Verification"),
    ]

    def decompose(self, meta_task: str) -> List[Subquestion]:
        """Decomposes a meta task into a structured list of subquestions."""
        task_clean = meta_task.strip()
        subquestions: List[Subquestion] = []

        # 1. Information Structure
        sq1 = Subquestion(
            id="SQ-1",
            dimension="Information Structure & State Density",
            question=f"What are the minimal irreducible state representations and input types for: '{task_clean}'?",
            dependencies=[],
            priority=1,
        )
        subquestions.append(sq1)

        # 2. Computational Complexity & Reducibility
        sq2 = Subquestion(
            id="SQ-2",
            dimension="Computational Complexity & Reducibility",
            question=f"What are the optimal algorithmic time/space bounds and can search space be pruned recursively for: '{task_clean}'?",
            dependencies=["SQ-1"],
            priority=2,
        )
        subquestions.append(sq2)

        # 3. Boundary Invariants
        sq3 = Subquestion(
            id="SQ-3",
            dimension="Boundary Conditions & Invariant Singularities",
            question=f"What boundary conditions, null/zero cases, overflows, or edge exceptions must be guarded against in: '{task_clean}'?",
            dependencies=["SQ-1"],
            priority=2,
        )
        subquestions.append(sq3)

        # 4. Operator Algebra & Interface Contract
        sq4 = Subquestion(
            id="SQ-4",
            dimension="Operator Algebra & Interface Contract",
            question=f"What function signatures, type invariants, and pure idempotence guarantees satisfy: '{task_clean}'?",
            dependencies=["SQ-2", "SQ-3"],
            priority=3,
        )
        subquestions.append(sq4)

        # 5. Sandbox Execution & Verification
        sq5 = Subquestion(
            id="SQ-5",
            dimension="Sandbox Execution & Formal Verification",
            question=f"What assertions and test harness prove 100% correct execution for: '{task_clean}'?",
            dependencies=["SQ-4"],
            priority=4,
        )
        subquestions.append(sq5)

        return subquestions

    def topological_sort(self, subquestions: List[Subquestion]) -> List[Subquestion]:
        """Sorts subquestions topologically based on dependency graphs."""
        sq_map = {sq.id: sq for sq in subquestions}
        visited = set()
        order = []

        def dfs(sq_id: str):
            if sq_id in visited or sq_id not in sq_map:
                return
            visited.add(sq_id)
            for dep_id in sq_map[sq_id].dependencies:
                dfs(dep_id)
            order.append(sq_map[sq_id])

        for sq in subquestions:
            dfs(sq.id)

        return order
