# Examples

## Example 1 — Hermes session-scoped sandbox path (the original report)

Input (Kurultai task):

```
Failing command (stderr captured):
docker run --rm -v /srv/hermes-workspace/sandboxes/docker/session:a1b2c3/home:/root \
  -v /srv/hermes-workspace/sandboxes/docker/session:a1b2c3/workspace:/workspace \
  hermes-sandbox:0.20.5 sleep 30
stderr: docker: Error response from daemon: invalid mode: /root.
```

Diagnosis walk:

1. `docker version`, `docker info`, `docker image inspect hermes-sandbox:0.20.5` all succeed; `hermes doctor` passes.
2. stderr already shows the signature: `invalid mode: /root`.
3. Repo search finds `-v` emission in `tools/environments/docker.py` and the `session:` prefix in `tools/terminal_tool.py`.
4. Minimal repro: `mkdir -p "/tmp/session:t1"` then `docker run --rm -v "/tmp/session:t1":/root hermes-sandbox:0.20.5 true` → exit 125; colon-free path → exit 0.
5. Fix: switch generated mounts to `--mount type=bind,source=...,target=...` (option b), keeping the logical `session:<id>` stored separately.
6. Regression test asserts container creation succeeds with identifier `session:t1`.

Output: patched `docker.py`, regression test, diagnosis note citing the stderr evidence.

## Example 2 — Generic agent framework with `task:<uuid>` workspace paths

Input:

```
Our runner builds: -v /var/lib/runner/tasks/task:9f81-.../ws:/workspace
docker run exits 125. journalctl -u docker shows nothing useful.
```

Diagnosis walk:

1. Infrastructure checks pass; image present.
2. `journalctl` is a dead end as expected — rerun the failing command with `2>err.log` and find `Error response from daemon: invalid mode: /workspace` in `err.log`.
3. `grep -rn -- '-v' <repo>` locates the mount builder; `grep -rn 'task:' <repo>` locates the identifier.
4. Repro confirms colon path fails, colon-free succeeds.
5. Fix chosen: slugify the identifier for directory names (`task-9f81-...`) while keeping `task:9f81-...` as the logical key.
6. Regression test runs the mount builder with `task:9f81-...` and asserts the host path contains no colon.

## Example 3 — Mistaken diagnosis: exit 125 from a name conflict

Input:

```
docker run exits 125, we think it's the colon thing. Error: "Conflict. The container name /foo is already in use".
```

Diagnosis walk:

1. Capture stderr: no `invalid mode` signature — the error is a name conflict.
2. Stop: this is a different exit-125 cause. Remove the stale container or use `--rm`/unique names; do not patch mount code.
3. If colon paths are also suspected, run the minimal repro separately before changing code.

Output: diagnosis "not the colon issue", no patch applied.