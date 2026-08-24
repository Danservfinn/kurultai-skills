# Tests

Manual checklist for a reviewer on macOS with Docker Desktop and Ollama installed.

1. **Config correctness:** `grep -A4 '^model:' <HOST_CONFIG_PATH>` shows `base_url: http://host.docker.internal:11434/v1` (with scheme and `/v1`) and a model name that appears in `ollama list` output.
2. **Persistence:** `docker inspect <CONTAINER> --format '{{json .Mounts}}'` shows a bind mount for config.yaml from the host. Then `docker compose up -d` in `<COMPOSE_DIR>` and re-check the config inside the container (`docker exec <CONTAINER> cat <CONTAINER_CONFIG_PATH>`) — the edit survives recreation.
3. **Connectivity:** `docker exec <CONTAINER> curl -s http://host.docker.internal:11434/v1/models` (or the curlimages/curl fallback) prints a JSON body containing `"id"` entries for the host's models. Do not rely on exit code alone — `curl` without `-f` exits 0 on HTTP 404/500; verify the body.
4. **End-to-end:** send a chat request through Hermes and confirm the response comes from the configured Ollama model (watch `ollama serve` logs or `docker logs <CONTAINER>`).
5. **Auto-start:** Compose file contains `restart: unless-stopped` for the Hermes service; Docker Desktop "Start when you sign in" is checked; Ollama appears in System Settings > General > Login Items.
6. **Security check:** if `OLLAMA_HOST=0.0.0.0` was set, `lsof -iTCP:11434 -sTCP:LISTEN` shows Ollama listening on `*:11434` — confirm the machine is on a trusted network, and confirm `launchctl getenv OLLAMA_HOST` returns nothing if the env-var method was not intended to persist.