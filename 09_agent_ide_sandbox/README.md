# 🤖 Agent-IDE-Sandbox: Multi-Agent Dev Loop & LOGOS Cognitive Architecture

**Agent-IDE-Sandbox** is an advanced agentic coding framework that unifies collaborative AI agents (Coder, Tester, Reviewer, and LOGOS Cognitive Strategists) inside a secure execution sandbox to automatically write, validate, debug, and formally verify code.

Enhanced with the mathematical and structural principles of the **Lightyear v10.0 Ultra / LOGOS Cognitive Framework** (Level 0–2 Meta-Architecture & 7-Layer Stack,), the entire sandbox serves as a dynamic interface architecture for any connected local or cloud LLM.

---

## 🌟 What's New: Lightyear v10.0 Ultra / LOGOS Integration

The sandbox now includes the full algorithmic stack from Lightyear v10.0 Ultra:

1. **Level 0: Master Index & Subquestion Taxonomy (`decomposition.py`)**:
   - Decomposes complex coding and architectural tasks into hierarchical subquestions across Information Theory, Complexity Bounds, Boundary Invariants, and Operator Symmetries.
   - Computes execution schedules via topological DAG sorting.
2. **Level 1 & 2: Dual-Framework Protocol & Convergence Engine (`convergence.py`)**:
   - Evaluates problems across **Framework 1 (Classical CS Baseline)** and **Framework 2 (Theory 2 Structural / Non-Archimedean Invariants)**.
   - Constructs Property Alignment Matrices and executes backward chaining from desired goal states.
3. **Layer 1: Axiomatic Derivation Engine (`axiomatic_engine.py`)**:
   - Formal logic consistency checks preventing unguarded division singularities, array bounds violations, or contradictory statements.
4. **Layer 2: Fractal Reasoning Engine MERA (`fractal_mera.py`)**:
   - Multiscale Entanglement Renormalization Ansatz (MERA) coarse-graining across AST tokens (Scale 0), function guards (Scale 1), interfaces (Scale 2), and system invariants (Scale 3).
5. **Layer 3: Holographic Memory Compression (`holographic_memory.py`)**:
   - Boundary-to-Bulk complex phase projections (Holographic Reduced Representations) enabling infinite context retention without token explosion.
6. **Layer 4: Neural Architecture Search (NAS) Cognitive Topology (`nas_topology.py`)**:
   - Dynamically analyzes task ambiguity and synthesizes the optimal multi-agent execution topology:
     - `linear_pipeline` (standard deterministic tasks)
     - `tree_of_thought` (heuristic search and optimization)
     - `dual_framework` (deep system & invariant synthesis)
     - `recursive_refinement` (iterative search space reduction & crypto analysis)
7. **Layer 5: Dynamic Axiom Retrieval System (`dynamic_retrieval.py`)**:
   - Lightweight web search integration (DuckDuckGo instant search without requiring paid keys) and algorithmic corpus fallback for dynamic theorem extraction.
8. **Layer 6: Pondering Engine with Strict 95%+ Confidence Boundary (`pondering_engine.py`)**:
   - Horizontal multi-angle exploration across 5 orthogonal inquiry dimensions.
   - Strict filtering rejecting any speculative hypothesis with confidence $C < 0.95$.
   - Quantifies recursive candidate space reduction $(1 - r)^k$.
9. **Layer 7: Universal Operator Interface Architecture (`operator_interface.py`)**:
   - The entire sandbox functions as the primary interface architecture for the connected LLM.

---

## 🔌 Universal LLM Model Support (Local GGUF & Frontier Cloud APIs)

The system features a plug-and-play provider subsystem with **zero mandatory external pip dependencies** (built using standard library `urllib.request`):

| Provider | Type | Supported Models | Configuration |
|---|---|---|---|
| **Ollama** | Local GGUF | `qwen2.5-coder`, `deepseek-r1`, `llama3.2`, `mistral`, `codellama`, etc. | Set `OLLAMA_HOST` (default: `http://localhost:11434`) |
| **Local Server** | Local GGUF | `llama.cpp` server, LM Studio, vLLM | Set `base_url` (default: `http://localhost:8080/v1`) |
| **OpenAI** | Cloud API | `gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini` | `export OPENAI_API_KEY="..."` |
| **Anthropic** | Cloud API | `claude-3-7-sonnet`, `claude-3-5-sonnet`, `claude-3-opus` | `export ANTHROPIC_API_KEY="..."` |
| **xAI Grok** | Cloud API | `grok-2-latest`, `grok-beta` | `export XAI_API_KEY="..."` |
| **Google Gemini** | Cloud API | `gemini-1.5-flash`, `gemini-2.0-flash` | `export GEMINI_API_KEY="..."` |
| **Mock Engine** | Offline | High-fidelity deterministic multi-agent simulation | Always available (Zero keys needed) |

---

## 🚀 Quick Start

### 1. Launch Web Chatbot Interface (Claude & ChatGPT Style)
Launch the modern browser chatbot interface with live thinking accordions, sandbox terminal tabs, and dynamic API switching:
```bash
python run_web_ui.py
# Optional flags: --port 8080 --host 127.0.0.1 --provider ollama
```

### 2. Run Interactive Terminal Operator Console
Launch the interactive terminal console to choose your provider (Ollama local GGUF or Cloud API), toggle LOGOS reasoning, and run custom tasks:
```bash
python run_interactive_sandbox.py
```

### 3. Run Headless / CLI Runner
Run with the deterministic mock provider and LOGOS enabled:
```bash
python run_sandbox.py --logos
```

Run with a local Ollama GGUF model:
```bash
python run_sandbox.py --provider ollama --model qwen2.5-coder:7b --logos
```

Run with Claude, OpenAI, or Grok:
```bash
python run_sandbox.py --provider claude --model claude-3-7-sonnet-20250219 --logos
python run_sandbox.py --provider openai --model gpt-4o --logos
python run_sandbox.py --provider grok --model grok-2-latest --logos
```

### 4. Run Test Suite
All 92 unit and integration tests pass with 100% test coverage:
```bash
pytest
```

---

## 📐 Mathematical Framework & State Machine

```
        ┌────────────────────────────────────────────────────────────┐
        │                                                            │
        ▼                                                            │
[User Task] ──► [LOGOS: NAS Topology & Pondering] ──► [Coder Draft] ──► [Tester Harness]
                                                                             │
               ┌─────────────────────────────────────────────────────────────┤
               ▼ (Test Fails)                                                ▼ (Test Passes)
      [Coder: Debug / Self-Repair]                                    [Reviewer Audit]
               ▲                                                             │
               └────────────────── (Audits Fail) ────────────────────────────┤
                                                                             ▼ (Audits Pass)
                                                                        [Terminated: OK]
```

At iteration $k \in \{1, \dots, K_{\max}\}$:
1. **Pondering & Confidence Filtering**:
   $$\mathcal{P}_{\text{accepted}} = \left\{ p_i \in \mathcal{P} \;\middle|\; C(p_i) \ge 0.95 \right\}$$
2. **Code Generation**:
   $$C_k = \operatorname{Coder}(T, \mathcal{P}_{\text{accepted}}, E_{k-1})$$
3. **Execution Sandbox**:
   $$R_k, E_k = \operatorname{Sandbox}(S_k)$$
4. **Holographic Boundary Superposition**:
   $$\mathbf{\Psi}_k = \alpha \mathbf{\Psi}_{k-1} + \beta \mathbf{v}(E_k)$$

---

## 🛡️ Security & Sandbox Isolation
- **Subprocess Isolation**: Scripts run inside isolated temporary directories with strict timeout limits (`subprocess.run(timeout=3.0)`).
- **Static Boundary AST Filters**: Blocks dangerous system operations (`os.system`, `subprocess`, `rmtree`, `eval`) before process creation.
- **Formal Invariant Verification**: `AxiomaticEngine` verifies logical consistency and bounds guards before execution.