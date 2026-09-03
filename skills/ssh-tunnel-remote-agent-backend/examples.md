# Examples

## Example 1 — Dedicated user `hermes` on a VPS (systemd service)

Inputs: `REMOTE_USER=hermes`, `REMOTE_HOST=203.0.113.10`, `REMOTE_SSH_PORT=22`, `AGENT_PORT=8642`, `LOCAL_PORT=18642`.

1. Local key exists (`ls ~/.ssh/id_ed25519` succeeds); skip generation.
2. Agent runs as `hermes`; shell is already `/bin/bash`. Install the key:
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519.pub -p 22 hermes@203.0.113.10
   ```
   On the host, verify: `sudo ls -la /home/hermes/.ssh` shows `authorized_keys` mode 600 owned by `hermes`, `.ssh` mode 700.
3. Verify non-interactive health check:
   ```bash
   ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519 -p 22 hermes@203.0.113.10 \
     'curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8642/health'
   ```
   Output: `200`.
4. Open the tunnel in the background:
   ```bash
   ssh -N -L 18642:127.0.0.1:8642 -i ~/.ssh/id_ed25519 -o BatchMode=yes \
     -o StrictHostKeyChecking=accept-new -p 22 hermes@203.0.113.10 &
   ```
5. Local client base URL: `http://127.0.0.1:18642`. List remote sessions:
   ```bash
   ssh -o BatchMode=yes -i ~/.ssh/id_ed25519 -p 22 hermes@203.0.113.10 'ls ~/.hermes/profiles'
   ```
7. `curl http://127.0.0.1:18642/health` → 200; then `kill %1` to tear down.

## Example 2 — Non-standard SSH port and wrong-user failure

Inputs: `REMOTE_USER=deploy` (first attempt), agent actually runs as `hermes`; `REMOTE_HOST=pi.lan`, `REMOTE_SSH_PORT=2222`, `AGENT_PORT=8642`, `LOCAL_PORT=18642`.

1. Generate a key: `ssh-keygen -t ed25519` (accept defaults, empty passphrase).
2. Key install succeeds for `deploy`. Health check passes (`200`), but `ssh -p 2222 deploy@pi.lan 'ls ~/.hermes'` returns empty — the agent's data lives under `/home/hermes`. This is the wrong-user failure mode: management screens would look empty.
3. Fix: authorize the key for the correct user, then re-verify with the same command as `hermes@pi.lan` — `ls ~/.hermes` now lists `config.yaml`, `profiles/`, `state.db`.
4. Tunnel: `ssh -N -L 18642:127.0.0.1:8642 -i ~/.ssh/id_ed25519 -o BatchMode=yes -o StrictHostKeyChecking=accept-new -p 2222 hermes@pi.lan`.

## Example 3 — Containerized agent with host volume

Inputs: `REMOTE_USER=hermes`, `REMOTE_HOST=198.51.100.7`, `REMOTE_SSH_PORT=22`, agent runs in Docker with data volume mounted at `/srv/hermes-data` on the host.

1–4. Key install, verification, and tunnel as in Example 1. Chat works, but `ssh hermes@198.51.100.7 'ls ~/.hermes'` is empty — containerized-data failure mode.
5. On the SSH host, create the launcher and symlink:
   ```bash
   mkdir -p ~/.config/hermes-desktop
   printf '#!/bin/sh\nexec docker exec -i hermes hermes "$@"\n' > ~/.config/hermes-desktop/remote-hermes
   chmod +x ~/.config/hermes-desktop/remote-hermes
   [ -d ~/.hermes ] && [ ! -L ~/.hermes ] || ln -s /srv/hermes-data ~/.hermes
   ```
   The guard refuses to clobber a real `~/.hermes` directory.
6. Management data access now works: `ssh hermes@198.51.100.7 'ls ~/.hermes/profiles'` lists profiles from the container's volume.