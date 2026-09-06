# LIMITATIONS.md — Agent-IDE Sandbox
## Architecture Evolution & Boundary Analysis

This document details how the original limitations of `09_agent_ide_sandbox` were systematically addressed through the integration of the **Claude-Lightyear v10.0 Ultra / LOGOS** cognitive architecture, alongside remaining future work for production deployment.

---

## 1. Resolved Limitations via Claude-Lightyear v10.0 Ultra / LOGOS

| Original Limitation | Severity | Resolution via LOGOS Integration | Status |
|---|---|---|---|
| **Sequential Multi-Agent Topology** (rigid Coder→Tester→Reviewer waterfall) | High | **Layer 4 NAS Engine (`nas_topology.py`)**: Dynamically evaluates task complexity and synthesizes optimal cognitive topology (Linear, Tree-of-Thought, Dual-Framework, Recursive Refinement). | **RESOLVED** ✅ |
| **Lack of DAG Subtask Planning** (cannot break complex prompts into DAG) | High | **Level 0 Master Index Decomposer (`decomposition.py`)**: Recursive hierarchical subquestion taxonomy with dependency graph topological sorting. | **RESOLVED** ✅ |
| **Hash-Collision Trigram Embeddings** (lexical-only keyword matching in memory) | Medium | **Layer 3 Holographic Memory (`holographic_memory.py`)**: Boundary-to-Bulk complex phase interference vectors with Hermitian inner product associative recall. | **RESOLVED** ✅ |
| **Rolling Window Memory Forgetting** (old messages dropped after token budget) | High | **Holographic Compression & Coarse-Graining**: Compresses execution logs into compact boundary representations without losing invariant constraints. | **RESOLVED** ✅ |
| **No Real Model / LLM Support** (only mock rules were executed) | Critical | **Universal LLM Subsystem (`agent_core/llm/`)**: Native local Ollama GGUF runner (`http://localhost:11434`) + Cloud Frontier APIs (OpenAI, Claude, Grok, Gemini) with zero extra pip dependencies. | **RESOLVED** ✅ |
| **Absence of Mathematical Formalism** (ad-hoc heuristic code repairs) | Medium | **Layer 1 Axiom DB (`axiomatic_engine.py`)** & **Layer 6 Pondering Engine (`pondering_engine.py`)**: Formal logic consistency checks and strict $\ge 95\%$ confidence filtering. | **RESOLVED** ✅ |

---

## 2. Remaining Production Engineering Frontiers

While the cognitive and algorithmic architecture is now state-of-the-art, the following infrastructure frontiers remain for multi-tenant cloud deployments:

### 1. Operating System Sandboxing (MicroVMs)
- **Current implementation**: Process-level temporary isolation via Python `subprocess.run(timeout=3.0)` and temporary directory virtualization.
- **Production requirement**: Multi-tenant untrusted execution requires containerized isolation using Docker with gVisor (`runsc`) or lightweight microVMs (AWS Firecracker / Kata Containers) to prevent kernel privilege escalation or escape.

### 2. Live Web Search Rate Limits
- **Current implementation**: DuckDuckGo instant answer search via standard HTTP (`urllib.request`) with zero API keys required, backed by an offline CS knowledge corpus.
- **Production requirement**: Enterprise search backends (e.g. Brave Search API, Tavily, or Bing Web Search) with distributed rate-limiting and query caching for high-volume automated agents.

### 3. Distributed GPU Inference Coordination
- **Current implementation**: Point-to-point connection to local Ollama daemon (`localhost:11434`) or cloud API endpoints.
- **Production requirement**: Dynamic load-balancing across multi-node Ollama / vLLM clusters with automated model weight caching and KV-cache offloading.
