"""
run_sandbox.py
==============
Runs the multi-agent developer loop simulation.
Coordinates Coder, Tester, and Reviewer agents in a sandbox compile cycle.
"""

from agent_core.orchestrator import AgenticIDEOrchestrator

def run_agentic_loop_demo():
    print("==================================================")
    print("      AGENT-IDE-SANDBOX DEVELOPMENT PIPELINE      ")
    print("==================================================")
    
    orchestrator = AgenticIDEOrchestrator(max_retries=3)
    
    # Task definition
    task = "Write a safe division function 'divide(a, b)' that handles zero divisor inputs."
    
    # Run loop
    results = orchestrator.run_development_cycle(task)
    
    print("\n--------------------------------------------------")
    print("      DEVELOPMENT CYCLE EXECUTION METRICS         ")
    print("--------------------------------------------------")
    print(f"Status:             {results['status'].upper()}")
    print(f"Total loop retries: {results['attempts']}")
    
    if results['status'] == "success":
        print(f"Reviewer Audit:     APPROVED (Security: {results['reviewer_audit']['security_check']}, Style Score: {results['reviewer_audit']['style_score']})")
        print("\nFinal Synthesized Script:")
        print("-" * 35)
        print(results['final_code'].strip())
        print("-" * 35)
        print("\nTest Execution Logs:")
        print(results['test_logs'].strip())
    else:
        print(f"Error Logs:         {results['error_logs']}")
        
    print("==================================================")

if __name__ == "__main__":
    run_agentic_loop_demo()
