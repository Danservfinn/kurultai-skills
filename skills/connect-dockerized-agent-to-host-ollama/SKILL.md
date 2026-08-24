---
name: connect-dockerized-agent-to-host-ollama
description: Configure Hermes in Docker to reach an Ollama server on the macOS host (e.g. MLX backend), verify connectivity, and set up auto-start
category: infrastructure
---

# Connect a Dockerized Agent to Host Ollama

## Goal

Make a Hermes agent running inside a Docker container use an Ollama server on the macOS host (so MLX-backed models on Apple Silicon work), verify the connection, and make the stack start automatically after login.

## Inputs

- Hermes `config.yaml` accessible on the host (recommended: bind-mounted into the container, not edited inside it)
- Ollama installed and running on the host (`ollama list` works)
- Docker Desktop running, with the Hermes container (or Compose file) available
- No API key required; Ollama's OpenAI-compatible endpoint is unauthenticated

## Steps

1. On the host, run `ollama list` and copy a real model name (e.g. `llama3.1`, `qwen2.5:14b`). Do not use a placeholder like `my-model`.
2. Edit `config.yaml` on the host so it is bind-mounted into the container (see commands.md for the mount and edit). Set:
   ```yaml
   model:
     provider: custom
     model: <name from `ollama list`>
     base_url: http://host.docker.internal:11434/v1
     api_key: "none"
   ```
   The `http://` scheme and the `/v1` path are both required. If the container currently has config only inside its filesystem, copy it out first (`docker cp`) and re-create the container with a bind mount — otherwise the next `docker compose up -d` or container recreation discards the edit.
3. From inside the Hermes container, test connectivity: `curl -sv http://host.docker.internal:11434/v1/models`. If `curl` is not installed in the container, run the test from a throwaway curl container on the same Docker network instead (see commands.md). Note that `curl -sv` without `-f` exits 0 even on HTTP 404/500 — check the response body for a JSON model list.
4. If the curl fails to connect: Ollama is bound only to localhost. Restart it listening on all interfaces with `OLLAMA_HOST=0.0.0.0:11434 ollama serve` (or set the same variable in the Ollama macOS app settings). **Warning:** this exposes an unauthenticated LLM API on port 11434 to every device on your LAN — only do this on a trusted network, and prefer `127.0.0.1` plus Docker Desktop's host networking if your setup allows it. If you used `launchctl setenv OLLAMA_HOST ...`, note that this persists for all future processes until you run `launchctl unsetenv OLLAMA_HOST`. Retry the curl.
5. For auto-start, let each component start independently — Hermes Desktop cannot launch Docker or Ollama:
   - Docker Desktop: Settings > General > enable "Start Docker Desktop when you sign in".
   - Ollama: keep it enabled under System Settings > General > Login Items.
   - Hermes container: set `restart: unless-stopped` in the Compose service (or `--restart unless-stopped` with `docker run`).
6. For a manual one-line start, from the directory containing the Compose file run `docker compose up -d`.

## Outputs

- Hermes-in-Docker using a host Ollama model via `http://host.docker.internal:11434/v1`
- Verified connectivity: curl of `/v1/models` returns a JSON model list
- Stack auto-starts after login (Docker Desktop + Ollama login items + `restart: unless-stopped`)

## Failure modes

- `base_url` missing the `http://` scheme or the `/v1` path
- Model name is a placeholder instead of one from `ollama list`
- Ollama bound only to 127.0.0.1, so `host.docker.internal` connections are refused
- Config edited inside the container and lost on recreation — persist via bind mount
- `curl` not present in the container — "executable not found" is not a connectivity failure; use the fallback test
- Expecting Hermes Desktop to start Docker or Ollama itself — it does not
- `OLLAMA_HOST=0.0.0.0` exposes the unauthenticated API to the LAN; `launchctl setenv` persists user-wide

## Source

Discord thread `/1485307775444844625/1541086922410303518` ("Ollama locally but Hermes inside docker set up"), 2026-08-24. Advice from HexLab and Gille; confirmed working by OP.