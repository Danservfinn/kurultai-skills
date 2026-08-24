# Examples

## Example 1 — MacBook Pro M4, MLX backend, Compose

**Input:** Hermes runs via `docker compose` in `~/hermes`; Ollama (macOS app, MLX) runs on the host. OP's broken config:

```yaml
model:
  provider: custom
  model: my-model
  base_url: host.docker.internal:11434
  api_key: "none"
```

**Actions:**
1. `ollama list` shows `qwen2.5:14b`.
2. Bind-mount the config: add `- ./config.yaml:/app/config.yaml` (or the Compose `volumes:` equivalent) and edit on the host:
   ```yaml
   model:
     provider: custom
     model: qwen2.5:14b
     base_url: http://host.docker.internal:11434/v1
     api_key: "none"
   ```
3. `docker compose up -d` to re-create with the mount, then `docker exec <container> curl -sv http://host.docker.internal:11434/v1/models` — JSON model list returned.
4. Add `restart: unless-stopped` to the Compose service.

**Result:** Hermes in Docker answers using the host's MLX-backed model; stack restores after reboot.

## Example 2 — curl missing in the container

**Input:** Same setup, but `docker exec <container> curl ...` fails with `executable file not found`.

**Action:** Do not treat this as a connectivity failure. Test from a throwaway container on the same network:

```bash
docker run --rm --network <hermes-network> curlimages/curl:latest -sv http://host.docker.internal:11434/v1/models
```

Confirm the response body is a JSON `{"data": [...]}` model list, not just exit code 0.

## Example 3 — connection refused, Ollama on localhost only

**Input:** curl to `host.docker.internal:11434` times out / connection refused.

**Actions:**
1. Stop the Ollama app, restart from a terminal with `OLLAMA_HOST=0.0.0.0:11434 ollama serve`.
2. Retry the curl — now returns the model list.
3. Note the LAN exposure; on an untrusted network, revert and investigate Docker Desktop host networking instead. If `launchctl setenv OLLAMA_HOST 0.0.0.0:11434` was used earlier, undo with `launchctl unsetenv OLLAMA_HOST`.