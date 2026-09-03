# Commands

Placeholders (substitute before running):

- `REMOTE_USER` — SSH username running the agent (e.g. `hermes`)
- `REMOTE_HOST` — host address (e.g. `203.0.113.10`)
- `REMOTE_SSH_PORT` — SSH port (e.g. `22`)
- `LOCAL_PORT` — local tunnel port (e.g. `18642`)
- `AGENT_PORT` — remote agent loopback port (e.g. `8642`)

## Step 1 — generate key if missing

```bash
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
```

## Step 2 — prepare agent user and install key

```bash
# On the remote host (via any working login):
sudo chsh -s /bin/bash REMOTE_USER
sudo -u REMOTE_USER mkdir -p ~REMOTE_USER/.ssh
sudo -u REMOTE_USER chmod 700 ~REMOTE_USER/.ssh
```

```bash
# From the local machine — installs the public key into ~REMOTE_USER/.ssh/authorized_keys:
ssh-copy-id -i ~/.ssh/id_ed25519.pub -p REMOTE_SSH_PORT REMOTE_USER@REMOTE_HOST
# Fallback if ssh-copy-id is unavailable:
cat ~/.ssh/id_ed25519.pub | ssh -p REMOTE_SSH_PORT REMOTE_USER@REMOTE_HOST \
  'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

```bash
# Verify permissions on the remote host:
ssh -p REMOTE_SSH_PORT REMOTE_USER@REMOTE_HOST 'ls -ld ~/.ssh ~/.ssh/authorized_keys'
```

## Step 3 — non-interactive verification

```bash
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519 \
  -p REMOTE_SSH_PORT REMOTE_USER@REMOTE_HOST \
  'curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:AGENT_PORT/health'
```

```bash
# Fallback if /health does not exist on this deployment — find the real listener:
ssh -p REMOTE_SSH_PORT REMOTE_USER@REMOTE_HOST 'ss -tlnp | grep AGENT_PORT; curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:AGENT_PORT/'
```

## Step 4 — establish tunnel

```bash
ssh -N -L LOCAL_PORT:127.0.0.1:AGENT_PORT -i ~/.ssh/id_ed25519 \
  -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
  -p REMOTE_SSH_PORT REMOTE_USER@REMOTE_HOST &
```

## Step 5 — use tunnel and proxy file data

```bash
curl http://127.0.0.1:LOCAL_PORT/health
ssh -o BatchMode=yes -i ~/.ssh/id_ed25519 -p REMOTE_SSH_PORT REMOTE_USER@REMOTE_HOST \
  'ls ~/.hermes; cat ~/.hermes/config.yaml'
```

## Step 6 — Docker launcher and data symlink (on the SSH host)

```bash
mkdir -p ~/.config/hermes-desktop
printf '#!/bin/sh\nexec docker exec -i hermes hermes "$@"\n' > ~/.config/hermes-desktop/remote-hermes
chmod +x ~/.config/hermes-desktop/remote-hermes
if [ -e ~/.hermes ] && [ ! -L ~/.hermes ]; then echo "REFUSING: ~/.hermes is a real directory"; else ln -sfn /srv/hermes-data ~/.hermes; fi
```

## Step 7 — health check and teardown

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:LOCAL_PORT/health
pkill -f "ssh -N -L LOCAL_PORT:127.0.0.1:AGENT_PORT"