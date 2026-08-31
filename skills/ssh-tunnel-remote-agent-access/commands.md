# Commands

Placeholders: `<keyPath>` (local SSH key, default `~/.ssh/id_ed25519`), `<host>`, `<user>`, `<agentPort>` (remote API port, default 8642), `<localPort>` (default 8642), `<dockerContainer>`, `<dockerVolumePath>`. `<keyPath>.pub` is the public half of the same key pair, created in Step 1.

## Step 1 — Generate key pair if absent

```bash
[ -f <keyPath> ] || ssh-keygen -t ed25519 -f <keyPath> -N ""
```

## Step 2 — Fix nologin shell on remote host (run on remote host)

```bash
sudo chsh -s /bin/bash <user>
```

## Step 3 — Authorize the desktop's public key (run from local machine)

Transfer `<keyPath>.pub` and append it, setting permissions. The permission check uses `find`/`ls`, portable across GNU and BSD/macOS remotes:

```bash
ssh <user>@<host> 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
cat <keyPath>.pub | ssh <user>@<host> 'cat >> ~/.ssh/authorized_keys'
# verify ownership and modes (portable):
ssh <user>@<host> 'ls -ld ~/.ssh ~/.ssh/authorized_keys'
# expect: drwx------ for ~/.ssh, -rw------- for authorized_keys, both owned by <user>
```

Alternative one-liner:

```bash
ssh-copy-id -i <keyPath>.pub <user>@<host>
```

## Step 4 — Verify non-interactive SSH + health check

```bash
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i <keyPath> -p 22 <user>@<host> \
  'curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:<agentPort>/health'
# expect: 200
```

## Step 5 — Establish the tunnel (background)

```bash
nohup ssh -N -L <localPort>:127.0.0.1:<agentPort> -i <keyPath> \
  -o BatchMode=yes -o StrictHostKeyChecking=accept-new <user>@<host> \
  >/tmp/hermes-tunnel.log 2>&1 &
```

## Step 6 — Verify health AND management endpoints return real data

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:<localPort>/health
# expect: 200

for ep in sessions skills memory logs; do
  code=$(curl -s -o /tmp/hermes-$ep.json -w "%{http_code}" http://127.0.0.1:<localPort>/$ep)
  size=$(wc -c < /tmp/hermes-$ep.json | tr -d ' ')
  echo "$ep: HTTP $code, $size bytes"
  # FAIL if code is not 200 or body is empty ({} / [] / "") — that means
  # wrong SSH user or Docker deployment needing Step 7
done
```

## Step 7 — Docker launcher + symlink (run on remote host, wrapped in a subshell so guards abort the block, not your SSH session)

Paste as one block, or save to a script and run it:

```bash
ssh <user>@<host> 'bash -s' <<'EOF'
set -e
if [ -e "$HOME/bin/remote-hermes" ]; then
  echo "refusing: ~/bin/remote-hermes already exists" >&2; exit 1
fi
if [ -e "$HOME/.hermes" ] && [ ! -L "$HOME/.hermes" ]; then
  echo "refusing: real ~/.hermes exists" >&2; exit 1
fi
mkdir -p "$HOME/bin"
cat > "$HOME/bin/remote-hermes" <<LAUNCHER
#!/bin/bash
exec docker exec <dockerContainer> hermes "\$@"
LAUNCHER
chmod +x "$HOME/bin/remote-hermes"
ln -s <dockerVolumePath> "$HOME/.hermes"
echo "done"
EOF