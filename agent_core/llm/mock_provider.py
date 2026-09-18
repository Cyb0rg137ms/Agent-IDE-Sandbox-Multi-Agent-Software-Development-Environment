"""
mock_provider.py
================
Deterministic mock LLM provider for zero-cost testing, CI/CD, and offline verification.
Simulates multi-agent code generation, testing, reviews, and LOGOS pondering.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from agent_core.llm.base import BaseLLMProvider, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider generating deterministic code and reasoning."""

    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        content = self._synthesize_response(prompt, system_prompt or "")
        return LLMResponse(
            content=content,
            model=self.model_name or "mock-engine-v1",
            provider=self.provider_name,
            prompt_tokens=max(1, len(prompt) // 4),
            completion_tokens=max(1, len(content) // 4),
            total_tokens=max(2, (len(prompt) + len(content)) // 4),
            finish_reason="stop",
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        full_prompt = "\n".join(m.get("content", "") for m in messages)
        system = next((m.get("content", "") for m in messages if m.get("role") == "system"), "")
        return self.generate(full_prompt, system_prompt=system, temperature=temperature, max_tokens=max_tokens)

    def _synthesize_response(self, prompt: str, system: str) -> str:
        p_lower = prompt.lower()
        s_lower = system.lower()

        # Extract target task if present
        target_task = p_lower
        if "target task:" in p_lower:
            try:
                target_task = p_lower.split("target task:")[1].split("\n")[0].strip()
            except Exception:
                target_task = p_lower

        # Check if error logs or defect refinement are provided for self-healing
        if "error" in p_lower or "traceback" in p_lower or "zerodivisionerror" in p_lower or "indexerror" in p_lower or "defects" in p_lower or "repair" in s_lower:
            match_fn = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', prompt)
            curr_fn = match_fn.group(1).lower() if match_fn else ""
            if "zerodivision" in p_lower or "zero-division" in p_lower or curr_fn == "divide" or ("divide" in target_task and "fibonacci" not in target_task and "search" not in target_task):
                return (
                    "```python\n"
                    "def divide(a, b):\n"
                    "    \"\"\"Divide a by b safely handling zero divisor.\"\"\"\n"
                    "    if b == 0:\n"
                    "        return 0\n"
                    "    return a / b\n"
                    "```"
                )
            if "indexerror" in p_lower or curr_fn == "get_element" or ("element" in target_task and "fibonacci" not in target_task and "search" not in target_task):
                return (
                    "```python\n"
                    "def get_element(arr, idx):\n"
                    "    \"\"\"Get element at index with safe bounds checking.\"\"\"\n"
                    "    if idx < 0 or idx >= len(arr):\n"
                    "        return None\n"
                    "    return arr[idx]\n"
                    "```"
                )
            app_code = self._synthesize_interactive_application(target_task)
            if app_code:
                return f"```html\n{app_code}\n```"
            return self._synthesize_python_code(target_task)

        # Tester role
        if "qa" in s_lower or "test" in s_lower or "generate test" in p_lower:
            match_fn = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)', prompt)
            if match_fn:
                fn = match_fn.group(1)
                args = [a.strip() for a in match_fn.group(2).split(",") if a.strip()]
                if fn == "divide":
                    return (
                        "```python\n"
                        "assert divide(6, 2) == 3\n"
                        "assert divide(5, 0) == 0\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "get_element":
                    return (
                        "```python\n"
                        "assert get_element([1, 2], 1) == 2\n"
                        "assert get_element([1, 2], 5) is None\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "fibonacci":
                    return (
                        "```python\n"
                        "assert fibonacci(1) == 1\n"
                        "assert fibonacci(5) == 5\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "quicksort" or fn == "sort":
                    return (
                        "```python\n"
                        "assert quicksort([3, 1, 2]) == [1, 2, 3]\n"
                        "assert quicksort([]) == []\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "binary_search":
                    return (
                        "```python\n"
                        "assert binary_search([1, 2, 3, 4], 3) == 2\n"
                        "assert binary_search([1, 2, 3, 4], 9) == -1\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "reverse_string":
                    return (
                        "```python\n"
                        "assert reverse_string('abc') == 'cba'\n"
                        "assert reverse_string('') == ''\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "is_palindrome":
                    return (
                        "```python\n"
                        "assert is_palindrome('radar') is True\n"
                        "assert is_palindrome('hello') is False\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "is_prime":
                    return (
                        "```python\n"
                        "assert is_prime(7) is True\n"
                        "assert is_prime(4) is False\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                if fn == "factorial":
                    return (
                        "```python\n"
                        "assert factorial(4) == 24\n"
                        "assert factorial(0) == 1\n"
                        "print('All tests passed')\n"
                        "```"
                    )
                call_args = []
                for a in args:
                    a_name = a.split(":")[0].strip().lower()
                    if any(k in a_name for k in ["arr", "list", "items", "nums"]):
                        call_args.append("[1, 2]")
                    elif any(k in a_name for k in ["s", "str", "text", "word"]):
                        call_args.append("'test'")
                    else:
                        call_args.append("1")
                call_str = ", ".join(call_args)
                return (
                    "```python\n"
                    f"res = {fn}({call_str})\n"
                    "assert res is not None\n"
                    "print('All tests passed')\n"
                    "```"
                )
            if "divide" in p_lower:
                return (
                    "```python\n"
                    "assert divide(6, 2) == 3\n"
                    "assert divide(5, 0) == 0\n"
                    "print('All tests passed')\n"
                    "```"
                )
            if "element" in p_lower:
                return (
                    "```python\n"
                    "assert get_element([1, 2], 1) == 2\n"
                    "assert get_element([1, 2], 5) is None\n"
                    "print('All tests passed')\n"
                    "```"
                )
            return (
                "```python\n"
                "print('All tests passed')\n"
                "```"
            )

        # Reviewer role
        if "reviewer" in s_lower or "architect" in s_lower or "audit" in p_lower:
            return (
                '{\n'
                '  "approved": true,\n'
                '  "security_check": "passed",\n'
                '  "style_score": 9.5,\n'
                '  "analysis": "Code adheres to security constraints, includes complete docstrings and boundary guards."\n'
                '}'
            )

        # Extract the specific target task if structured prompt is used
        target_task = p_lower
        if "target task:" in p_lower:
            try:
                target_task = p_lower.split("target task:")[1].split("\n")[0].strip()
            except Exception:
                target_task = p_lower

        # Code generation for interactive games and applications
        app_code = self._synthesize_interactive_application(target_task)
        if app_code:
            return f"```html\n{app_code}\n```"

        # Code generation for coding tasks (initial draft - deliberately simple/buggy to demonstrate self-healing)
        if "divide" in target_task:
            return (
                "```python\n"
                "def divide(a, b):\n"
                "    \"\"\"Divide two numbers.\"\"\"\n"
                "    return a / b\n"
                "```"
            )
        elif "element" in target_task:
            return (
                "```python\n"
                "def get_element(arr, idx):\n"
                "    \"\"\"Get element at index.\"\"\"\n"
                "    return arr[idx]\n"
                "```"
            )

        # Conversational, Conceptual, or Scientific / Mathematical Explanations
        conv_resp = self._synthesize_conversational_response(prompt)
        if conv_resp is not None:
            return conv_resp

        return self._synthesize_python_code(prompt)

    def _synthesize_conversational_response(self, prompt: str) -> Optional[str]:
        """Synthesizes rich markdown conversational explanations for non-code prompts."""
        p_lower = prompt.lower().strip()

        # Greetings & identity
        if any(p_lower.startswith(g) for g in ["hi", "hello", "hey", "greetings", "good morning", "good evening"]):
            return (
                "Hello! I am your **Agent-IDE Sandbox Assistant**, accelerated by the **LOGOS Ultra** "
                "cognitive architecture and the **TypeSafe AI Jev** fast-decision pipeline.\n\n"
                "Here is how I can assist you:\n"
                "- **Autonomous Code Sandbox**: Execute, unit-test, and self-heal code in isolated subprocesses.\n"
                "- **MCP Server Studio**: Design, test via JSON-RPC, and scaffold custom Model Context Protocol servers.\n"
                "- **Interactive Visual Artifacts**: Generate self-contained HTML5/WebGL simulations and games.\n"
                "- **TypeSafe Decision Pipeline**: Fast-path sub-15ms categorical routing and formal invariant enforcement.\n\n"
                "What project or problem would you like to explore today?"
            )

        if "who are you" in p_lower or "what are you" in p_lower:
            return (
                "I am the **Agent-IDE Sandbox AI**, an agentic software development environment. "
                "I combine frontier LLMs (Ollama local GGUF, Claude 3.7 Sonnet, OpenAI o1/gpt-4o, xAI Grok) "
                "with an isolated Python sandbox, formal MERA coarse-graining, holographic episodic memory, "
                "and native Model Context Protocol (MCP) server development tools."
            )

        if "zeta" in p_lower or "riemann" in p_lower or "spectral" in p_lower:
            return (
                "### Zeta Function & Spectral Physics Formulation\n\n"
                "The connection between the nontrivial zeros of the Riemann zeta function $\\zeta(s) = \\sum_{n=1}^\\infty n^{-s}$ "
                "and spectral operator theory arises via the **Hilbert-Pólya conjecture**:\n\n"
                "1. **Spectral Operator Conjecture**: There exists a self-adjoint Hamiltonian operator $\\hat{H} = -\\frac{\\hbar^2}{2m}\\nabla^2 + V(x)$ "
                "whose discrete eigenvalues correspond to the imaginary parts $E_n = \\gamma_n$ of the nontrivial zeros $s_n = \\frac{1}{2} + i\\gamma_n$.\n"
                "2. **Montgomery's Pair Correlation**: The two-point correlation function of high zeros converges to the **Gaussian Unitary Ensemble (GUE)** "
                "random matrix eigenvalue statistics: $1 - \\left(\\frac{\\sin(\\pi r)}{\\pi r}\\right)^2$.\n"
                "3. **Berry-Keating Semiclassical Limit**: For classical phase-space orbits, the chaotic dilation Hamiltonian $H = xp$ "
                "yields the smooth average counting function $\\langle N(E) \\rangle = \\frac{E}{2\\pi} \\ln\\left(\\frac{E}{2\\pi e}\\right) + \\frac{7}{8}$."
            )

        if "higgs" in p_lower or "guac" in p_lower or "boson mass" in p_lower:
            return (
                "### Higgs Boson Mass & Geometric Gauge Coupling ($\\Phi$-GUAC)\n\n"
                "In topological gauge unification and dimensional reduction manifolds:\n\n"
                "- **Vacuum Expectation Value ($v$)**: $v \\approx 246.22\\text{ GeV}$, governed by the minimum of the scalar potential $V(\\Phi) = -\\mu^2\\Phi^\\dagger\\Phi + \\lambda(\\Phi^\\dagger\\Phi)^2$.\n"
                "- **Physical Mass**: $m_H = \\sqrt{2\\lambda} v \\approx 125.1\\text{ GeV}$, requiring the quartic self-coupling constant $\\lambda \\approx 0.129$.\n"
                "- **Radiative Stability**: Top quark Yukawa radiative corrections $\\delta m_H^2 = -\\frac{3 y_t^2}{8\\pi^2} \\Lambda^2$ are geometrically damped "
                "across the dual topological manifold, stabilizing electroweak symmetry breaking without fine-tuning."
            )

        if "fractal" in p_lower or "measure theory" in p_lower or "hausdorff" in p_lower:
            return (
                "### Fractal Geometry & Measure-Theoretic Dimensions\n\n"
                "In geometric measure theory, metric spaces $(\\mathcal{X}, d)$ exhibit non-integer scaling dimensions:\n\n"
                "1. **Hausdorff Measure**: $\\mathcal{H}^d(S) = \\lim_{\\delta \\to 0} \\inf \\left\\{ \\sum_i (\\text{diam}(U_i))^d : S \\subseteq \\bigcup U_i, \\text{diam}(U_i) < \\delta \\right\\}$.\n"
                "2. **Hausdorff Dimension**: $d_H(S) = \\inf \\{d \\ge 0 : \\mathcal{H}^d(S) = 0\\} = \\sup \\{d \\ge 0 : \\mathcal{H}^d(S) = \\infty\\}$.\n"
                "3. **MERA Multiscale Renormalization**: Discrete code and token spaces exhibit self-similar topological entanglement entropy "
                "$S(L) \\sim c \\ln(L)$, mirroring conformal field theories in low dimensions."
            )

        if "knot" in p_lower or "topology" in p_lower:
            return (
                "### 3D Knot Theory & Topological Invariants\n\n"
                "Topological classification of 1-manifolds embedded in $\\mathbb{R}^3$ (or $S^3$):\n\n"
                "- **Reidemeister Moves**: Any two equivalent knot projections differ by a finite sequence of Type I (twist), Type II (poke), and Type III (slide) transformations.\n"
                "- **Jones Polynomial $V(t)$**: An oriented knot invariant derived from the braid group and Temperley-Lieb algebra, satisfying the skein relation: "
                "$t^{-1} V(L_+) - t V(L_-) = (t^{1/2} - t^{-1/2}) V(L_0)$.\n"
                "- **Alexander-Conway Polynomial**: Detects knot genus and homological fiberedness."
            )

        if "caching" in p_lower or "cache pattern" in p_lower:
            return (
                "### Modern Caching Patterns in Distributed Systems\n\n"
                "Key patterns for low-latency state caching:\n\n"
                "1. **Cache-Aside (Lazy Loading)**: Application inspects cache first; on miss, fetches from primary DB and warms cache.\n"
                "2. **Write-Through**: Application writes data to cache, and cache synchronously persists to storage, ensuring strict consistency.\n"
                "3. **Write-Behind (Write-Back)**: Writes enter cache immediately; an asynchronous background worker flushes batches to persistent storage.\n"
                "4. **Probabilistic Early Expiration (XFetch)**: Computes dynamic refresh probability $P = -\\beta \\cdot \\delta \\cdot \\ln(\\text{rand()}) > \\text{TTL}$ "
                "to prevent thundering herd stampedes on hot cache keys."
            )

        if "llm training" in p_lower or "optimizing" in p_lower and "training" in p_lower:
            return (
                "### Optimizing LLM Training Pipelines\n\n"
                "State-of-the-art techniques for accelerating large model training and fine-tuning:\n\n"
                "- **ZeRO-3 & FSDP**: Fully Sharded Data Parallelism shards optimizer states, gradients, and model parameters across GPUs.\n"
                "- **FlashAttention-3**: FP8 tiled matrix multiplication overlapping GEMM and softmax with hardware asynchronous copy.\n"
                "- **Activation Checkpointing**: Recomputes forward activations during backward pass to reduce peak VRAM by up to 70%.\n"
                "- **Pipeline Parallelism (1F1B)**: One-Forward-One-Backward schedule minimizes pipeline bubbles across device ranks."
            )

        if "mcp" in p_lower:
            return (
                "### Model Context Protocol (MCP) Architecture\n\n"
                "The **Model Context Protocol (MCP)** is an open standard designed by Anthropic enabling AI models to securely interact with local and remote resources.\n\n"
                "- **Transport**: Stdio (standard input/output for local processes) or SSE (Server-Sent Events for HTTP).\n"
                "- **Capabilities**:\n"
                "  - **Tools**: Executable functions callable by the model (`tools/list`, `tools/call`).\n"
                "  - **Resources**: Read-only contexts like database schemas or files (`resources/list`, `resources/read`).\n"
                "  - **Prompts**: Parameterized workflow templates (`prompts/list`, `prompts/get`).\n\n"
                "Use the **MCP Server Studio** in this app to create, test, and export your own custom servers!"
            )

        # General inquiry fallback: return clear, structured guidance
        coding_signals = ["write", "code", "function", "implement", "def ", "class ", "fix", "solve", "script", "program"]
        if not any(k in p_lower for k in coding_signals):
            return (
                f"### Analysis & Response\n\n"
                f"Regarding your query: *\"{prompt.strip()}\"*\n\n"
                "In system architecture and engineering, addressing this involves decomposing the problem into "
                "modular constraints, establishing clear boundary invariants, and validating execution pathways.\n\n"
                "- **Invariants**: Ensure complete input sanitization, deterministic state transitions, and bounded memory overhead.\n"
                "- **Execution**: Dispatched through the **TypeSafe AI Jev** fast-path decision engine.\n"
                "- **Actionable Next Steps**: You can instruct me to write a full Python implementation, scaffold an MCP server, "
                "or compile a self-contained interactive web preview."
            )

        return None

    def _synthesize_interactive_application(self, target_task: str) -> Optional[str]:
        """Dispatches to the exact game, canvas app, or interactive web application requested."""
        t = target_task.lower()
        if "snake" in t:
            return self._get_snake_game_html()
        if "pong" in t:
            return self._get_pong_game_html()
        if "tetris" in t:
            return self._get_tetris_game_html()
        if "tic tac toe" in t or "tictactoe" in t or "tic-tac-toe" in t:
            return self._get_tictactoe_game_html()
        if "flappy" in t:
            return self._get_flappy_bird_html()
        if "space invader" in t or "invaders" in t or "alien" in t or "shooter" in t:
            return self._get_space_invaders_html()
        if "breakout" in t or "brick" in t:
            return self._get_breakout_html()
        if "calculator" in t:
            return self._get_calculator_html()
        if "todo" in t or "to-do" in t or "task list" in t:
            return self._get_todo_app_html()
        if "minesweeper" in t or "mine" in t:
            return self._get_minesweeper_html()
        if "maze" in t:
            return self._get_maze_game_html()
        if "memory" in t or "card match" in t:
            return self._get_memory_game_html()
        if "temple" in t or ("runner" in t and "3d" in t):
            return self._get_temple_run_html()
        if any(k in t for k in ["game", "canvas", "arcade", "play", "html5", "interactive", "simulator", "app"]):
            return self._get_generic_canvas_game_html(target_task)
        return None

    def _get_snake_game_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Snake Arcade</title>
<style>
  body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  #hud { display: flex; gap: 20px; font-size: 18px; margin-bottom: 12px; font-weight: bold; }
  canvas { background: #020617; border: 2px solid #38bdf8; border-radius: 8px; box-shadow: 0 0 20px rgba(56,189,248,0.2); }
  .ctrl { margin-top: 10px; font-size: 13px; color: #94a3b8; }
</style>
</head>
<body>
  <div id="hud"><span>Score: <span id="score">0</span></span><span>Best: <span id="best">0</span></span></div>
  <canvas id="c" width="400" height="400"></canvas>
  <div class="ctrl">Use Arrow Keys or WASD to control snake • Space to Restart</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d'), grid = 20, count = 20;
  let snake = [{x: 10, y: 10}], dx = 1, dy = 0, food = {x: 15, y: 15}, score = 0, best = 0, over = false;
  function reset() { snake = [{x: 10, y: 10}]; dx = 1; dy = 0; score = 0; over = false; spawnFood(); }
  function spawnFood() { food = {x: Math.floor(Math.random()*count), y: Math.floor(Math.random()*count)}; }
  document.addEventListener('keydown', e => {
    if ((e.key === 'ArrowUp' || e.key === 'w') && dy === 0) { dx = 0; dy = -1; }
    if ((e.key === 'ArrowDown' || e.key === 's') && dy === 0) { dx = 0; dy = 1; }
    if ((e.key === 'ArrowLeft' || e.key === 'a') && dx === 0) { dx = -1; dy = 0; }
    if ((e.key === 'ArrowRight' || e.key === 'd') && dx === 0) { dx = 1; dy = 0; }
    if (e.key === ' ' && over) reset();
  });
  function loop() {
    setTimeout(loop, 90);
    if (over) return;
    let head = {x: snake[0].x + dx, y: snake[0].y + dy};
    if (head.x < 0 || head.x >= count || head.y < 0 || head.y >= count || snake.some(s => s.x === head.x && s.y === head.y)) {
      over = true;
      ctx.fillStyle = 'rgba(0,0,0,0.7)'; ctx.fillRect(0,0,c.width,c.height);
      ctx.fillStyle = '#ef4444'; ctx.font = '24px sans-serif'; ctx.textAlign = 'center';
      ctx.fillText('Game Over! Press Space', c.width/2, c.height/2);
      return;
    }
    snake.unshift(head);
    if (head.x === food.x && head.y === food.y) {
      score += 10; if (score > best) best = score;
      document.getElementById('score').textContent = score;
      document.getElementById('best').textContent = best;
      spawnFood();
    } else { snake.pop(); }
    ctx.fillStyle = '#020617'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = '#ef4444'; ctx.fillRect(food.x*grid+2, food.y*grid+2, grid-4, grid-4);
    snake.forEach((s, i) => {
      ctx.fillStyle = i === 0 ? '#38bdf8' : '#0ea5e9';
      ctx.fillRect(s.x*grid+1, s.y*grid+1, grid-2, grid-2);
    });
  }
  reset(); loop();
</script>
</body>
</html>'''

    def _get_pong_game_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Retro Pong</title>
<style>
  body { background: #0a0a0f; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  canvas { background: #000; border: 2px solid #6366f1; border-radius: 8px; }
  #score { font-size: 28px; font-weight: bold; margin-bottom: 10px; font-family: monospace; }
</style>
</head>
<body>
  <div id="score">Player: <span id="p">0</span> | AI: <span id="ai">0</span></div>
  <canvas id="c" width="600" height="400"></canvas>
  <div style="margin-top: 10px; font-size: 13px; color: #818cf8;">Move mouse vertically or use Up/Down keys</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  let py = 160, aiY = 160, bx = 300, by = 200, bdx = 4, bdy = 4, pScore = 0, aiScore = 0;
  c.addEventListener('mousemove', e => { const r = c.getBoundingClientRect(); py = e.clientY - r.top - 40; });
  function loop() {
    bx += bdx; by += bdy;
    if (by <= 5 || by >= 395) bdy = -bdy;
    aiY += (by - (aiY + 40)) * 0.08;
    if (bx <= 25 && by >= py && by <= py + 80) { bdx = Math.abs(bdx) + 0.2; }
    if (bx >= 575 && by >= aiY && by <= aiY + 80) { bdx = -Math.abs(bdx) - 0.2; }
    if (bx < 0) { aiScore++; document.getElementById('ai').textContent = aiScore; resetBall(); }
    if (bx > 600) { pScore++; document.getElementById('p').textContent = pScore; resetBall(); }
    ctx.fillStyle = '#000'; ctx.fillRect(0,0,600,400);
    ctx.strokeStyle = 'rgba(255,255,255,0.2)'; ctx.setLineDash([5, 5]);
    ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 400); ctx.stroke();
    ctx.fillStyle = '#38bdf8'; ctx.fillRect(10, py, 12, 80);
    ctx.fillStyle = '#f43f5e'; ctx.fillRect(578, aiY, 12, 80);
    ctx.fillStyle = '#facc15'; ctx.beginPath(); ctx.arc(bx, by, 7, 0, Math.PI*2); ctx.fill();
    requestAnimationFrame(loop);
  }
  function resetBall() { bx = 300; by = 200; bdx = -bdx; bdy = 3; }
  loop();
</script>
</body>
</html>'''

    def _get_tetris_game_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>HTML5 Tetris</title>
<style>
  body { background: #111827; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  canvas { background: #030712; border: 2px solid #a855f7; border-radius: 8px; }
  .stats { font-size: 20px; font-weight: bold; margin-bottom: 12px; }
</style>
</head>
<body>
  <div class="stats">Score: <span id="score">0</span></div>
  <canvas id="c" width="240" height="400"></canvas>
  <div style="margin-top: 10px; font-size: 12px; color: #9ca3af;">Left/Right: Move • Up: Rotate • Down: Drop</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  const cols = 10, rows = 20, block = 24, board = Array.from({length: rows}, () => Array(cols).fill(0));
  const shapes = [[[1,1,1,1]], [[1,1],[1,1]], [[0,1,0],[1,1,1]], [[1,0,0],[1,1,1]], [[0,0,1],[1,1,1]], [[1,1,0],[0,1,1]], [[0,1,1],[1,1,0]]];
  const colors = ['#06b6d4','#eab308','#a855f7','#3b82f6','#f97316','#22c55e','#ef4444'];
  let piece = newPiece(), px = 3, py = 0, score = 0, dropCounter = 0;
  function newPiece() { const idx = Math.floor(Math.random()*shapes.length); return {shape: shapes[idx], color: colors[idx]}; }
  function collide(x, y, s) {
    for (let r=0; r<s.length; r++) for (let c=0; c<s[r].length; c++) {
      if (s[r][c] && (board[y+r] && board[y+r][x+c]) !== 0) return true;
    }
    return false;
  }
  function merge() {
    piece.shape.forEach((r, y) => r.forEach((val, x) => { if (val) board[py+y][px+x] = piece.color; }));
    let lines = 0;
    for (let y = rows-1; y >= 0; y--) {
      if (board[y].every(cell => cell !== 0)) { board.splice(y, 1); board.unshift(Array(cols).fill(0)); lines++; y++; }
    }
    if (lines) { score += lines * 100; document.getElementById('score').textContent = score; }
    piece = newPiece(); px = 3; py = 0;
    if (collide(px, py, piece.shape)) board.forEach(r => r.fill(0));
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft' && !collide(px-1, py, piece.shape)) px--;
    if (e.key === 'ArrowRight' && !collide(px+1, py, piece.shape)) px++;
    if (e.key === 'ArrowDown' && !collide(px, py+1, piece.shape)) py++;
    if (e.key === 'ArrowUp') {
      const rot = piece.shape[0].map((_, i) => piece.shape.map(r => r[i]).reverse());
      if (!collide(px, py, rot)) piece.shape = rot;
    }
  });
  function loop(time = 0) {
    dropCounter++;
    if (dropCounter > 25) { if (!collide(px, py+1, piece.shape)) py++; else merge(); dropCounter = 0; }
    ctx.fillStyle = '#030712'; ctx.fillRect(0,0,c.width,c.height);
    board.forEach((r, y) => r.forEach((col, x) => {
      if (col) { ctx.fillStyle = col; ctx.fillRect(x*block, y*block, block-1, block-1); }
    }));
    piece.shape.forEach((r, y) => r.forEach((val, x) => {
      if (val) { ctx.fillStyle = piece.color; ctx.fillRect((px+x)*block, (py+y)*block, block-1, block-1); }
    }));
    requestAnimationFrame(loop);
  }
  loop();
</script>
</body>
</html>'''

    def _get_tictactoe_game_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Tic-Tac-Toe AI</title>
<style>
  body { background: #18181b; color: #f4f4f5; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  .grid { display: grid; grid-template-columns: repeat(3, 100px); grid-gap: 8px; margin: 20px 0; }
  .cell { width: 100px; height: 100px; background: #27272a; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 42px; font-weight: bold; cursor: pointer; transition: background 0.15s; }
  .cell:hover { background: #3f3f46; }
  .cell.x { color: #38bdf8; }
  .cell.o { color: #f43f5e; }
  button { background: #6366f1; border: none; color: #fff; padding: 10px 20px; font-size: 15px; border-radius: 6px; cursor: pointer; }
</style>
</head>
<body>
  <h2>Tic-Tac-Toe vs AI</h2>
  <div id="status">Your Turn (X)</div>
  <div class="grid" id="grid"></div>
  <button onclick="reset()">Restart Game</button>
<script>
  let b = Array(9).fill(null), over = false;
  const grid = document.getElementById('grid'), stat = document.getElementById('status');
  function checkWin(board) {
    const wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
    for (let [x,y,z] of wins) if (board[x] && board[x]===board[y] && board[x]===board[z]) return board[x];
    return board.every(c=>c) ? 'Tie' : null;
  }
  function click(i) {
    if (b[i] || over) return;
    b[i] = 'X'; render();
    let res = checkWin(b);
    if (res) { finish(res); return; }
    stat.textContent = "AI is thinking...";
    setTimeout(() => {
      let empty = b.map((v,idx)=>v===null?idx:null).filter(v=>v!==null);
      if (empty.length && !over) { b[empty[Math.floor(Math.random()*empty.length)]] = 'O'; }
      render();
      let r2 = checkWin(b);
      if (r2) finish(r2); else stat.textContent = "Your Turn (X)";
    }, 200);
  }
  function finish(r) { over = true; stat.textContent = r === 'Tie' ? "It's a Draw!" : `${r} Wins!`; }
  function render() {
    grid.innerHTML = '';
    b.forEach((v, i) => {
      const cell = document.createElement('div');
      cell.className = 'cell ' + (v ? v.toLowerCase() : '');
      cell.textContent = v || '';
      cell.onclick = () => click(i);
      grid.appendChild(cell);
    });
  }
  function reset() { b = Array(9).fill(null); over = false; stat.textContent = "Your Turn (X)"; render(); }
  reset();
</script>
</body>
</html>'''

    def _get_flappy_bird_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Flappy Bird HTML5</title>
<style>
  body { background: #0f172a; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  canvas { background: #38bdf8; border: 2px solid #0284c7; border-radius: 8px; }
  #score { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
</style>
</head>
<body>
  <div id="score">Score: 0</div>
  <canvas id="c" width="360" height="480"></canvas>
  <div style="margin-top: 10px; font-size: 13px; color: #94a3b8;">Click or Press Space to Jump</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  let bird = {y: 200, v: 0}, pipes = [], score = 0, over = false, frame = 0;
  function jump() { if (over) { reset(); return; } bird.v = -6; }
  document.addEventListener('keydown', e => { if (e.code === 'Space') jump(); });
  c.addEventListener('click', jump);
  function reset() { bird = {y: 200, v: 0}; pipes = []; score = 0; over = false; frame = 0; }
  function loop() {
    frame++;
    if (!over) {
      bird.v += 0.35; bird.y += bird.v;
      if (frame % 90 === 0) {
        let top = Math.random() * 200 + 40;
        pipes.push({x: 360, top: top, bottom: top + 120, passed: false});
      }
      pipes.forEach(p => {
        p.x -= 2.5;
        if (p.x < 70 && p.x + 50 > 30) {
          if (bird.y - 12 < p.top || bird.y + 12 > p.bottom) over = true;
        }
        if (!p.passed && p.x < 30) { p.passed = true; score++; document.getElementById('score').textContent = `Score: ${score}`; }
      });
      pipes = pipes.filter(p => p.x > -60);
      if (bird.y > 470 || bird.y < 0) over = true;
    }
    ctx.fillStyle = '#38bdf8'; ctx.fillRect(0,0,360,480);
    ctx.fillStyle = '#22c55e';
    pipes.forEach(p => {
      ctx.fillRect(p.x, 0, 50, p.top);
      ctx.fillRect(p.x, p.bottom, 50, 480 - p.bottom);
    });
    ctx.fillStyle = '#facc15'; ctx.beginPath(); ctx.arc(50, bird.y, 14, 0, Math.PI*2); ctx.fill();
    if (over) {
      ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0,0,360,480);
      ctx.fillStyle = '#fff'; ctx.font = '22px sans-serif'; ctx.textAlign = 'center';
      ctx.fillText('Game Over! Click to retry', 180, 240);
    }
    requestAnimationFrame(loop);
  }
  loop();
</script>
</body>
</html>'''

    def _get_space_invaders_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Space Invaders Arcade</title>
<style>
  body { background: #090a0f; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  canvas { background: #000; border: 2px solid #a855f7; border-radius: 8px; }
  #hud { font-size: 20px; font-weight: bold; margin-bottom: 8px; font-family: monospace; }
</style>
</head>
<body>
  <div id="hud">Score: <span id="sc">0</span></div>
  <canvas id="c" width="480" height="420"></canvas>
  <div style="margin-top: 10px; font-size: 13px; color: #c084fc;">Left/Right: Move • Spacebar: Fire Laser</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  let px = 220, bullets = [], aliens = [], dir = 1, score = 0, over = false;
  for (let r=0; r<4; r++) for (let col=0; col<8; col++) aliens.push({x: 50+col*45, y: 30+r*30, alive: true});
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft' && px > 10) px -= 15;
    if (e.key === 'ArrowRight' && px < 440) px += 15;
    if (e.key === ' ' && bullets.length < 3) bullets.push({x: px + 14, y: 380});
  });
  function loop() {
    ctx.fillStyle = '#000'; ctx.fillRect(0,0,480,420);
    bullets.forEach((b, bi) => {
      b.y -= 7;
      ctx.fillStyle = '#facc15'; ctx.fillRect(b.x, b.y, 4, 10);
      aliens.forEach(a => {
        if (a.alive && b.x > a.x && b.x < a.x+30 && b.y > a.y && b.y < a.y+20) {
          a.alive = false; bullets.splice(bi, 1); score += 50;
          document.getElementById('sc').textContent = score;
        }
      });
    });
    bullets = bullets.filter(b => b.y > 0);
    let edge = false;
    aliens.forEach(a => {
      if (!a.alive) return;
      a.x += dir * 0.8;
      if (a.x > 440 || a.x < 20) edge = true;
      ctx.fillStyle = '#a855f7'; ctx.fillRect(a.x, a.y, 28, 18);
    });
    if (edge) { dir = -dir; aliens.forEach(a => a.y += 10); }
    ctx.fillStyle = '#38bdf8'; ctx.fillRect(px, 390, 30, 14);
    requestAnimationFrame(loop);
  }
  loop();
</script>
</body>
</html>'''

    def _get_breakout_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Breakout / Arkanoid</title>
<style>
  body { background: #0f172a; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  canvas { background: #020617; border: 2px solid #38bdf8; border-radius: 8px; }
</style>
</head>
<body>
  <h2>Breakout Arcade</h2>
  <canvas id="c" width="480" height="360"></canvas>
  <div style="margin-top: 10px; font-size: 13px; color: #94a3b8;">Control paddle with mouse or Arrow keys</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  let px = 200, bx = 240, by = 250, dx = 3, dy = -3, bricks = [];
  for (let r=0; r<4; r++) for (let col=0; col<8; col++) bricks.push({x: 20+col*56, y: 30+r*22, active: true, col: ['#ef4444','#f97316','#eab308','#22c55e'][r]});
  c.addEventListener('mousemove', e => { const r = c.getBoundingClientRect(); px = e.clientX - r.left - 40; });
  function loop() {
    bx += dx; by += dy;
    if (bx < 6 || bx > 474) dx = -dx;
    if (by < 6) dy = -dy;
    if (by > 330 && bx > px && bx < px + 80) dy = -Math.abs(dy);
    if (by > 360) { bx = 240; by = 250; dy = -3; }
    bricks.forEach(b => {
      if (b.active && bx > b.x && bx < b.x+50 && by > b.y && by < b.y+18) {
        b.active = false; dy = -dy;
      }
    });
    ctx.fillStyle = '#020617'; ctx.fillRect(0,0,480,360);
    bricks.forEach(b => { if (b.active) { ctx.fillStyle = b.col; ctx.fillRect(b.x, b.y, 50, 18); } });
    ctx.fillStyle = '#38bdf8'; ctx.fillRect(px, 340, 80, 10);
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(bx, by, 6, 0, Math.PI*2); ctx.fill();
    requestAnimationFrame(loop);
  }
  loop();
</script>
</body>
</html>'''

    def _get_calculator_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Modern Glassmorphic Calculator</title>
<style>
  body { background: #18181b; font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  .calc { background: #27272a; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; box-shadow: 0 16px 36px rgba(0,0,0,0.5); width: 280px; }
  #screen { width: 100%; height: 50px; background: #09090b; border-radius: 8px; border: none; color: #fff; font-size: 26px; text-align: right; padding: 10px; margin-bottom: 16px; box-sizing: border-box; font-family: monospace; }
  .keys { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
  button { height: 48px; border-radius: 8px; border: none; font-size: 18px; font-weight: 600; cursor: pointer; background: #3f3f46; color: #fff; transition: background 0.15s; }
  button:hover { background: #52525b; }
  button.op { background: #cc785c; color: #fff; }
  button.op:hover { background: #de886d; }
  button.wide { grid-column: span 2; }
</style>
</head>
<body>
  <div class="calc">
    <input type="text" id="screen" value="0" readonly>
    <div class="keys">
      <button onclick="clearScr()">C</button><button onclick="delChar()">⌫</button><button class="op" onclick="press('/')">÷</button><button class="op" onclick="press('*')">×</button>
      <button onclick="press('7')">7</button><button onclick="press('8')">8</button><button onclick="press('9')">9</button><button class="op" onclick="press('-')">−</button>
      <button onclick="press('4')">4</button><button onclick="press('5')">5</button><button onclick="press('6')">6</button><button class="op" onclick="press('+')">+</button>
      <button onclick="press('1')">1</button><button onclick="press('2')">2</button><button onclick="press('3')">3</button><button class="op" onclick="calc()">=</button>
      <button class="wide" onclick="press('0')">0</button><button onclick="press('.')">.</button>
    </div>
  </div>
<script>
  let scr = document.getElementById('screen');
  function press(k) { if (scr.value === '0' && k !== '.') scr.value = ''; scr.value += k; }
  function clearScr() { scr.value = '0'; }
  function delChar() { scr.value = scr.value.slice(0,-1) || '0'; }
  function calc() { try { scr.value = Function('"use strict";return (' + scr.value + ')')(); } catch(e) { scr.value = 'Error'; } }
</script>
</body>
</html>'''

    def _get_todo_app_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Modern Task Manager</title>
<style>
  body { background: #121318; color: #fff; font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
  .box { background: #1a1b24; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; width: 400px; padding: 24px; box-shadow: 0 12px 30px rgba(0,0,0,0.4); }
  h2 { margin-top: 0; font-size: 20px; color: #a855f7; }
  .add-row { display: flex; gap: 8px; margin-bottom: 16px; }
  input { flex: 1; background: #252736; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 10px; color: #fff; outline: none; }
  button { background: #a855f7; border: none; border-radius: 6px; color: #fff; font-weight: 600; padding: 10px 16px; cursor: pointer; }
  ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
  li { background: #252736; border-radius: 6px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
  li.done span { text-decoration: line-through; opacity: 0.5; }
  .del { background: transparent; border: none; color: #ef4444; cursor: pointer; font-size: 16px; }
</style>
</head>
<body>
  <div class="box">
    <h2>Task Board</h2>
    <div class="add-row">
      <input id="in" placeholder="Enter task title...">
      <button onclick="add()">Add</button>
    </div>
    <ul id="list"></ul>
  </div>
<script>
  let tasks = [{text: 'Review system design invariants', done: true}, {text: 'Deploy MCP server', done: false}];
  function render() {
    const list = document.getElementById('list'); list.innerHTML = '';
    tasks.forEach((t, i) => {
      const li = document.createElement('li'); if (t.done) li.className = 'done';
      li.innerHTML = `<span onclick="toggle(${i})" style="cursor:pointer">${t.text}</span><button class="del" onclick="del(${i})">&times;</button>`;
      list.appendChild(li);
    });
  }
  function add() { const inp = document.getElementById('in'); if (!inp.value.trim()) return; tasks.push({text: inp.value.trim(), done: false}); inp.value = ''; render(); }
  function toggle(i) { tasks[i].done = !tasks[i].done; render(); }
  function del(i) { tasks.splice(i, 1); render(); }
  render();
</script>
</body>
</html>'''

    def _get_generic_canvas_game_html(self, target_task: str) -> str:
        safe_title = re.sub(r'[^a-zA-Z0-9 ]', '', target_task)[:30] or "Interactive Game"
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>{safe_title}</title>
<style>
  body {{ background: #0f111a; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
  canvas {{ background: #000; border: 2px solid #6366f1; border-radius: 8px; box-shadow: 0 0 20px rgba(99,102,241,0.25); }}
  #hud {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #a5b4fc; }}
</style>
</head>
<body>
  <div id="hud">Score: <span id="s">0</span> | {safe_title}</div>
  <canvas id="c" width="500" height="380"></canvas>
  <div style="margin-top: 10px; font-size: 13px; color: #94a3b8;">Use Arrow Keys or WASD to navigate</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  let px = 250, py = 190, score = 0, items = [];
  for (let i=0; i<6; i++) items.push({{x: Math.random()*460+20, y: Math.random()*340+20, r: 8}});
  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowUp' || e.key === 'w') py = Math.max(15, py - 12);
    if (e.key === 'ArrowDown' || e.key === 's') py = Math.min(365, py + 12);
    if (e.key === 'ArrowLeft' || e.key === 'a') px = Math.max(15, px - 12);
    if (e.key === 'ArrowRight' || e.key === 'd') px = Math.min(485, px + 12);
  }});
  function loop() {{
    ctx.fillStyle = '#080911'; ctx.fillRect(0,0,500,380);
    items.forEach(it => {{
      ctx.fillStyle = '#facc15'; ctx.beginPath(); ctx.arc(it.x, it.y, it.r, 0, Math.PI*2); ctx.fill();
      const dist = Math.hypot(it.x - px, it.y - py);
      if (dist < 20) {{ it.x = Math.random()*460+20; it.y = Math.random()*340+20; score += 25; document.getElementById('s').textContent = score; }}
    }});
    ctx.fillStyle = '#6366f1'; ctx.beginPath(); ctx.arc(px, py, 14, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#38bdf8'; ctx.beginPath(); ctx.arc(px, py, 6, 0, Math.PI*2); ctx.fill();
    requestAnimationFrame(loop);
  }}
  loop();
</script>
</body>
</html>'''

    def _synthesize_python_code(self, prompt: str) -> str:
        """Synthesizes valid, verified Python functions for general prompts."""
        p_lower = prompt.lower()
        if "fibonacci" in p_lower:
            return (
                "```python\n"
                "def fibonacci(n: int) -> int:\n"
                "    \"\"\"Compute the nth Fibonacci number efficiently with boundary guards.\"\"\"\n"
                "    if not isinstance(n, int) or n <= 0:\n"
                "        return 0\n"
                "    if n == 1:\n"
                "        return 1\n"
                "    a, b = 0, 1\n"
                "    for _ in range(2, n + 1):\n"
                "        a, b = b, a + b\n"
                "    return b\n"
                "```"
            )
        if "binary" in p_lower and "search" in p_lower:
            return (
                "```python\n"
                "def binary_search(arr, target):\n"
                "    \"\"\"Binary search on a sorted sequence.\"\"\"\n"
                "    if not arr:\n"
                "        return -1\n"
                "    low, high = 0, len(arr) - 1\n"
                "    while low <= high:\n"
                "        mid = (low + high) // 2\n"
                "        if arr[mid] == target:\n"
                "            return mid\n"
                "        elif arr[mid] < target:\n"
                "            low = mid + 1\n"
                "        else:\n"
                "            high = mid - 1\n"
                "    return -1\n"
                "```"
            )
        if "reverse" in p_lower and "string" in p_lower:
            return (
                "```python\n"
                "def reverse_string(s: str) -> str:\n"
                "    \"\"\"Reverse input string with type validation.\"\"\"\n"
                "    if not isinstance(s, str):\n"
                "        return ''\n"
                "    return s[::-1]\n"
                "```"
            )
        if "palindrome" in p_lower:
            return (
                "```python\n"
                "def is_palindrome(s: str) -> bool:\n"
                "    \"\"\"Check if string is a palindrome ignoring non-alphanumerics.\"\"\"\n"
                "    if not isinstance(s, str):\n"
                "        return False\n"
                "    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n"
                "    return cleaned == cleaned[::-1]\n"
                "```"
            )
        if "prime" in p_lower:
            return (
                "```python\n"
                "def is_prime(n: int) -> bool:\n"
                "    \"\"\"Determine primality with domain boundary guards.\"\"\"\n"
                "    if not isinstance(n, int) or n < 2:\n"
                "        return False\n"
                "    for i in range(2, int(n**0.5) + 1):\n"
                "        if n % i == 0:\n"
                "            return False\n"
                "    return True\n"
                "```"
            )
        if "sort" in p_lower or "quicksort" in p_lower:
            return (
                "```python\n"
                "def quicksort(arr):\n"
                "    \"\"\"Quicksort algorithm with array bounds validation.\"\"\"\n"
                "    if not arr or len(arr) <= 1:\n"
                "        return arr or []\n"
                "    pivot = arr[len(arr) // 2]\n"
                "    left = [x for x in arr if x < pivot]\n"
                "    mid = [x for x in arr if x == pivot]\n"
                "    right = [x for x in arr if x > pivot]\n"
                "    return quicksort(left) + mid + quicksort(right)\n"
                "```"
            )

        if "factorial" in p_lower:
            return (
                "```python\n"
                "def factorial(n: int) -> int:\n"
                "    \"\"\"Compute factorial with boundary and domain invariance.\"\"\"\n"
                "    if not isinstance(n, int) or n < 0:\n"
                "        raise ValueError('Factorial input must be non-negative integer.')\n"
                "    if n <= 1:\n"
                "        return 1\n"
                "    result = 1\n"
                "    for i in range(2, n + 1):\n"
                "        result *= i\n"
                "    return result\n"
                "```"
            )
        if "matrix" in p_lower and ("mult" in p_lower or "dot" in p_lower or "prod" in p_lower):
            return (
                "```python\n"
                "def matrix_multiply(A, B):\n"
                "    \"\"\"Multiply two 2D matrices asserting dimension invariants.\"\"\"\n"
                "    if not A or not B or not A[0] or not B[0]:\n"
                "        return []\n"
                "    if len(A[0]) != len(B):\n"
                "        raise ValueError(f'Incompatible inner dimensions: {len(A[0])} vs {len(B)}')\n"
                "    rows, cols, inner = len(A), len(B[0]), len(B)\n"
                "    C = [[0] * cols for _ in range(rows)]\n"
                "    for i in range(rows):\n"
                "        for j in range(cols):\n"
                "            for k in range(inner):\n"
                "                C[i][j] += A[i][k] * B[k][j]\n"
                "    return C\n"
                "```"
            )

        match = re.search(r'(?:def|function|implement|write(?:\s+a)?)\s+([a-zA-Z_][a-zA-Z0-9_]*)', prompt, re.IGNORECASE)
        fn_name = match.group(1) if match else "solve"
        if fn_name.lower() in ["code", "program", "function", "script", "solution", "the", "a", "an", "for"]:
            fn_name = "solve"

        return (
            "```python\n"
            f"def {fn_name}(*args, **kwargs):\n"
            f"    \"\"\"Synthesized invariant-verified solution for: {prompt[:60]}...\"\"\"\n"
            "    if not args and not kwargs:\n"
            "        return 'Verified Result'\n"
            "    if args:\n"
            "        arg0 = args[0]\n"
            "        if isinstance(arg0, (int, float)):\n"
            "            return arg0 * 2\n"
            "        elif isinstance(arg0, str):\n"
            "            return arg0.strip().title()\n"
            "        elif isinstance(arg0, (list, tuple)):\n"
            "            return list(reversed(arg0))\n"
            "    return 'Execution Success'\n"
            "```"
        )

    def _get_generic_canvas_game_html(self, target_task: str) -> str:
        """Returns a complete, self-contained, responsive HTML5 Arcade canvas game for any generic prompt."""
        clean_title = target_task.replace('"', '').replace("'", '').strip()[:40].title() or "Neon Arcade Sandbox"
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>{clean_title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
  body {{ background: #0b0f19; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow: hidden; }}
  #game-container {{ position: relative; width: 680px; height: 460px; background: #030712; border: 2px solid #38bdf8; border-radius: 12px; box-shadow: 0 0 30px rgba(56,189,248,0.25); overflow: hidden; }}
  canvas {{ display: block; width: 100%; height: 100%; }}
  #ui {{ position: absolute; top: 12px; left: 16px; right: 16px; display: flex; justify-content: space-between; font-size: 15px; font-weight: bold; pointer-events: none; text-shadow: 0 0 8px rgba(0,0,0,0.8); z-index: 10; }}
  .badge {{ background: rgba(15,23,42,0.75); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(56,189,248,0.4); }}
  #overlay {{ position: absolute; inset: 0; background: rgba(3,7,18,0.85); display: none; flex-direction: column; align-items: center; justify-content: center; gap: 14px; z-index: 20; }}
  #overlay h2 {{ font-size: 28px; color: #f43f5e; text-shadow: 0 0 12px rgba(244,63,94,0.6); }}
  #overlay button {{ background: #38bdf8; color: #030712; border: none; font-weight: bold; padding: 10px 22px; border-radius: 6px; cursor: pointer; font-size: 15px; transition: transform 0.1s; }}
  #overlay button:hover {{ transform: scale(1.05); background: #7dd3fc; }}
  .instructions {{ margin-top: 10px; font-size: 13px; color: #94a3b8; }}
</style>
</head>
<body>
  <div id="game-container">
    <div id="ui">
      <div class="badge">Score: <span id="score-val" style="color:#38bdf8">0</span></div>
      <div class="badge">{clean_title}</div>
      <div class="badge">Shield: <span id="health-val" style="color:#10b981">100%</span></div>
    </div>
    <div id="overlay">
      <h2 id="over-title">MISSION FAILED</h2>
      <p style="color:#cbd5e1">Final Score: <span id="final-score" style="font-weight:bold;color:#38bdf8">0</span></p>
      <button onclick="restartGame()">Play Again</button>
    </div>
    <canvas id="canvas" width="680" height="460"></canvas>
  </div>
  <div class="instructions">Use [Arrow Keys] or [WASD] to Navigate • Collect Orbs • Evade Hazard Hazards</div>
<script>
  const canvas = document.getElementById('canvas'), ctx = canvas.getContext('2d');
  let player = {{ x: 340, y: 230, vx: 0, vy: 0, size: 14, speed: 4.5 }};
  let score = 0, health = 100, isOver = false, keys = {{}};
  let particles = [], orbs = [], hazards = [];

  function spawnOrb() {{
    orbs.push({{ x: 30 + Math.random() * (canvas.width - 60), y: 30 + Math.random() * (canvas.height - 60), r: 7, pulse: 0 }});
  }}
  function spawnHazard() {{
    const side = Math.floor(Math.random() * 4);
    let x, y, vx, vy;
    if (side === 0) {{ x = Math.random() * canvas.width; y = -20; vx = (Math.random()-0.5)*3; vy = 1.5 + Math.random()*2; }}
    else if (side === 1) {{ x = canvas.width + 20; y = Math.random() * canvas.height; vx = -(1.5 + Math.random()*2); vy = (Math.random()-0.5)*3; }}
    else if (side === 2) {{ x = Math.random() * canvas.width; y = canvas.height + 20; vx = (Math.random()-0.5)*3; vy = -(1.5 + Math.random()*2); }}
    else {{ x = -20; y = Math.random() * canvas.height; vx = 1.5 + Math.random()*2; vy = (Math.random()-0.5)*3; }}
    hazards.push({{ x, y, vx, vy, size: 12 + Math.random() * 10, hue: Math.random() * 40 }});
  }}

  for(let i=0; i<6; i++) spawnOrb();

  window.addEventListener('keydown', e => {{ keys[e.key.toLowerCase()] = true; if(e.key === ' ' && isOver) restartGame(); }});
  window.addEventListener('keyup', e => {{ keys[e.key.toLowerCase()] = false; }});

  let hazardTimer = 0;
  function update(dt) {{
    if (isOver) return;
    let dx = 0, dy = 0;
    if (keys['arrowup'] || keys['w']) dy -= 1;
    if (keys['arrowdown'] || keys['s']) dy += 1;
    if (keys['arrowleft'] || keys['a']) dx -= 1;
    if (keys['arrowright'] || keys['d']) dx += 1;
    const len = Math.hypot(dx, dy) || 1;
    if (dx || dy) {{
      player.vx = (dx / len) * player.speed;
      player.vy = (dy / len) * player.speed;
      particles.push({{ x: player.x, y: player.y, r: 4, alpha: 0.8, color: '#38bdf8' }});
    }} else {{
      player.vx *= 0.88; player.vy *= 0.88;
    }}
    player.x = Math.max(player.size, Math.min(canvas.width - player.size, player.x + player.vx));
    player.y = Math.max(player.size, Math.min(canvas.height - player.size, player.y + player.vy));

    // Spawn hazards
    hazardTimer++;
    if (hazardTimer % 45 === 0 && hazards.length < 18) spawnHazard();

    // Update hazards
    for (let i = hazards.length - 1; i >= 0; i--) {{
      const h = hazards[i];
      h.x += h.vx; h.y += h.vy;
      if (Math.hypot(player.x - h.x, player.y - h.y) < player.size + h.size) {{
        health -= 25;
        hazards.splice(i, 1);
        document.getElementById('health-val').textContent = Math.max(0, health) + '%';
        if (health <= 0) gameOver();
        continue;
      }}
      if (h.x < -40 || h.x > canvas.width + 40 || h.y < -40 || h.y > canvas.height + 40) {{
        hazards.splice(i, 1);
      }}
    }}

    // Check orbs
    for (let i = orbs.length - 1; i >= 0; i--) {{
      const o = orbs[i];
      o.pulse += 0.08;
      if (Math.hypot(player.x - o.x, player.y - o.y) < player.size + o.r + 4) {{
        score += 100;
        document.getElementById('score-val').textContent = score;
        for (let p = 0; p < 8; p++) particles.push({{ x: o.x, y: o.y, vx: (Math.random()-0.5)*5, vy: (Math.random()-0.5)*5, r: 3, alpha: 1, color: '#fbbf24' }});
        orbs.splice(i, 1);
        spawnOrb();
      }}
    }}

    // Particles
    for (let i = particles.length - 1; i >= 0; i--) {{
      const p = particles[i];
      if (p.vx) p.x += p.vx;
      if (p.vy) p.y += p.vy;
      p.alpha -= 0.03;
      if (p.alpha <= 0) particles.splice(i, 1);
    }}
  }}

  function render() {{
    ctx.fillStyle = '#030712';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid lines
    ctx.strokeStyle = 'rgba(56,189,248,0.06)';
    ctx.lineWidth = 1;
    for(let x = 0; x < canvas.width; x += 30) {{ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }}
    for(let y = 0; y < canvas.height; y += 30) {{ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }}

    // Particles
    particles.forEach(p => {{
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI*2); ctx.fill();
    }});
    ctx.globalAlpha = 1;

    // Orbs
    orbs.forEach(o => {{
      ctx.shadowColor = '#fbbf24'; ctx.shadowBlur = 10;
      ctx.fillStyle = '#fbbf24';
      ctx.beginPath(); ctx.arc(o.x, o.y, o.r + Math.sin(o.pulse)*1.5, 0, Math.PI*2); ctx.fill();
    }});

    // Hazards
    hazards.forEach(h => {{
      ctx.shadowColor = '#f43f5e'; ctx.shadowBlur = 12;
      ctx.fillStyle = '#f43f5e';
      ctx.beginPath(); ctx.arc(h.x, h.y, h.size, 0, Math.PI*2); ctx.fill();
    }});

    // Player
    ctx.shadowColor = '#38bdf8'; ctx.shadowBlur = 15;
    ctx.fillStyle = '#38bdf8';
    ctx.beginPath(); ctx.arc(player.x, player.y, player.size, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#f8fafc';
    ctx.beginPath(); ctx.arc(player.x + player.vx*1.2, player.y + player.vy*1.2, 5, 0, Math.PI*2); ctx.fill();
    ctx.shadowBlur = 0;
  }}

  function loop() {{
    update();
    render();
    requestAnimationFrame(loop);
  }}

  function gameOver() {{
    isOver = true;
    document.getElementById('final-score').textContent = score;
    document.getElementById('overlay').style.display = 'flex';
  }}

  function restartGame() {{
    player = {{ x: 340, y: 230, vx: 0, vy: 0, size: 14, speed: 4.5 }};
    score = 0; health = 100; isOver = false;
    hazards = []; particles = []; orbs = [];
    for(let i=0; i<6; i++) spawnOrb();
    document.getElementById('score-val').textContent = '0';
    document.getElementById('health-val').textContent = '100%';
    document.getElementById('overlay').style.display = 'none';
  }}

  requestAnimationFrame(loop);
</script>
</body>
</html>'''

    def _get_minesweeper_html(self) -> str:
        """Returns a complete, self-contained HTML5 Minesweeper application."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Neon Minesweeper</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
  #hud { display: flex; justify-content: space-between; width: 360px; margin-bottom: 12px; font-weight: bold; }
  #board { display: grid; grid-template-columns: repeat(9, 38px); grid-gap: 3px; background: #1e293b; padding: 8px; border-radius: 8px; border: 2px solid #38bdf8; }
  .cell { width: 38px; height: 38px; background: #334155; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: bold; cursor: pointer; font-size: 16px; transition: background 0.1s; }
  .cell:hover { background: #475569; }
  .cell.revealed { background: #0f172a; cursor: default; }
  .cell.mine { background: #e11d48; }
  #status { margin-top: 12px; font-size: 14px; color: #94a3b8; }
  button.reset { margin-top: 8px; background: #38bdf8; color: #020617; border: none; font-weight: bold; padding: 6px 16px; border-radius: 4px; cursor: pointer; }
</style>
</head>
<body>
  <div id="hud"><span>Mines: <span id="mines-left">10</span></span><span>Timer: <span id="timer">0s</span></span></div>
  <div id="board"></div>
  <div id="status">Left-click to reveal • Right-click to flag</div>
  <button class="reset" onclick="init()">Restart</button>
<script>
  const rows = 9, cols = 9, totalMines = 10;
  let grid = [], revealed = 0, gameOver = false, timer = 0, timerId = null;
  function init() {
    clearInterval(timerId); timer = 0; gameOver = false; revealed = 0;
    document.getElementById('timer').textContent = '0s';
    document.getElementById('mines-left').textContent = totalMines;
    document.getElementById('status').textContent = 'Left-click to reveal • Right-click to flag';
    grid = Array.from({length: rows}, () => Array.from({length: cols}, () => ({mine: false, rev: false, flag: false, count: 0})));
    let placed = 0;
    while (placed < totalMines) {
      let r = Math.floor(Math.random()*rows), c = Math.floor(Math.random()*cols);
      if (!grid[r][c].mine) { grid[r][c].mine = true; placed++; }
    }
    for(let r=0; r<rows; r++) {
      for(let c=0; c<cols; c++) {
        if (grid[r][c].mine) continue;
        let cnt = 0;
        for(let dr=-1; dr<=1; dr++) for(let dc=-1; dc<=1; dc++) {
          let nr = r+dr, nc = c+dc;
          if (nr>=0 && nr<rows && nc>=0 && nc<cols && grid[nr][nc].mine) cnt++;
        }
        grid[r][c].count = cnt;
      }
    }
    render();
    timerId = setInterval(() => { timer++; document.getElementById('timer').textContent = timer + 's'; }, 1000);
  }
  function render() {
    const b = document.getElementById('board'); b.innerHTML = '';
    for(let r=0; r<rows; r++) {
      for(let c=0; c<cols; c++) {
        const d = document.createElement('div');
        d.className = 'cell' + (grid[r][c].rev ? ' revealed' : '') + (grid[r][c].rev && grid[r][c].mine ? ' mine' : '');
        if (grid[r][c].rev) {
          if (grid[r][c].mine) d.textContent = '💣';
          else if (grid[r][c].count > 0) d.textContent = grid[r][c].count;
        } else if (grid[r][c].flag) {
          d.textContent = '🚩';
        }
        d.onclick = () => reveal(r, c);
        d.oncontextmenu = (e) => { e.preventDefault(); flag(r, c); };
        b.appendChild(d);
      }
    }
  }
  function flag(r, c) {
    if (gameOver || grid[r][c].rev) return;
    grid[r][c].flag = !grid[r][c].flag;
    render();
  }
  function reveal(r, c) {
    if (gameOver || grid[r][c].rev || grid[r][c].flag) return;
    grid[r][c].rev = true;
    if (grid[r][c].mine) {
      gameOver = true; clearInterval(timerId);
      document.getElementById('status').textContent = '💥 Game Over! You hit a mine.';
      for(let i=0; i<rows; i++) for(let j=0; j<cols; j++) if(grid[i][j].mine) grid[i][j].rev = true;
      render();
      return;
    }
    revealed++;
    if (grid[r][c].count === 0) {
      for(let dr=-1; dr<=1; dr++) for(let dc=-1; dc<=1; dc++) {
        let nr = r+dr, nc = c+dc;
        if (nr>=0 && nr<rows && nc>=0 && nc<cols && !grid[nr][nc].rev) reveal(nr, nc);
      }
    }
    if (revealed === rows*cols - totalMines) {
      gameOver = true; clearInterval(timerId);
      document.getElementById('status').textContent = '🎉 Congratulations! You cleared the field!';
    }
    render();
  }
  init();
</script>
</body>
</html>'''

    def _get_maze_game_html(self) -> str:
        """Returns a complete, self-contained HTML5 Procedural Maze game."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Neon Maze Runner</title>
<style>
  body { background: #020617; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  #hud { font-size: 16px; margin-bottom: 10px; font-weight: bold; }
  canvas { background: #0f172a; border: 2px solid #38bdf8; border-radius: 8px; box-shadow: 0 0 20px rgba(56,189,248,0.25); }
  .ctrl { margin-top: 10px; font-size: 13px; color: #94a3b8; }
</style>
</head>
<body>
  <div id="hud">Reach the Green Portal! • Moves: <span id="moves">0</span></div>
  <canvas id="c" width="420" height="420"></canvas>
  <div class="ctrl">Use Arrow Keys or WASD to navigate • Space to generate new maze</div>
<script>
  const c = document.getElementById('c'), ctx = c.getContext('2d'), sz = 21, cs = 20;
  let maze = [], px = 1, py = 1, gx = sz - 2, gy = sz - 2, moves = 0;
  function gen() {
    moves = 0; document.getElementById('moves').textContent = '0';
    maze = Array.from({length: sz}, () => Array(sz).fill(1));
    function carve(x, y) {
      maze[y][x] = 0;
      const dirs = [[0,-2],[0,2],[-2,0],[2,0]].sort(() => Math.random()-0.5);
      for(const [dx, dy] of dirs) {
        const nx = x+dx, ny = y+dy;
        if(nx>0 && nx<sz-1 && ny>0 && ny<sz-1 && maze[ny][nx] === 1) {
          maze[y+dy/2][x+dx/2] = 0;
          carve(nx, ny);
        }
      }
    }
    carve(1, 1);
    maze[gy][gx] = 0;
    px = 1; py = 1;
    draw();
  }
  function draw() {
    ctx.fillStyle = '#0f172a'; ctx.fillRect(0, 0, 420, 420);
    for(let y=0; y<sz; y++) for(let x=0; x<sz; x++) {
      if(maze[y][x] === 1) { ctx.fillStyle = '#1e293b'; ctx.fillRect(x*cs, y*cs, cs, cs); }
    }
    ctx.fillStyle = '#10b981'; ctx.shadowColor = '#10b981'; ctx.shadowBlur = 10;
    ctx.fillRect(gx*cs+2, gy*cs+2, cs-4, cs-4);
    ctx.fillStyle = '#38bdf8'; ctx.shadowColor = '#38bdf8'; ctx.shadowBlur = 12;
    ctx.beginPath(); ctx.arc(px*cs+cs/2, py*cs+cs/2, cs/2-2, 0, Math.PI*2); ctx.fill();
    ctx.shadowBlur = 0;
  }
  window.addEventListener('keydown', e => {
    let dx = 0, dy = 0;
    if(e.key === 'ArrowUp' || e.key.toLowerCase() === 'w') dy = -1;
    if(e.key === 'ArrowDown' || e.key.toLowerCase() === 's') dy = 1;
    if(e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') dx = -1;
    if(e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') dx = 1;
    if(e.key === ' ') { gen(); return; }
    if(dx !== 0 || dy !== 0) {
      if(maze[py+dy] && maze[py+dy][px+dx] === 0) {
        px += dx; py += dy; moves++;
        document.getElementById('moves').textContent = moves;
        draw();
        if(px === gx && py === gy) { setTimeout(() => { alert('🏆 Maze Solved in ' + moves + ' moves!'); gen(); }, 50); }
      }
    }
  });
  gen();
</script>
</body>
</html>'''

    def _get_memory_game_html(self) -> str:
        """Returns a complete, self-contained HTML5 Card Matching Memory game."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Cyber Memory Match</title>
<style>
  body { background: #090d16; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  #hud { display: flex; gap: 24px; font-size: 16px; margin-bottom: 16px; font-weight: bold; }
  #grid { display: grid; grid-template-columns: repeat(4, 75px); grid-gap: 12px; }
  .card { width: 75px; height: 75px; background: #1e293b; border: 2px solid #38bdf8; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 28px; cursor: pointer; transition: transform 0.2s, background 0.2s; }
  .card:hover { transform: scale(1.05); }
  .card.flipped { background: #0284c7; }
  .card.matched { background: #059669; border-color: #34d399; cursor: default; transform: none; }
  button { margin-top: 16px; background: #38bdf8; color: #020617; border: none; font-weight: bold; padding: 8px 18px; border-radius: 6px; cursor: pointer; }
</style>
</head>
<body>
  <div id="hud"><span>Moves: <span id="m">0</span></span><span>Matches: <span id="matched">0/8</span></span></div>
  <div id="grid"></div>
  <button onclick="init()">Restart Game</button>
<script>
  const icons = ['⚡', '💎', '🔥', '🚀', '⭐', '🧬', '🛡️', '🎯'];
  let cards = [], first = null, second = null, lock = false, moves = 0, matches = 0;
  function init() {
    moves = 0; matches = 0; first = null; second = null; lock = false;
    document.getElementById('m').textContent = '0';
    document.getElementById('matched').textContent = '0/8';
    cards = [...icons, ...icons].sort(() => Math.random() - 0.5);
    const g = document.getElementById('grid'); g.innerHTML = '';
    cards.forEach((val, i) => {
      const c = document.createElement('div');
      c.className = 'card';
      c.dataset.val = val; c.dataset.i = i;
      c.onclick = () => flip(c);
      g.appendChild(c);
    });
  }
  function flip(c) {
    if (lock || c.classList.contains('flipped') || c.classList.contains('matched')) return;
    c.classList.add('flipped');
    c.textContent = c.dataset.val;
    if (!first) { first = c; return; }
    second = c; moves++;
    document.getElementById('m').textContent = moves;
    if (first.dataset.val === second.dataset.val) {
      first.classList.add('matched'); second.classList.add('matched');
      matches++; document.getElementById('matched').textContent = matches + '/8';
      first = null; second = null;
      if (matches === 8) setTimeout(() => alert('🎉 Victory! Matched all cards in ' + moves + ' moves!'), 200);
    } else {
      lock = true;
      setTimeout(() => {
        first.classList.remove('flipped'); first.textContent = '';
        second.classList.remove('flipped'); second.textContent = '';
        first = null; second = null; lock = false;
      }, 700);
    }
  }
  init();
</script>
</body>
</html>'''

    def _get_temple_run_html(self) -> str:
        """Returns a complete, self-contained, 3D perspective HTML5 Temple Run game."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Temple Run 3D - Ancient Relic Runner</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body {
    background: #0d0e15;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #e6edf3;
    overflow: hidden;
  }
  #game-wrapper {
    position: relative;
    width: 800px;
    height: 520px;
    background: #161822;
    border-radius: 12px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 30px rgba(234,158,37,0.2);
    overflow: hidden;
    border: 1px solid rgba(234,158,37,0.3);
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }
  #ui-overlay {
    position: absolute;
    top: 16px;
    left: 20px;
    right: 20px;
    display: flex;
    justify-content: space-between;
    pointer-events: none;
    font-size: 16px;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
  }
  .stat-badge {
    background: rgba(13, 14, 21, 0.75);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 6px 14px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  #center-msg {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    background: rgba(13, 14, 21, 0.92);
    border: 2px solid #ea9e25;
    border-radius: 16px;
    padding: 30px 40px;
    box-shadow: 0 0 40px rgba(234,158,37,0.4);
    display: none;
  }
  #center-msg h1 {
    font-size: 36px;
    color: #ea9e25;
    margin-bottom: 10px;
    letter-spacing: 2px;
    text-shadow: 0 0 10px rgba(234,158,37,0.5);
  }
  #center-msg p {
    font-size: 16px;
    color: #a0aec0;
    margin: 8px 0;
  }
  .btn-restart {
    margin-top: 18px;
    background: linear-gradient(135deg, #ea9e25, #c27803);
    color: #fff;
    border: none;
    padding: 10px 24px;
    font-size: 16px;
    font-weight: 700;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(234,158,37,0.4);
    transition: transform 0.15s, box-shadow 0.15s;
    pointer-events: auto;
  }
  .btn-restart:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(234,158,37,0.6);
  }
  #controls-hint {
    position: absolute;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 13px;
    color: rgba(255,255,255,0.6);
    background: rgba(0,0,0,0.6);
    padding: 4px 14px;
    border-radius: 12px;
    pointer-events: none;
  }
</style>
</head>
<body>
<div id="game-wrapper">
  <canvas id="c" width="800" height="520"></canvas>
  <div id="ui-overlay">
    <div class="stat-badge"><span>🏃</span><span id="dist-val">0 m</span></div>
    <div class="stat-badge"><span>🪙</span><span id="coin-val">0</span></div>
    <div class="stat-badge"><span>⭐</span><span id="score-val">0</span></div>
    <div class="stat-badge"><span id="lives-val">❤️❤️❤️</span></div>
  </div>
  <div id="center-msg">
    <h1 id="msg-title">GAME OVER</h1>
    <p id="msg-dist">Distance: 0 m</p>
    <p id="msg-coins">Coins: 0</p>
    <p id="msg-score">Final Score: 0</p>
    <button class="btn-restart" id="btn-restart">PLAY AGAIN (SPACE)</button>
  </div>
  <div id="controls-hint">⬅️/➡️ or A/D to Switch Lanes · ⬆️ or Space to Jump · ⬇️ or S to Slide</div>
</div>
<script>
(function() {
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  const W = 800, H = 520, HORIZON = 150;
  const LANES = [-1, 0, 1];
  
  let audioCtx = null;
  function getAudio() {
    if (!audioCtx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) audioCtx = new AC();
    }
    return audioCtx;
  }
  function playBeep(freq, type, dur, gainVal=0.1) {
    try {
      const actx = getAudio();
      if (!actx) return;
      if (actx.state === 'suspended') actx.resume();
      const osc = actx.createOscillator();
      const gain = actx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, actx.currentTime);
      gain.gain.setValueAtTime(gainVal, actx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + dur);
      osc.connect(gain);
      gain.connect(actx.destination);
      osc.start();
      osc.stop(actx.currentTime + dur);
    } catch(e) {}
  }
  function playCoin() { playBeep(880, 'sine', 0.15, 0.15); }
  function playJump() { playBeep(340, 'triangle', 0.25, 0.12); }
  function playSlide() { playBeep(180, 'sawtooth', 0.2, 0.1); }
  function playCrash() { playBeep(90, 'square', 0.4, 0.25); }

  let state = {
    distance: 0,
    coins: 0,
    score: 0,
    lives: 3,
    speed: 380,
    gameOver: false,
    roadScroll: 0
  };

  let player = {
    lane: 0,
    currentX: 0,
    targetX: 0,
    y: 0,
    vy: 0,
    isJumping: false,
    isSliding: false,
    slideTimer: 0,
    runTime: 0
  };

  let obstacles = [];
  let coins = [];
  let particles = [];
  let lastObstacleZ = 900;
  let lastCoinZ = 700;

  function resetGame() {
    state.distance = 0;
    state.coins = 0;
    state.score = 0;
    state.lives = 3;
    state.speed = 400;
    state.gameOver = false;
    state.roadScroll = 0;

    player.lane = 0;
    player.currentX = 0;
    player.targetX = 0;
    player.y = 0;
    player.vy = 0;
    player.isJumping = false;
    player.isSliding = false;
    player.slideTimer = 0;

    obstacles = [];
    coins = [];
    particles = [];
    lastObstacleZ = 800;
    lastCoinZ = 600;

    document.getElementById('center-msg').style.display = 'none';
  }

  window.addEventListener('keydown', function(e) {
    if (state.gameOver) {
      if (e.code === 'Space' || e.code === 'Enter') resetGame();
      return;
    }
    if (e.code === 'ArrowLeft' || e.code === 'KeyA') {
      if (player.lane > -1) { player.lane--; playSlide(); }
    } else if (e.code === 'ArrowRight' || e.code === 'KeyD') {
      if (player.lane < 1) { player.lane++; playSlide(); }
    } else if ((e.code === 'ArrowUp' || e.code === 'KeyW' || e.code === 'Space') && !player.isJumping) {
      player.isJumping = true;
      player.vy = 520;
      player.isSliding = false;
      playJump();
    } else if ((e.code === 'ArrowDown' || e.code === 'KeyS') && !player.isSliding) {
      player.isSliding = true;
      player.slideTimer = 0.55;
      if (player.isJumping) { player.vy = -600; }
      playSlide();
    }
  });

  document.getElementById('btn-restart').onclick = resetGame;

  function project(lane, z, heightOffGround = 0) {
    const depth = Math.max(1, z);
    const scale = 220 / (depth + 180);
    const roadWidthAtZ = 50 + (620 - 50) * Math.pow((1000 - depth) / 1000, 1.3);
    const laneSpacing = roadWidthAtZ / 3;
    const screenX = W / 2 + lane * laneSpacing;
    const screenY = HORIZON + (H - 40 - HORIZON) * Math.pow((1000 - depth) / 1000, 1.3) - heightOffGround * scale;
    return { x: screenX, y: screenY, scale: scale };
  }

  function spawnWorld() {
    while (lastObstacleZ < 2800) {
      lastObstacleZ += 280 + Math.random() * 260;
      const typeRand = Math.random();
      const lane = LANES[Math.floor(Math.random() * LANES.length)];
      if (typeRand < 0.4) {
        obstacles.push({ type: 'hurdle', lane: lane, z: lastObstacleZ, passed: false });
      } else if (typeRand < 0.75) {
        obstacles.push({ type: 'arch', lane: lane, z: lastObstacleZ, passed: false });
      } else {
        obstacles.push({ type: 'monolith', lane: lane, z: lastObstacleZ, passed: false });
      }
    }

    while (lastCoinZ < 2800) {
      lastCoinZ += 120 + Math.random() * 100;
      const lane = LANES[Math.floor(Math.random() * LANES.length)];
      const count = 3 + Math.floor(Math.random() * 4);
      for (let i = 0; i < count; i++) {
        coins.push({ lane: lane, z: lastCoinZ + i * 40, collected: false });
      }
      lastCoinZ += count * 40;
    }
  }

  function addParticles(x, y, color, count=8) {
    for (let i = 0; i < count; i++) {
      particles.push({
        x: x, y: y,
        vx: (Math.random() - 0.5) * 160,
        vy: (Math.random() - 0.8) * 180,
        life: 0.4 + Math.random() * 0.3,
        maxLife: 0.7,
        color: color,
        size: 3 + Math.random() * 4
      });
    }
  }

  let lastTime = performance.now();

  function update(dt) {
    if (state.gameOver) return;

    state.distance += state.speed * dt * 0.05;
    state.score += Math.floor(state.speed * dt * 0.1);
    state.speed = Math.min(850, state.speed + dt * 4);
    state.roadScroll = (state.roadScroll + state.speed * dt) % 100;

    player.runTime += dt * (state.speed / 200);
    player.targetX = player.lane;
    player.currentX += (player.targetX - player.currentX) * Math.min(1, dt * 14);

    if (player.isJumping) {
      player.y += player.vy * dt;
      player.vy -= 1400 * dt;
      if (player.y <= 0) {
        player.y = 0;
        player.vy = 0;
        player.isJumping = false;
      }
    }

    if (player.isSliding) {
      player.slideTimer -= dt;
      if (player.slideTimer <= 0) {
        player.isSliding = false;
      }
    }

    for (let i = 0; i < obstacles.length; i++) {
      const obs = obstacles[i];
      obs.z -= state.speed * dt;

      if (!obs.passed && obs.z > 80 && obs.z < 150) {
        const laneDiff = Math.abs(obs.lane - player.currentX);
        if (laneDiff < 0.55) {
          let hit = false;
          if (obs.type === 'hurdle' && player.y < 45) {
            hit = true;
          } else if (obs.type === 'arch' && !player.isSliding) {
            hit = true;
          } else if (obs.type === 'monolith') {
            hit = true;
          }

          if (hit) {
            obs.passed = true;
            state.lives--;
            playCrash();
            const p = project(player.currentX, 100, player.y);
            addParticles(p.x, p.y, '#e53e3e', 20);

            if (state.lives <= 0) {
              state.gameOver = true;
              document.getElementById('center-msg').style.display = 'block';
              document.getElementById('msg-dist').textContent = `Distance: ${Math.floor(state.distance)} m`;
              document.getElementById('msg-coins').textContent = `Coins: ${state.coins}`;
              document.getElementById('msg-score').textContent = `Final Score: ${state.score}`;
            }
          }
        }
      }

      if (obs.z <= 40) obs.passed = true;
    }

    for (let i = 0; i < coins.length; i++) {
      const c = coins[i];
      c.z -= state.speed * dt;
      if (!c.collected && c.z > 70 && c.z < 150) {
        const laneDiff = Math.abs(c.lane - player.currentX);
        if (laneDiff < 0.6 && player.y < 70) {
          c.collected = true;
          state.coins++;
          state.score += 50;
          playCoin();
          const p = project(c.lane, c.z, 20);
          addParticles(p.x, p.y, '#f6ad55', 10);
        }
      }
    }

    obstacles = obstacles.filter(o => o.z > 30);
    coins = coins.filter(c => c.z > 30 && !c.collected);
    lastObstacleZ -= state.speed * dt;
    lastCoinZ -= state.speed * dt;

    spawnWorld();

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.life -= dt;
      if (p.life <= 0) particles.splice(i, 1);
    }

    document.getElementById('dist-val').textContent = `${Math.floor(state.distance)} m`;
    document.getElementById('coin-val').textContent = state.coins;
    document.getElementById('score-val').textContent = state.score;
    document.getElementById('lives-val').textContent = '❤️'.repeat(Math.max(0, state.lives));
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    const bgGrad = ctx.createLinearGradient(0, 0, 0, HORIZON);
    bgGrad.addColorStop(0, '#0a0a10');
    bgGrad.addColorStop(0.7, '#1a1625');
    bgGrad.addColorStop(1, '#2c1e18');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, HORIZON);

    ctx.fillStyle = '#120d18';
    ctx.beginPath();
    ctx.moveTo(0, HORIZON);
    ctx.lineTo(250, HORIZON - 60);
    ctx.lineTo(350, HORIZON - 30);
    ctx.lineTo(400, HORIZON - 80);
    ctx.lineTo(450, HORIZON - 30);
    ctx.lineTo(550, HORIZON - 60);
    ctx.lineTo(W, HORIZON);
    ctx.fill();

    const flicker = Math.sin(performance.now() * 0.01) * 3;
    ctx.fillStyle = '#ff9900';
    ctx.beginPath();
    ctx.arc(280, HORIZON - 40, 6 + flicker, 0, Math.PI * 2);
    ctx.arc(520, HORIZON - 40, 6 - flicker, 0, Math.PI * 2);
    ctx.fill();

    const roadBottomLeft = W / 2 - 310;
    const roadBottomRight = W / 2 + 310;
    const roadTopLeft = W / 2 - 25;
    const roadTopRight = W / 2 + 25;

    const roadGrad = ctx.createLinearGradient(0, HORIZON, 0, H);
    roadGrad.addColorStop(0, '#1c1614');
    roadGrad.addColorStop(1, '#3b2f28');
    ctx.fillStyle = roadGrad;
    ctx.beginPath();
    ctx.moveTo(roadTopLeft, HORIZON);
    ctx.lineTo(roadTopRight, HORIZON);
    ctx.lineTo(roadBottomRight, H);
    ctx.lineTo(roadBottomLeft, H);
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = 'rgba(10, 8, 7, 0.4)';
    ctx.lineWidth = 2;
    for (let d = 0; d < 12; d++) {
      const zVal = ((d * 80 + state.roadScroll * 3) % 960) + 40;
      const pL = project(-1.5, zVal);
      const pR = project(1.5, zVal);
      ctx.beginPath();
      ctx.moveTo(pL.x, pL.y);
      ctx.lineTo(pR.x, pR.y);
      ctx.stroke();
    }

    ctx.strokeStyle = 'rgba(234, 158, 37, 0.25)';
    ctx.lineWidth = 2;
    [-0.5, 0.5].forEach(dividerLane => {
      const topP = project(dividerLane, 1000);
      const botP = project(dividerLane, 40);
      ctx.beginPath();
      ctx.moveTo(topP.x, topP.y);
      ctx.lineTo(botP.x, botP.y);
      ctx.stroke();
    });

    ctx.fillStyle = '#221a16';
    ctx.beginPath();
    ctx.moveTo(0, HORIZON);
    ctx.lineTo(roadTopLeft, HORIZON);
    ctx.lineTo(roadBottomLeft, H);
    ctx.lineTo(0, H);
    ctx.closePath();
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(roadTopRight, HORIZON);
    ctx.lineTo(W, HORIZON);
    ctx.lineTo(W, H);
    ctx.lineTo(roadBottomRight, H);
    ctx.closePath();
    ctx.fill();

    coins.sort((a, b) => b.z - a.z);
    for (const coin of coins) {
      if (coin.z > 950) continue;
      const p = project(coin.lane, coin.z, 28);
      const coinRadius = 14 * p.scale;
      const spinScale = Math.abs(Math.cos(performance.now() * 0.005 + coin.z));

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.scale(Math.max(0.15, spinScale), 1);
      ctx.fillStyle = '#f6e05e';
      ctx.beginPath();
      ctx.arc(0, 0, coinRadius, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#d69e2e';
      ctx.lineWidth = 2 * p.scale;
      ctx.stroke();
      ctx.fillStyle = '#b7791f';
      ctx.fillRect(-coinRadius * 0.3, -coinRadius * 0.3, coinRadius * 0.6, coinRadius * 0.6);
      ctx.restore();
    }

    obstacles.sort((a, b) => b.z - a.z);
    for (const obs of obstacles) {
      if (obs.z > 950) continue;
      const p = project(obs.lane, obs.z, 0);

      if (obs.type === 'hurdle') {
        const w = 90 * p.scale;
        const h = 45 * p.scale;
        ctx.fillStyle = '#742a2a';
        ctx.fillRect(p.x - w / 2, p.y - h, w, h);
        ctx.fillStyle = '#e53e3e';
        for (let s = 0; s < 4; s++) {
          ctx.beginPath();
          ctx.moveTo(p.x - w / 2 + s * (w / 4), p.y - h);
          ctx.lineTo(p.x - w / 2 + (s + 0.5) * (w / 4), p.y - h - 14 * p.scale);
          ctx.lineTo(p.x - w / 2 + (s + 1) * (w / 4), p.y - h);
          ctx.fill();
        }
      } else if (obs.type === 'arch') {
        const w = 110 * p.scale;
        const h = 130 * p.scale;
        ctx.fillStyle = '#4a5568';
        ctx.fillRect(p.x - w / 2, p.y - h, 14 * p.scale, h);
        ctx.fillRect(p.x + w / 2 - 14 * p.scale, p.y - h, 14 * p.scale, h);
        ctx.fillStyle = '#2d3748';
        ctx.fillRect(p.x - w / 2 - 6 * p.scale, p.y - h, w + 12 * p.scale, 40 * p.scale);
        ctx.strokeStyle = '#38a169';
        ctx.lineWidth = 3 * p.scale;
        ctx.beginPath();
        ctx.moveTo(p.x - 20 * p.scale, p.y - h + 40 * p.scale);
        ctx.lineTo(p.x - 15 * p.scale, p.y - h + 70 * p.scale);
        ctx.moveTo(p.x + 20 * p.scale, p.y - h + 40 * p.scale);
        ctx.lineTo(p.x + 25 * p.scale, p.y - h + 65 * p.scale);
        ctx.stroke();
      } else if (obs.type === 'monolith') {
        const w = 85 * p.scale;
        const h = 140 * p.scale;
        ctx.fillStyle = '#2d3748';
        ctx.fillRect(p.x - w / 2, p.y - h, w, h);
        ctx.fillStyle = '#ecc94b';
        ctx.beginPath();
        ctx.arc(p.x, p.y - h * 0.6, 12 * p.scale, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    const pp = project(player.currentX, 100, player.y);
    const pScale = pp.scale * 1.35;

    ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
    ctx.beginPath();
    const shadowP = project(player.currentX, 100, 0);
    const shadowW = (player.isSliding ? 55 : 36) * pScale * (1 - player.y / 200);
    ctx.ellipse(shadowP.x, shadowP.y, Math.max(5, shadowW), 8 * pScale, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.save();
    ctx.translate(pp.x, pp.y);

    if (player.isSliding) {
      ctx.fillStyle = '#dd6b20';
      ctx.fillRect(-22 * pScale, -18 * pScale, 44 * pScale, 14 * pScale);
      ctx.fillStyle = '#fbd38d';
      ctx.beginPath();
      ctx.arc(24 * pScale, -11 * pScale, 9 * pScale, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(214, 158, 46, 0.5)';
      ctx.fillRect(-35 * pScale, -8 * pScale, 12 * pScale, 6 * pScale);
    } else {
      const legCycle = Math.sin(player.runTime * 14);
      const leg1 = player.isJumping ? -15 : legCycle * 20;
      const leg2 = player.isJumping ? 15 : -legCycle * 20;

      ctx.strokeStyle = '#2b6cb0';
      ctx.lineWidth = 7 * pScale;
      ctx.beginPath();
      ctx.moveTo(-6 * pScale, -25 * pScale);
      ctx.lineTo(-10 * pScale + leg1 * 0.4 * pScale, 0);
      ctx.moveTo(6 * pScale, -25 * pScale);
      ctx.lineTo(10 * pScale + leg2 * 0.4 * pScale, 0);
      ctx.stroke();

      ctx.fillStyle = '#dd6b20';
      ctx.fillRect(-14 * pScale, -55 * pScale, 28 * pScale, 32 * pScale);

      ctx.fillStyle = '#744210';
      ctx.fillRect(-18 * pScale, -50 * pScale, 6 * pScale, 22 * pScale);

      ctx.fillStyle = '#fbd38d';
      ctx.beginPath();
      ctx.arc(0, -66 * pScale, 11 * pScale, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#975a16';
      ctx.fillRect(-16 * pScale, -75 * pScale, 32 * pScale, 6 * pScale);
      ctx.fillRect(-10 * pScale, -83 * pScale, 20 * pScale, 9 * pScale);

      ctx.strokeStyle = '#744210';
      ctx.lineWidth = 3 * pScale;
      ctx.beginPath();
      ctx.moveTo(14 * pScale, -42 * pScale);
      ctx.lineTo(24 * pScale, -56 * pScale);
      ctx.stroke();
      ctx.fillStyle = '#ff9900';
      ctx.beginPath();
      ctx.arc(24 * pScale, -59 * pScale + Math.sin(performance.now() * 0.02) * 2, 6 * pScale, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    for (const p of particles) {
      const alpha = Math.max(0, p.life / p.maxLife);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = alpha;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1.0;
    }
  }

  function loop(timestamp) {
    const dt = Math.min(0.1, (timestamp - lastTime) / 1000);
    lastTime = timestamp;

    update(dt);
    draw();

    requestAnimationFrame(loop);
  }

  resetGame();
  requestAnimationFrame(loop);
})();
</script>
</body>
</html>'''


# Backward compatibility alias
MockProvider = MockLLMProvider
