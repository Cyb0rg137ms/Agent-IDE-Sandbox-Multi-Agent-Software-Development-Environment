# CPU-only image. The container adds process/filesystem isolation that the in-app
# subprocess runner does NOT provide on its own; add --network none / --memory / --cpus
# at run time for resource limits.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE run_web_ui.py ./
COPY agent_core ./agent_core
COPY server ./server
COPY web ./web
RUN pip install --no-cache-dir . && useradd -m ide
USER ide
WORKDIR /home/ide
EXPOSE 8000
# docker run --rm -p 127.0.0.1:8000:8000 --memory 1g --cpus 2 agent-ide
CMD ["agent-ide", "--host", "0.0.0.0", "--port", "8000", "--no-browser"]
