# Examples

## Example 1: Bare-metal VPS, default port

```
skill: ssh-tunnel-remote-agent-access
inputs:
  keyPath: ~/.ssh/id_ed25519
  host: vps.example.com
  user: hermes
  agentPort: 8642
  localPort: 8642
```

Run: Steps 1–6. The `hermes` user runs the agent directly, `~/.hermes` exists on the host, so Step 7 is skipped. Expected result: `/health` returns 200 through the tunnel and `/sessions` returns JSON containing session IDs from the remote `state.db`.

## Example 2: Service user with nologin shell

```
skill: ssh-tunnel-remote-agent-access
inputs:
  keyPath: ~/.ssh/hermes_vps
  host: 203.0.113.10
  user: hermes
  agentPort: 8642
  localPort: 18642
```

The `hermes` account was created with `/usr/sbin/nologin`. Run Step 2 first (`sudo chsh -s /bin/bash hermes` on the remote host), then Steps 3–6. Use `localPort: 18642` because 8642 is occupied locally by a local Hermes install.

## Example 3: Agent in Docker on the remote host

```
skill: ssh-tunnel-remote-agent-access
inputs:
  keyPath: ~/.ssh/id_ed25519
  host: pi.lan
  user: pi
  agentPort: 8642
  localPort: 8642
  dockerContainer: hermes-agent
  dockerVolumePath: /var/lib/docker/volumes/hermes_data/_data
```

Chat works after Step 5, but Step 6 shows `/sessions` and `/logs` empty (404 or `[]` with no remote session IDs). Run Step 7: write `~/bin/remote-hermes` that wraps `docker exec hermes-agent hermes "$@"`, and symlink `~/.hermes` → the data volume. Guards refuse to run if `~/bin/remote-hermes` or a real `~/.hermes` directory already exists. Re-run Step 6; sessions now return remote data.