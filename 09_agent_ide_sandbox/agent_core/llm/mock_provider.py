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
            if any(k in target_task for k in ["temple", "game", "canvas"]) or "<canvas" in p_lower:
                return f"```html\n{self._get_temple_run_html()}\n```"
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
                call_args = ", ".join(["1" if i == 0 else "0" for i in range(len(args))])
                return (
                    "```python\n"
                    f"res = {fn}({call_args})\n"
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
        if any(k in target_task for k in ["temple", "runner", "game", "canvas", "arcade", "play"]):
            return f"```html\n{self._get_temple_run_html()}\n```"

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

        # LOGOS Axiomatic / Pondering reasoning (textual queries)
        if "axiom" in p_lower or "ponder" in p_lower or "logos" in p_lower:
            return (
                "### LOGOS Axiomatic Derivation & Pondering Analysis\n"
                "- Angle 1 (Information Density): Incompressible token structures identified.\n"
                "- Angle 2 (Boundary Constraints): Divisor non-zero invariant enforced at boundary.\n"
                "- Angle 3 (Operator Symmetries): Commutative and zero-annihilator properties mapped.\n"
                "Confidence Score: 0.98 (>95% threshold passed).\n"
            )

        return self._synthesize_python_code(prompt)

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
