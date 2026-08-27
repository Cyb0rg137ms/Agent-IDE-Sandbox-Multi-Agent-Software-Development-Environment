# 🤖 Agent-IDE-Sandbox: Multi-Agent Dev Loop Orchestrator

Agent-IDE-Sandbox is an agentic coding framework that orchestrates collaborative AI agents (Coder, Tester, and Reviewer) inside a secure execution sandbox to automatically write, validate, and debug Python code. By capturing runtime errors and stdout from isolated subprocesses, the orchestrator feeds tracebacks back to the Coder agent to perform automated error recovery.

---

## 📐 Mathematical Framework & State Machine

The orchestrator operates as a Finite State Machine (FSM) executing a task $T$:

```
        ┌────────────────────────────────────┐
        │                                    │
        ▼                                    │
[Start State] ──► [Coder: Gen Code] ──► [Tester: Gen Tests] ──► [Sandbox Run]
                                                                     │
               ┌─────────────────────────────────────────────────────┤
               ▼ (Test Fails)                                        ▼ (Test Passes)
      [Coder: Debug / Fix]                                    [Reviewer Audit]
               ▲                                                     │
               └───────── (Audits Fail) ─────────────────────────────┤
                                                                     ▼ (Audits Pass)
                                                                [Terminated: OK]
```

At iteration $k \in \{1, \dots, K_{\max}\}$:
1. **Code Generation**:
   $$C_k = \operatorname{Coder}(T, E_{k-1})$$
   where $E_{k-1}$ represents the traceback log from the previous iteration ($E_0 = \emptyset$).
2. **Test Generation**:
   $$S_k = \operatorname{Tester}(C_k, T)$$
3. **Execution Sandbox**:
   $$R_k, E_k = \operatorname{Sandbox}(S_k)$$
   where $R_k \in \{0, 1\}$ represents the execution success status. If $R_k = 1$, the loop terminates successfully, sending $C_k$ to the Reviewer.

---

## 🛠️ Workings & Pipeline

1. **Subprocess Isolation**: Scripts are run in separate processes using temporary workspace directories and custom file names, preventing global namespace contamination.
2. **Security Filtering**: Before spawning shell processes, the sandbox parses code files to block dangerous instructions (e.g. `os.system`, `subprocess`, `rmtree`, or `eval`), protecting host filesystems.
3. **Iterative Repair**: Uses standard syntax tracebacks (like `ZeroDivisionError` or `IndexError`) to provide contextual feedback to the Coder agent, enabling self-correction.

---

## 💎 Key Advantages

- **Secure Execution**: Guards execution using active token blockers and process limits to prevent host system damage.
- **Self-Healing Code**: Solves bugs autonomously by feeding raw exception text back to prompt completions.
- **Zero API Key Requirement**: Features deterministic mockup configurations to enable complete integration testing without active LLM subscriptions.

---

## 📦 How to Install and Run

### Prerequisites
- Python 3.9 or higher

### Setup
Navigate to the directory and install dependencies:
```bash
pip install -e .
```

### Running Tests
Run the test suite using `pytest`:
```bash
pytest tests/
```

### Running the Orchestration Demo
To execute the interactive self-healing agent loop:
```bash
python run_sandbox.py
```

---

<div align="center">
  <a href="https://q.com">
    <img src="../../assets/https_q_com.png" alt="Q Logo" width="100" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
  </a>
  <br/>
  <small>Ecosystem mapping and validation protocols courtesy of <a href="https://q.com">q.com</a></small>
</div>
