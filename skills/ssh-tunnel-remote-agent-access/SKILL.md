---
name: ssh-tunnel-remote-agent-access
description: Connect a local client to a remote Hermes agent/API server over an SSH tunnel so all management features (sessions, skills, memory, logs) work as if the agent were local
category: infrastructure
---

# SSH Tunnel Remote Agent Access

## Goal

Establish an SSH tunnel from a local port to a remote Hermes agent API listening on `127.0.0.1:<agentPort>` (default 8642), and verify that chat plus management endpoints (sessions, skills, memory, logs) return real remote data — not just a health check.

## Inputs

- SSH key pair path on the local machine (default `~/.ssh/id_ed25519`); generated in Step 1 if absent
- Remote host address and SSH user (must be the same user that runs the agent, so `~` resolves to the real `~/.hermes` data directory)
- Remote agent API port (default 8642)
- Local port for the tunnel (default 8642; pick another if occupied)
- If the agent runs in Docker on the remote host: container name and data volume path

## Steps

1. Generate an SSH key pair on the local machine if it does not already exist: `ssh-keygen -t ed25519`. Do not set a passphrase — `BatchMode=yes` in later steps fails closed on passphrase-protected keys.
2. On the remote host, ensure the SSH user is the same user that runs the agent. If it is a service user with a nologin shell, run `sudo chsh -s /bin/bash <user>` on the remote host.
3. Authorize the desktop's public key on the remote host. Create `~/.ssh` with mode 700 and `~/.ssh/authorized_keys` with mode 600, both owned by the target user, then append the local public key (`<keyPath>.pub`) — transfer it over the existing SSH session with `ssh` + `cat >>`, or use `ssh-copy-id`.
4. Verify non-interactive SSH works exactly as the client will call it: `ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i <keyPath> -p 22 <user>@<host> 'curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:<agentPort>/health'` — expect `200`.
5. Establish the tunnel: `ssh -N -L <localPort>:127.0.0.1:<agentPort> -i <keyPath> -o BatchMode=yes -o StrictHostKeyChecking=accept-new <user>@<host>` (run in a background terminal or under `nohup`).
6. Point the client at `http://127.0.0.1:<localPort>`. Verify chat works AND verify each management endpoint returns real data, not just HTTP 200: fetch `/sessions`, `/skills`, `/memory`, and `/logs` through the tunnel and confirm the responses are non-empty and contain remote data (e.g., session IDs from the remote `~/.hermes/state.db`). A 200 with an empty body or a 404 means the tunnel is up but management access is broken — usually the wrong SSH user or a Docker deployment without the Step 7 setup.
7. If the agent runs in Docker on the remote host, the host has no `~/.hermes`, so management screens will be empty even though chat works. Write a launcher script on the remote host that runs the CLI via `docker exec`, and symlink `~/.hermes` to the container's data volume. Refuse to overwrite an existing launcher or an existing real `~/.hermes`. Run the guard checks inside a subshell or script so a triggered guard aborts the setup block, not the user's SSH session.

## Outputs

- Working SSH tunnel from local port `<localPort>` to remote agent API on `127.0.0.1:<agentPort>`
- Verified `/health` returning 200 through the tunnel
- Verified non-empty responses from `/sessions`, `/skills`, `/memory`, `/logs` containing remote data
- Full remote management access via SSH exec against remote `~/.hermes`

## Failure modes

- SSH key has a passphrase and no agent is loaded — `BatchMode=yes` fails closed with no useful error. Use a passphrase-less key or load ssh-agent first.
- Logging in as the wrong user so `~` points at an empty directory — chat works but sessions/logs appear empty. Management endpoint verification in Step 6 catches this.
- Wrong permissions on `~/.ssh/authorized_keys` (not 700/600 or wrong owner) causing `Permission denied`. Use the portable permission check in commands.md Step 3 (works on GNU and BSD/macOS `stat`).
- Docker deployments where the host has no `~/.hermes` — chat works but sessions/logs are empty until the launcher and symlink from Step 7 are set up.
- Remote agent API not listening on `127.0.0.1` (e.g., bound only inside the container network) — health check fails; confirm with `curl` on the remote host first.
- No API key or service required beyond SSH access itself; if the remote host requires 2FA or password auth only, `BatchMode=yes` cannot work.

## Source

- https://github.com/fathah/hermes-desktop — `docs/SSH-TUNNEL-VPS.md` (tunnel flags, `chsh`, authorized_keys 700/600 setup, health-check verification command, Docker Case D launcher/symlink with no-overwrite guards)