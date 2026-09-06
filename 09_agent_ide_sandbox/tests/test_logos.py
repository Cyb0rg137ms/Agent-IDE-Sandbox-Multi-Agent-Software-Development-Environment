"""
test_logos.py
=============
Unit tests for Claude-Lightyear v10.0 Ultra & LOGOS cognitive modules:
  - Level 0: MasterIndexDecomposer & Subquestion Taxonomy
  - Level 1 & 2: DualFrameworkConvergenceEngine & Property Alignment
  - Layer 1: AxiomaticEngine & Invariant Verification
  - Layer 2: FractalReasoningEngine (MERA Multiscale Coarse-Graining)
  - Layer 3: HolographicMemoryEngine (Boundary-to-Bulk Projection)
  - Layer 4: NASTopologyEngine (Dynamic Cognitive Topology)
  - Layer 5: DynamicAxiomRetriever (Corpus & Web Ingestion)
  - Layer 6: PonderingEngine (Horizontal Multi-Angle & 95%+ Confidence Filtering)
"""

import pytest
from agent_core.logos import (
    MasterIndexDecomposer,
    DualFrameworkConvergenceEngine,
    AxiomaticEngine,
    FractalReasoningEngine,
    HolographicMemoryEngine,
    NASTopologyEngine,
    DynamicAxiomRetriever,
    PonderingEngine,
    TopologyType,
)


class TestMasterIndexDecomposer:
    def test_decomposition(self):
        decomposer = MasterIndexDecomposer()
        subqs = decomposer.decompose("Write safe division function")
        assert len(subqs) == 5
        assert subqs[0].id == "SQ-1"
        assert "Information Structure" in subqs[0].dimension

    def test_topological_sort(self):
        decomposer = MasterIndexDecomposer()
        subqs = decomposer.decompose("Write safe division function")
        sorted_qs = decomposer.topological_sort(subqs)
        assert len(sorted_qs) == 5
        # SQ-1 should appear before SQ-2 and SQ-3
        ids = [sq.id for sq in sorted_qs]
        assert ids.index("SQ-1") < ids.index("SQ-2")
        assert ids.index("SQ-1") < ids.index("SQ-3")


class TestAxiomaticEngine:
    def test_core_axioms_loaded(self):
        engine = AxiomaticEngine()
        axioms = engine.list_axioms()
        assert len(axioms) >= 6
        assert any(ax.id == "AX_ARITH_DIV_ZERO" for ax in axioms)

    def test_consistency_check_division_guard(self):
        engine = AxiomaticEngine()
        # Failing case: division without guard
        bad_code = ["result = a / b"]
        consistent, violations = engine.verify_consistency(bad_code)
        assert consistent is False
        assert len(violations) > 0

        # Passing case: guarded division
        good_code = ["if b == 0: return 0", "return a / b"]
        consistent, violations = engine.verify_consistency(good_code)
        assert consistent is True
        assert len(violations) == 0

    def test_derive_requirements(self):
        engine = AxiomaticEngine()
        steps = engine.derive_requirements("safe division calculation")
        assert len(steps) >= 2
        assert any("AX_ARITH_DIV_ZERO" in s.rule_applied for s in steps)


class TestFractalReasoningEngine:
    def test_multiscale_mera_analysis(self):
        engine = FractalReasoningEngine()
        code = (
            "def safe_div(a, b):\n"
            "    '''Docstring.'''\n"
            "    if b == 0:\n"
            "        return 0\n"
            "    return a / b\n"
        )
        hierarchy = engine.analyze_code_multiscale(code)
        assert len(hierarchy[0]) > 0  # Tokens
        assert len(hierarchy[1]) >= 1  # Function & branch guards
        assert len(hierarchy[2]) >= 1  # Interface
        assert len(hierarchy[3]) >= 1  # Invariants

        summary = engine.coarse_grain_summary(hierarchy)
        assert "MERA FRACTAL REASONING" in summary


class TestHolographicMemoryEngine:
    def test_holographic_projection_and_recall(self):
        engine = HolographicMemoryEngine(dimension=64)
        engine.store("Zero division guard handles denominator equal to 0.", memory_id="trace_zero")
        engine.store("Array index bounds protection handles empty lists.", memory_id="trace_bounds")

        recalled = engine.associative_recall("denominator zero guard", top_k=1)
        assert len(recalled) == 1
        record, fidelity = recalled[0]
        assert record.id == "trace_zero"
        assert fidelity > 0.0

    def test_compression_metrics(self):
        engine = HolographicMemoryEngine(dimension=128)
        engine.store("A " * 500)
        stats = engine.get_boundary_compression_stats()
        assert stats["total_records"] == 1
        assert stats["raw_characters_stored"] >= 1000
        assert stats["compression_ratio"] > 0


class TestNASTopologyEngine:
    def test_simple_task_selects_pipeline(self):
        engine = NASTopologyEngine()
        topology = engine.search_optimal_topology("Write a helper to add two numbers")
        assert topology.topology_type == TopologyType.LINEAR_PIPELINE

    def test_complex_task_selects_dual_framework(self):
        engine = NASTopologyEngine()
        topology = engine.search_optimal_topology("Develop dual framework architecture with theory invariants")
        assert topology.topology_type == TopologyType.DUAL_FRAMEWORK

    def test_search_task_selects_tree_of_thought(self):
        engine = NASTopologyEngine()
        topology = engine.search_optimal_topology("Perform optimal search over heuristic tree space")
        assert topology.topology_type == TopologyType.TREE_OF_THOUGHT


class TestDynamicAxiomRetriever:
    def test_offline_retrieval_fallback(self):
        retriever = DynamicAxiomRetriever()
        results = retriever.search_duckduckgo("division by zero")
        assert len(results) > 0
        assert "division" in results[0].snippet.lower() or "zero" in results[0].snippet.lower()

    def test_extract_and_register_axioms(self):
        retriever = DynamicAxiomRetriever()
        extracted = retriever.extract_and_register_axioms("p-adic ultrametric")
        assert len(extracted) > 0
        assert extracted[0].confidence >= 0.95


class TestPonderingEngine:
    def test_horizontal_pondering_strict_threshold(self):
        engine = PonderingEngine()
        synthesis = engine.evaluate_multi_angle("Write safe division function")

        # Must evaluate angles and filter strictly on >= 95%
        assert synthesis.total_angles_evaluated >= 5
        assert synthesis.qualified_properties_count >= 3

        # All qualified properties must satisfy confidence >= 0.95
        for p in synthesis.qualified_properties:
            assert p.confidence >= 0.95
            assert p.passed_threshold is True

        # Speculative angle (< 0.95) must be rejected
        assert len(synthesis.rejected_properties) >= 1
        for p in synthesis.rejected_properties:
            assert p.confidence < 0.95
            assert p.passed_threshold is False

    def test_recursive_space_reduction(self):
        engine = PonderingEngine()
        calc = engine.compute_recursive_reduction(initial_space_bits=128, iterations=10, per_iter_reduction_pct=90.0)
        assert calc["iterations"] == 10
        assert calc["bits_eliminated"] > 30
        assert calc["remaining_bits"] < 128


class TestDualFrameworkConvergenceEngine:
    def test_convergence_protocol(self):
        engine = DualFrameworkConvergenceEngine()
        task = "safe division with zero handling"
        f1 = engine.analyze_framework_1_classical(task)
        f2 = engine.analyze_framework_2_theory2(task)

        assert f1.confidence >= 0.95
        assert f2.confidence >= 0.95

        matrix = engine.construct_property_alignment_matrix(f1, f2, task)
        assert len(matrix) >= 3

        backward = engine.backward_chain_from_goal("Zero exceptions in sandbox", matrix)
        assert len(backward) == 4

        spec = engine.synthesize_unified_specification(task, f1, f2, matrix)
        assert spec["dual_framework_congruence"] is True
        assert spec["overall_confidence"] >= 0.95
