# Limitations

- **The in-app runner is not an OS sandbox.** `CodeExecutionSandbox` runs `python -I` in a temp dir
  with a timeout. It applies no CPU, memory, network or filesystem isolation. The earlier
  README's "isolated Docker sandbox with resource limits" claim did not match the code and has
  been removed. For untrusted code, run the whole app in the provided container with
  `--network none --memory ... --cpus ...`, or use a VM.
- **The static guard is incomplete by construction.** Computed names such as
  `getattr(os, 'sys' + 'tem')` are not caught, and a test asserts this so it stays visible. The
  attack corpus (22 cases) was written alongside the guard, so 22/22 is an in-sample regression
  number, not a security evaluation.
- **No model-quality numbers.** The pipeline benchmark uses the canned *mock* provider, so it
  measures orchestration overhead only.
- **LOGOS module names are metaphors.** Names like MERA, holographic memory and NAS topology
  describe heuristic prompt-planning and text-ranking code. They do not implement the physics
  or the ML methods they are named after.
- **Single user, loopback only.** There is no authentication. Do not expose the server.
- **Typing debt.** 9 legacy modules are excluded from the mypy gate (see `pyproject.toml`).
- **Docker image not built locally.** There was no Docker daemon in the authoring environment,
  and CI does not build the image.
