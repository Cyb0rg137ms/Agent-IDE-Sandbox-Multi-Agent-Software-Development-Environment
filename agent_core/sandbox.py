"""
sandbox.py
==========
Execution sandbox for executing code and running test cases inside
isolated environments.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple

from agent_core.static_guard import scan

#: v1 substring blocklist, kept for backward compatibility (checked first).
LEGACY_BLOCKLIST = (
    "import os; os.system",
    "subprocess.call",
    "shutil.rmtree",
    "eval(",
)


class CodeExecutionSandbox:
    """Manages the creation, execution, and validation of code in a sandbox."""

    def __init__(self, timeout_seconds: float = 3.0, static_guard: bool = True):
        self.timeout = timeout_seconds
        #: AST guard (agent_core.static_guard). Disable only for trusted code.
        self.static_guard = static_guard

    def execute_script(
        self, code_content: str, filename: str = "temp_script.py"
    ) -> Tuple[bool, str]:
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
        # Block malicious commands at boundary (v1 substring list, then AST guard)
        if any(bad in code_content for bad in LEGACY_BLOCKLIST):
            return False, "Security Violation: Blocked malicious system operations."
        if self.static_guard:
            violations = scan(code_content)
            if violations:
                detail = "; ".join(str(v) for v in violations[:5])
                return False, f"Security Violation: Blocked by static guard ({detail})."

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
                    # -I: isolated mode (ignores PYTHON* env vars and user site-packages)
                    [sys.executable, "-I", str(file_path)],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=self.timeout,
                    text=True,
                )

                logs = result.stdout + result.stderr
                # Check for runtime errors, assertion failures, or unhandled exceptions
                has_error = (
                    result.returncode != 0
                    or "Traceback (most recent call last):" in logs
                    or "AssertionError" in logs
                    or "FAILED (" in logs
                    or "ERROR: " in logs
                    or "SyntaxError:" in logs
                    or "NameError:" in logs
                    or "TypeError:" in logs
                    or "ZeroDivisionError:" in logs
                )
                success = (result.returncode == 0) and not has_error
                return success, logs

            except subprocess.TimeoutExpired:
                return False, "Execution Error: Process timed out (exceeded limit)."
            except Exception as e:
                return False, f"Subprocess initialization error: {e}"
