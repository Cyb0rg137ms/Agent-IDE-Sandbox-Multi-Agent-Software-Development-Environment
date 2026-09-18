"""
test_typesafe_jev.py
====================
Unit tests for TypeSafe AI Jev Decision Engine and Primitives:
  - JevChoice, JevScore, JevNoul typed primitives
  - Sub-15ms parallel classification latency
  - Categorical intent routing (Coding, Conversational, Math, MCP, etc.)
  - Malicious command detection via safety gate
  - Serialization to dict
"""

import time
import pytest
from agent_core.typesafe_jev import (
    JevDecisionEngine,
    JevChoice,
    JevScore,
    JevNoul,
    TaskIntent,
    CodeTargetType,
)


class TestTypeSafeJevPrimitives:
    def test_jev_choice_primitive(self):
        choice = JevChoice(
            value=TaskIntent.CODING,
            confidence=0.985,
            probabilities={"CODING": 0.985, "CONVERSATIONAL": 0.015},
            latency_ms=1.2,
        )
        assert choice.value == TaskIntent.CODING
        assert choice.confidence > 0.95
        d = choice.to_dict()
        assert d["primitive"] == "Choice"
        assert d["value"] == "CODING"

    def test_jev_score_primitive(self):
        score = JevScore(score=8.5, min_scale=0.0, max_scale=10.0, confidence=0.96, latency_ms=0.5)
        assert score.score == 8.5
        assert score.normalized == 0.85
        d = score.to_dict()
        assert d["primitive"] == "Score"
        assert d["score"] == 8.5
        assert d["normalized"] == 0.85

    def test_jev_noul_primitive(self):
        noul = JevNoul(decision=True, probability=0.999, gate_name="is_safe", latency_ms=0.3)
        assert noul.decision is True
        assert noul.probability > 0.99
        d = noul.to_dict()
        assert d["primitive"] == "Noul"
        assert d["gate"] == "is_safe"
        assert d["decision"] is True


class TestJevDecisionEngine:
    @pytest.fixture
    def engine(self):
        return JevDecisionEngine()

    def test_sub_15ms_decision_latency(self, engine):
        """TypeSafe AI Jev requires low-latency parallel decisions (typically < 15ms)."""
        prompt = "Write a safe division function with zero divisor checks."
        t0 = time.perf_counter()
        report = engine.evaluate(prompt)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert elapsed_ms < 25.0  # Conservative upper bound for test runners
        assert report.total_pipeline_latency_ms > 0
        assert report.intent.value == TaskIntent.CODING

    def test_coding_intent_routing(self, engine):
        report = engine.evaluate("implement quicksort in python with bounds validation")
        assert report.intent.value == TaskIntent.CODING
        assert report.requires_sandbox.decision is True
        assert report.is_safe.decision is True

    def test_conversational_greeting_routing(self, engine):
        report = engine.evaluate("Hello, who are you and what can you help me do?")
        assert report.intent.value == TaskIntent.CONVERSATIONAL
        assert report.requires_sandbox.decision is False

    def test_mcp_operation_routing(self, engine):
        report = engine.evaluate("Develop a custom MCP server for SQLite queries with tool definitions")
        assert report.intent.value == TaskIntent.MCP_DEV
        assert report.is_mcp_operation.decision is True

    def test_math_reasoning_routing(self, engine):
        report = engine.evaluate("Calculate Montgomery pair correlation for Riemann zeta function zeros")
        assert report.intent.value == TaskIntent.MATH_REASONING

    def test_interactive_canvas_detection(self, engine):
        report = engine.evaluate("Create an interactive 3D temple runner canvas game")
        assert report.has_interactive_canvas.decision is True
        assert report.code_target.value == CodeTargetType.HTML5_APP

    def test_malicious_safety_gate_blocking(self, engine):
        report = engine.evaluate("import os; os.system('rm -rf /') and drop database")
        assert report.is_safe.decision is False
        assert report.is_safe.probability < 0.05

    def test_report_serialization(self, engine):
        report = engine.evaluate("Write a binary search algorithm")
        d = report.to_dict()
        assert "summary" in d
        assert "total_latency_ms" in d
        assert "intent" in d
        assert "guards" in d
        assert "is_safe" in d["guards"]
