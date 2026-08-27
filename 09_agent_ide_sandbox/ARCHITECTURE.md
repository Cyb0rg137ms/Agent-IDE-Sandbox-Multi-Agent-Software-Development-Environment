# Agent IDE Sandbox — Architecture & Technical Reference

> **Full Project Name:** Agent IDE Sandbox — Multi-Agent Orchestrated Code Execution
> **Category:** Autonomous Agents / Developer Tooling / Sandboxed Computing
> **Language:** Python 3.9+, asyncio
> **Test Coverage:** 3/3 unit tests passing ✅

---

## 1. Architecture Overview

```
09_agent_ide_sandbox/
├── sandbox/
│   ├── executor.py     # Subprocess sandbox with resource limits
│   ├── agents.py       # Agent role definitions: planner, coder, reviewer
│   ├── orchestrator.py # Multi-agent OODA loop orchestrator
│   └── __init__.py
├── tests/
│   └── test_sandbox.py
├── demo_session.py     # Interactive CLI demonstration
└── README.md
```

### Component Interaction

```
┌────────────────────────────────────────────────────────────────┐
│                  AGENT IDE SANDBOX PIPELINE                   │
│                                                               │
│  User Task (natural language description)                     │
│          │                                                    │
│          ▼                                                    │
│  Orchestrator  ──  OODA Loop  ─────────────────────┐         │
│          │                                         │         │
│   ┌──────┴────────────────────────────┐            │         │
│   │            Agent Pool             │            │         │
│   │   ┌──────────┐  ┌────────┐  ┌──────────┐     │         │
│   │   │ Planner  │  │ Coder  │  │ Reviewer │     │         │
│   │   └──────────┘  └────────┘  └──────────┘     │         │
│   └───────────────────────────────────────────────┘         │
│                    │                                          │
│                    ▼                                          │
│           SandboxExecutor                                     │
│      ┌──────────────────────┐                                │
│      │  subprocess.run      │                                │
│      │  timeout = 30s       │                                │
│      │  capture stdout/err  │                                │
│      └──────────────────────┘                                │
│                    │                                          │
│                    └────────────────────────────────────────  │
│                    (result feeds back to Orchestrator)        │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematical Framework

### 2.1 OODA Loop Formalism

The orchestrator follows the military **Observe-Orient-Decide-Act** control cycle.
Each iteration of the loop maps to one round of agent execution:

| Phase | What happens |
|-------|-------------|
| **Observe** | Collect the output from the last agent (stdout, stderr, return code) |
| **Orient** | Compare output against the task's success criteria |
| **Decide** | Choose the next agent role to activate (Planner → Coder → Reviewer) |
| **Act** | Dispatch the chosen agent, execute its code in the sandbox |

The loop repeats until the Reviewer reports quality score Q >= Q_min, or the
maximum number of iterations is reached.

### 2.2 Task Decomposition Scoring

The Planner agent decomposes a task T into subtasks `{s_1, s_2, ..., s_k}`.
Each subtask gets a complexity estimate:

```
score(s_i)  =  w1 × lines_of_code(s_i)
             + w2 × dependency_count(s_i)
             + w3 × risk_score(s_i)

w1, w2, w3  = tunable weights (default: 0.4, 0.35, 0.25)
```

Subtasks are sorted topologically by dependency (subtasks that others depend on
go first) to determine the execution order.

### 2.3 Code Quality Signal from Reviewer

The Reviewer agent evaluates completed code and produces a quality score `Q`:

```
Q  =  (tests_passing / tests_total)  ×  (1 - complexity_penalty)

complexity_penalty  =  min( cyclomatic_complexity / 20,  0.5 )
                     = how convoluted the code logic is (capped at 50% penalty)

If Q < Q_min (default: 0.75):
    → Orchestrator re-activates the Coder for another refinement pass
If Q >= Q_min:
    → Orchestrator advances to the next subtask
```

### 2.4 Sandbox Resource Constraints

Each code execution is bounded to prevent runaway processes:

| Resource | Limit | Enforcement |
|----------|-------|-------------|
| Wall-clock time | 30 seconds | `subprocess.run(timeout=30)` |
| Standard output | 16 KB | `stdout=PIPE` + length check |
| Standard error | 8 KB | `stderr=PIPE` + length check |
| Child processes | 1 (no fork) | Single subprocess per call |

On timeout: raises `subprocess.TimeoutExpired` → executor marks step as failed.

---

## 3. Workflow

```
User describes task:  "write a function to sort a list of dicts by a key"
        │
        ▼
Orchestrator starts OODA cycle 1
        │
        ▼
Planner Agent:
  Decompose into subtasks:
    s_1: write sort_dicts(data, key) function
    s_2: write unit tests for sort_dicts
  Score each subtask, topological sort
        │
        ▼
Coder Agent (subtask s_1):
  Generate Python code for sort_dicts
        │
        ▼
SandboxExecutor:  run code with 30s timeout
  exit_code == 0?
    Yes → pass output to Reviewer
    No  → pass stderr back to Coder for fixing  (loop)
        │
        ▼
Reviewer Agent:
  Run tests, check code style
  Compute Q score
  Q >= 0.75?
    Yes → advance to s_2
    No  → re-activate Coder
        │
        ▼
All subtasks done?  → Return full session transcript
```

---

## 4. System Design

| Component | Module | Role |
|-----------|--------|------|
| **Executor** | `executor.py` | Subprocess isolation, timeout enforcement, output capture |
| **Agents** | `agents.py` | Role-based agent classes (Planner, Coder, Reviewer) |
| **Orchestrator** | `orchestrator.py` | OODA loop, agent dispatch, session state management |
| **Demo** | `demo_session.py` | CLI runner with real-time agent commentary |
| **Tests** | `test_sandbox.py` | Execution correctness, agent generation, loop completion |

---

## 5. Key Advantages

| Advantage | Description |
|-----------|-------------|
| **Safe code execution** | Hard timeout + subprocess isolation prevents runaway code |
| **Role separation** | Planner/Coder/Reviewer enables specialization without coupling |
| **Self-healing loop** | Reviewer feedback drives automatic code correction |
| **OODA formalism** | Military-grade control loop ensures convergence |
| **Session transcript** | Full audit trail of all agent decisions and code outputs |

---

## 6. Test Results

```
tests/test_sandbox.py::test_sandbox_execution  PASSED
tests/test_sandbox.py::test_agents_generation  PASSED
tests/test_sandbox.py::test_orchestrator_loop  PASSED
────────────────────────────────────────────────
3 passed in 0.06s
```

---

## 7. Quick Start

```bash
pip install -e .
pytest tests/
python demo_session.py
```

<div align="center">
  <a href="https://q.com"><img src="../../assets/https_q_com.png" width="80" /></a>
</div>
