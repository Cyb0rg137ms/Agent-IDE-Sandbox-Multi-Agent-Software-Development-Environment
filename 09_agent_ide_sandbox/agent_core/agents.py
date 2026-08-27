"""
agents.py
=========
Defines the Developer, Tester, and Reviewer agents.
Includes mock generation profiles to allow testability without API keys,
along with support for real API endpoints.
"""

from typing import Dict, Any, List

class BaseAgent:
    """Base Agent class representing an LLM assistant."""
    
    def __init__(self, role: str, model_name: str = "gpt-4-mock"):
        self.role = role
        self.model = model_name

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generates a text completion based on role and prompt."""
        # Baseline simulation logic
        pass

class CoderAgent(BaseAgent):
    """Responsible for writing and fixing code files."""
    
    def __init__(self):
        super().__init__(role="Senior Software Engineer")

    def generate_code(self, task_description: str, error_logs: str = "") -> str:
        """
        Generates Python code to solve a task.
        If error logs are provided, it generates a corrected script.
        """
        if error_logs:
            # Code is failing: fix it
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
                
        # Generate initial draft based on task
        if "divide" in task_description.lower():
            # Initial buggy draft (missing divide-by-zero check)
            return (
                "def divide(a, b):\n"
                "    \"\"\"Divide two numbers.\"\"\"\n"
                "    return a / b\n"
            )
        elif "element" in task_description.lower():
            # Initial buggy draft (missing index boundaries check)
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
    
    def __init__(self):
        super().__init__(role="Senior QA Engineer")

    def generate_tests(self, code_to_test: str, task_description: str) -> str:
        """Generates an executable python script to verify code functionality."""
        if "divide" in task_description.lower():
            return (
                f"{code_to_test}\n"
                "assert divide(6, 2) == 3\n"
                "assert divide(5, 0) == 0\n" # Will trigger ZeroDivisionError in buggy draft
                "print('All tests passed')"
            )
        elif "element" in task_description.lower():
            return (
                f"{code_to_test}\n"
                "assert get_element([1, 2], 1) == 2\n"
                "assert get_element([1, 2], 5) is None\n" # Will trigger IndexError in buggy draft
                "print('All tests passed')"
            )
        else:
            return "print('No tests written')"

class ReviewerAgent(BaseAgent):
    """Responsible for auditing code quality and security."""
    
    def __init__(self):
        super().__init__(role="Principal Architect")

    def review_code(self, code: str) -> Dict[str, Any]:
        """Audits security and style parameters."""
        is_safe = "os.system" not in code and "eval" not in code
        has_docstring = '"""' in code or "'''" in code or "#" in code
        
        return {
            "approved": is_safe and has_docstring,
            "security_check": "passed" if is_safe else "failed",
            "style_score": 9.0 if has_docstring else 5.0
        }
