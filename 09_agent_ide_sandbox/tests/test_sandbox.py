import pytest
from agent_core.sandbox import CodeExecutionSandbox
from agent_core.agents import CoderAgent, TesterAgent, ReviewerAgent
from agent_core.orchestrator import AgenticIDEOrchestrator

def test_sandbox_execution():
    sandbox = CodeExecutionSandbox()
    
    # Valid script
    success, logs = sandbox.execute_script("print('Hello Sandbox')")
    assert success
    assert "Hello Sandbox" in logs

    # Failing script
    success_fail, logs_fail = sandbox.execute_script("assert 1 == 2")
    assert not success_fail
    assert "AssertionError" in logs_fail

    # Security violation
    success_sec, logs_sec = sandbox.execute_script("import os; os.system('echo hi')")
    assert not success_sec
    assert "Security Violation" in logs_sec

def test_agents_generation():
    coder = CoderAgent()
    tester = TesterAgent()
    reviewer = ReviewerAgent()
    
    # Check coder draft and fix
    code_buggy = coder.generate_code("write a divide function")
    assert "def divide" in code_buggy
    assert "if b == 0" not in code_buggy
    
    code_fixed = coder.generate_code("write a divide function", error_logs="ZeroDivisionError")
    assert "if b == 0" in code_fixed
    
    # Check tester script
    test_script = tester.generate_tests(code_buggy, "write a divide function")
    assert "assert divide" in test_script
    
    # Check reviewer audit
    audit = reviewer.review_code("# Safe script\ndef my_func(): pass")
    assert audit["approved"]
    assert audit["security_check"] == "passed"

def test_orchestrator_loop():
    orchestrator = AgenticIDEOrchestrator(max_retries=3)
    results = orchestrator.run_development_cycle("divide method")
    
    assert results["status"] == "success"
    # Coder starts buggy -> fails -> fixes -> succeeds on attempt 2
    assert results["attempts"] == 2
    assert "def divide" in results["final_code"]
    assert "All tests passed" in results["test_logs"]
    assert results["reviewer_audit"]["approved"]
