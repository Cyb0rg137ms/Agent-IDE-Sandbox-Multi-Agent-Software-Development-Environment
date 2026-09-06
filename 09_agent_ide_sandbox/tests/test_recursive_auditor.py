"""
test_recursive_auditor.py
=========================
Tests for RigorousAuditor and recursive fixed-point convergence (OO_{k+1} == OO_k).
"""

import pytest
from agent_core.logos.recursive_auditor import RigorousAuditor, AuditReport
from agent_core.operator_interface import SandboxOperatorInterface, SandboxSessionReport


class TestRigorousAuditor:
    def test_detect_flaws_in_buggy_code(self):
        auditor = RigorousAuditor()
        # Code missing zero-divisor check
        buggy_code = "def divide(a, b):\n    return a / b"
        report = auditor.audit(buggy_code, "write a divide function")

        assert isinstance(report, AuditReport)
        assert report.is_converged is False
        assert any("zero" in issue.lower() for issue in report.detected_issues)
        assert report.score < 10.0

    def test_converged_on_correct_code(self):
        auditor = RigorousAuditor()
        # Code with zero division check
        correct_code = "def divide(a, b):\n    if b == 0:\n        return 0\n    return a / b"
        report = auditor.audit(correct_code, "write a divide function")

        assert isinstance(report, AuditReport)
        assert report.is_converged is True
        assert len(report.detected_issues) == 0
        assert report.score == 10.0

    def test_game_audit_checks(self):
        auditor = RigorousAuditor()
        # Incomplete game code missing requestAnimationFrame
        incomplete_game = "<html><body><canvas id='c'></canvas><script>let x = 1;</script></body></html>"
        report = auditor.audit(incomplete_game, "build a game")

        assert report.is_converged is False
        assert any("animation" in iss.lower() or "loop" in iss.lower() for iss in report.detected_issues)

    def test_recursive_operator_convergence(self):
        operator = SandboxOperatorInterface(provider_name="mock", enable_logos=True)
        report = operator.solve_task("write a divide function")

        assert isinstance(report, SandboxSessionReport)
        assert report.status == "success"
        # Dual-pass guarantee: OO_1 -> OO_2 -> OO_3
        assert report.convergence_rounds == 2
        assert report.fixed_point_reached is True
        assert len(report.audit_history) == 2
        assert report.audit_history[0]["iteration"] == 1
        assert report.audit_history[1]["iteration"] == 2
        data = report.to_dict()
        assert data["convergence_rounds"] == 2
        assert data["fixed_point_reached"] is True
        assert len(data["audit_history"]) == 2
        assert "def divide" in report.final_code

