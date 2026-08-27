"""
orchestrator.py
===============
Coordinates the agentic coding loop: Coder, Tester, and Reviewer interaction 
with sandbox code execution.
"""

from typing import Dict, Any, Tuple
from agent_core.agents import CoderAgent, TesterAgent, ReviewerAgent
from agent_core.sandbox import CodeExecutionSandbox

class AgenticIDEOrchestrator:
    """Manages the iterative code generation, testing, and debugging loop."""
    
    def __init__(self, max_retries: int = 3):
        self.coder = CoderAgent()
        self.tester = TesterAgent()
        self.reviewer = ReviewerAgent()
        self.sandbox = CodeExecutionSandbox()
        self.max_retries = max_retries

    def run_development_cycle(self, task: str) -> Dict[str, Any]:
        """
        Runs the complete developer loop:
        1. Coder generates code.
        2. Tester generates validation scripts.
        3. Sandbox executes test script.
        4. If tests fail, Coder receives logs to debug/fix. Loop retries.
        5. If tests pass, Reviewer audits code.
        
        Args:
            task: Task description.
            
        Returns:
            Dictionary with final code, execution logs, and compilation status.
        """
        print(f"\n[ORCHESTRATOR] Starting development cycle for task: '{task}'")
        
        # Step 1: Initial draft generation
        code = self.coder.generate_code(task)
        error_logs = ""
        
        for attempt in range(self.max_retries):
            print(f"[ORCHESTRATOR] Attempt {attempt + 1:02d} - Validating code structure...")
            
            # Step 2: Generate test suite
            tests = self.tester.generate_tests(code, task)
            
            # Step 3: Execute in sandbox
            success, logs = self.sandbox.execute_script(tests, "test_runner.py")
            
            if success:
                print("[ORCHESTRATOR] Success! All tests passed in sandbox.")
                # Step 4: Code review
                review = self.reviewer.review_code(code)
                return {
                    "status": "success",
                    "attempts": attempt + 1,
                    "final_code": code,
                    "test_logs": logs,
                    "reviewer_audit": review
                }
            else:
                print(f"[ORCHESTRATOR] Test failed. Capturing execution error logs...")
                error_logs = logs
                # Feed error logs back to coder for repair
                code = self.coder.generate_code(task, error_logs)
                
        # Loop exhausted without success
        return {
            "status": "failed",
            "attempts": self.max_retries,
            "final_code": code,
            "error_logs": error_logs,
            "reviewer_audit": None
        }
