"""
sandbox.py
==========
Execution sandbox for executing code and running test cases inside 
isolated environments.
"""

import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple

class CodeExecutionSandbox:
    """Manages the creation, execution, and validation of code in a sandbox."""
    
    def __init__(self, timeout_seconds: float = 3.0):
        self.timeout = timeout_seconds

    def execute_script(self, code_content: str, filename: str = "temp_script.py") -> Tuple[bool, str]:
        """
        Executes a Python script in a temporary directory, capturing stdout and stderr.
        
        Args:
            code_content: Python code to execute.
            filename: Target file name inside the sandbox.
            
        Returns:
            A tuple containing:
                - success: True if the process exited with code 0, False otherwise.
                - logs: Combined stdout and stderr logs.
        """
        # Block malicious commands at boundary
        blocklist = ["import os; os.system", "subprocess.call", "shutil.rmtree", "eval("]
        if any(bad in code_content for bad in blocklist):
            return False, "Security Violation: Blocked malicious system operations."
            
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / filename
            
            # Write script
            try:
                file_path.write_text(code_content, encoding="utf-8")
            except Exception as e:
                return False, f"File IO error in sandbox initialization: {e}"
                
            # Execute subprocess
            try:
                result = subprocess.run(
                    [sys.executable, str(file_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=self.timeout,
                    text=True
                )
                
                success = (result.returncode == 0)
                logs = result.stdout + result.stderr
                return success, logs
                
            except subprocess.TimeoutExpired:
                return False, "Execution Error: Process timed out (exceeded limit)."
            except Exception as e:
                return False, f"Subprocess initialization error: {e}"
