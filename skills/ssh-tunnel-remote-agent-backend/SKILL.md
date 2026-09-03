---
name: ssh-tunnel-remote-agent-backend
description: >
  Securely access a remote AI agent's loopback-only API (default 127.0.0.1:8642)
  and its home-directory data (sessions, skills, memory, config, logs) from a
  local machine via an SSH tunnel. Use when a self-hosted agent runs on a VPS,
  VM, or LAN box and you need full management-screen parity — not just chat —
  without exposing the API publicly. Triggers: remote backend setup, "connect
  desktop app to remote agent", tunnel to 127.0.0.1 service, remote ~/.hermes
  data access, containerized agent with empty management screens.
category: infrastructure
---
```

# SSH Tunnel to a Remote Agent Backend

## Goal

Forward a local port to a remote agent's loopback API over SSH, and proxy file-based management data (sessions, skills, memory, config) via SSH commands — so every management screen works as if the agent were local, without exposing the API to the public internet.

## Inputs

- `REMOTE_USER` — SSH username on the remote host; **must be the same user that runs the agent** (e.g. `hermes`), so `~` resolves to the real data directory.
- `REMOTE_HOST` — remote host address (VPS, VM, LAN box).
- `REMOTE_SSH_PORT` — SSH port (default 22).
- `LOCAL_PORT` — free local TCP port for the tunnel (e.g. 18642).
- `AGENT_PORT` — port the agent listens on, loopback only (default 8642).
- Local SSH key pair at `~/.ssh/id_ed25519` (generated in step 1 if missing).
- No external API keys required for the tunnel itself; the agent's own API key may be needed for authenticated endpoints (see Failure modes).

## Steps

1. Generate an SSH key locally if `~/.ssh/id_ed25519` does not exist: `ssh-keygen -t ed25519`.
2. Ensure the remote agent runs as a dedicated user with a real shell (`sudo chsh -s /bin/bash <REMOTE_USER>` if it is `/usr/sbin/nologin`). Create `~/.ssh` (mode 700) and append the local public key to `~/.ssh/authorized_keys` (mode 600, owned by the agent user) using `ssh-copy-id` or a piped append.
3. Verify non-interactive SSH exactly as clients will call it: `ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519 -p <REMOTE_SSH_PORT> <REMOTE_USER>@<REMOTE_HOST> 'curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:<AGENT_PORT>/health'` — expect 200. "Permission denied" means the key is not authorized; a passphrase prompt means BatchMode will fail closed.
4. Establish the tunnel: `ssh -N -L <LOCAL_PORT>:127.0.0.1:<AGENT_PORT> -i ~/.ssh/id_ed25519 -o BatchMode=yes -o StrictHostKeyChecking=accept-new -p <REMOTE_SSH_PORT> <REMOTE_USER>@<REMOTE_HOST>` (run in background or a second terminal).
5. Point local clients at `http://127.0.0.1:<LOCAL_PORT>`. Access file-based data (sessions, skills, memory, config, logs) by running remote read/write commands through `ssh <REMOTE_USER>@<REMOTE_HOST> ...` (sshExec-style proxying) — never by reading a local home directory.
6. If the agent runs in a Docker container with a host-mounted data volume: on the SSH host, (a) create a launcher script `~/.config/<app>/remote-<agent>` that invokes the agent CLI via `docker exec`, and (b) create a symlink `~/.hermes` → the container's host data volume. Refuse to overwrite an existing real directory at `~/.hermes`.
7. Health-check the service through the tunnel (`curl http://127.0.0.1:<LOCAL_PORT>/health`), then tear down the tunnel when finished.

## Outputs

- Working SSH tunnel forwarding `localhost:<LOCAL_PORT>` to the remote agent's loopback API.
- Remote CLI/SSH proxy access to the agent's home-directory data.
- Health check confirmation (HTTP 200).

## Failure modes

- **Wrong user**: SSH'ing as a user other than the agent's runtime user makes `~` point at an empty directory; management screens look empty. Fix: re-key for the correct user.
- **Nologin shell or bad perms**: agent user set to `/usr/sbin/nologin`, or `.ssh`/`authorized_keys` with wrong mode/ownership, blocks key auth.
- **Passphrase-protected key with no agent loaded**: `BatchMode=yes` fails with no useful error. Fix: use a passphrase-free key or load `ssh-agent`.
- **Containerized agent, no host-side data dir**: chat works over the tunnel but sessions/logs/memory appear empty. Fix: step 6 launcher + symlink to the host volume.
- **Auth-gated endpoints**: dashboard/WebSocket endpoints may require a separate session token distinct from the API server key; a 200 on `/health` does not guarantee those work.
- **Service name drift**: if `/health` or port 8642 does not match this deployment, probe with `curl -sS http://127.0.0.1:<AGENT_PORT>/` and `ss -tlnp | grep <AGENT_PORT>` on the host to find the real port/endpoint before assuming failure.

## Source

- https://github.com/fathah/hermes-desktop — `docs/SSH-TUNNEL-VPS.md` (tunnel flags, BatchMode verification command, systemd-user setup, Docker launcher + symlink conventions). Retrieved 2026-09-03.