# Commands

Placeholders:
- `<CONTAINER>` — Hermes container name or ID (`docker ps` to find it)
- `<MODEL>` — a real model name from `ollama list`
- `<COMPOSE_DIR>` — directory containing the Compose file
- `<HERMES_NETWORK>` — Docker network the Hermes container is on (`docker inspect <CONTAINER> | grep -A5 NetworkMode` or check the Compose file)
- `<HOST_CONFIG_PATH>` — path to config.yaml on the host, e.g. `~/hermes/config.yaml`
- `<CONTAINER_CONFIG_PATH>` — path config.yaml is mounted at inside the container (per image docs, commonly `/app/config.yaml`)

## Step 1 — list available models on the host

```bash
ollama list
```

## Step 2 — persist and edit config.yaml via bind mount

If config exists only inside the container, copy it out first:

```bash
docker cp <CONTAINER>:<CONTAINER_CONFIG_PATH> <HOST_CONFIG_PATH>
```

Edit `<HOST_CONFIG_PATH>` on the host with any local editor:

```bash
open -e <HOST_CONFIG_PATH>   # or: vim / nano / code
```

Set:
```yaml
model:
  provider: custom
  model: <MODEL>
  base_url: http://host.docker.internal:11434/v1
  api_key: "none"
```

Add the mount to the Compose service (or `-v <HOST_CONFIG_PATH>:<CONTAINER_CONFIG_PATH>` with `docker run`), then re-create:

```bash
cd <COMPOSE_DIR> && docker compose up -d
```

## Step 3 — test connectivity from inside the container

```bash
docker exec <CONTAINER> curl -sv http://host.docker.internal:11434/v1/models
```

Fallback if curl is not installed in the container:

```bash
docker run --rm --network <HERMES_NETWORK> curlimages/curl:latest -sv http://host.docker.internal:11434/v1/models
```

Check the body is a JSON model list; `-sv` alone exits 0 on HTTP errors.

## Step 4 — rebind Ollama if the curl fails to connect

Stop the Ollama app, then from a terminal:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

(Or set the same value in the Ollama macOS app settings.) Retry the Step 3 curl. If you previously used `launchctl setenv OLLAMA_HOST 0.0.0.0:11434`, undo it with:

```bash
launchctl unsetenv OLLAMA_HOST
```

## Step 5 — auto-start configuration

Docker Desktop: Settings > General > "Start Docker Desktop when you sign in" (GUI only).
Ollama: System Settings > General > Login Items (GUI only).
Hermes: add `restart: unless-stopped` to the Compose service, or for docker run:

```bash
docker run -d --restart unless-stopped ... <image>
```

## Step 6 — manual one-line start

```bash
cd <COMPOSE_DIR> && docker compose up -d