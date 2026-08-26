---
name: split-shared-sqlite-state-dir-between-docker-and-local-agent-runtimes
description: Diagnose and fix 'disk I/O error' / missing sessions caused by a Docker Hermes container and the local Desktop app sharing one SQLite state directory, by giving Docker a dedicated data directory without data loss
category: ops-automation
---
```

# Split a shared SQLite state directory between Docker and local Hermes runtimes

## Goal

Two Hermes runtimes (a Docker container and the Desktop app's local backend) must not share the same SQLite state directory. When they do, the running Dashboard process fails with `sqlite3.OperationalError: disk I/O error` and sessions disappear, even though offline `sessions repair --check-only` passes. This skill confirms the diagnosis, restores access, and permanently splits the Docker container onto a dedicated host data directory (`~/.hermes-docker`) without losing data or deleting the local Desktop installation.

## Inputs

- `docker-compose.yml` with a `volumes:` section for the `hermes` service, located in a known project directory (e.g. `~/my-agent-os`)
- Host shell access (macOS) to the machine running both Docker and the Desktop app
- Symptom report: sessions missing in Dashboard/Desktop while `hermes sessions repair --check-only` passes
- Docker CLI with `docker compose` v2 available on the host

## Steps

1. **Verify the database is intact.** From the directory containing `docker-compose.yml`, run `docker compose exec -T hermes hermes sessions repair --check-only` against the running container. For additional profiles, run `docker compose exec -T hermes hermes -p <profile> sessions repair --check-only` (the `-p` flag goes between `hermes` and the subcommand). If the check passes, the DB file is fine and the problem is runtime access — do NOT run recovery or repair-with-write. If `exec` fails because the container is not running, note that and continue; the diagnosis in step 2 still applies.

2. **Confirm the CLI surface before trusting it.** The subcommands `hermes sessions repair --check-only` and `hermes debug share` come from a support thread, not official docs. Before relying on either, run `docker compose exec -T hermes hermes --help` and `docker compose exec -T hermes hermes sessions --help` and confirm the subcommands and flags exist in your image version. If a subcommand is absent, skip that step and rely on log inspection instead (step 3).

3. **Collect diagnostics — with consent for any upload.** Look for `sqlite3.OperationalError: disk I/O error` in container logs: `docker compose logs --tail 200 hermes | grep -i "disk I/O error"`. This is local-only and preferred. Optionally, `hermes debug share --nous` (run inside the container: `docker compose exec -T hermes hermes debug share --nous`) produces a debug bundle and uploads it to Nous Research's support service — it can contain logs, file paths, and possibly session content, and it leaves your machine. Only run it if the operator explicitly consents to that upload; the local log grep is sufficient for diagnosis.

4. **Identify concurrent runtimes sharing the state dir.** Run `docker compose config` and inspect the `hermes` service volumes. A mount like `~/.hermes:/opt/data` (rendered by `config` as an expanded absolute host path such as `/Users/<name>/.hermes:/opt/data`) that is also the local Desktop backend's home directory is the root cause. Also check shell history / recent commands for `docker compose run` invocations — each one starts a second Hermes service tree against the same SQLite directory while the normal container runs.

5. **Restore access temporarily.** Close all Desktop app windows and verify no local backend is running: `ps ax -o pid,ppid,command | grep -i "[H]ermes.app"` (empty output = closed). Then `docker compose restart hermes` and confirm sessions reappear in Dashboard before reopening Desktop. Do not run `docker compose run` repair/check commands while the normal container is up.

6. **Stop the container and verify it stopped.** Run `docker compose stop hermes`, then `docker compose ps hermes` and confirm status is not `running` (or the service is absent). A still-running writer during the copy in step 7 can produce a torn SQLite copy (stale WAL/SHM sidecars) that still passes `--check-only`.

7. **Copy the data to a dedicated directory, refusing to merge.** Run `test ! -e "$HOME/.hermes-docker" && mkdir "$HOME/.hermes-docker" && rsync -a "$HOME/.hermes/" "$HOME/.hermes-docker/"`. If `$HOME/.hermes-docker` already exists, the `test` fails and nothing is copied — abort and escalate; merging two state directories can corrupt state. `rsync -a` copies `state.db` plus any `state.db-wal` / `state.db-shm` sidecar files; do not exclude them. After the copy, verify sidecars (if present in the source) exist in the destination: `ls -la "$HOME/.hermes-docker" | grep -E "state.db"`.

8. **Edit docker-compose.yml.** In the `hermes` service `volumes:` section, change only the data mount from `- ~/.hermes:/opt/data` to `- ${HOME}/.hermes-docker:/opt/data`. Leave workspace mounts (`/workspace/...`) and any `:ro` mounts unchanged.

9. **Validate and recreate.** Run `docker compose config` (confirm the `/opt/data` source now resolves to the `.hermes-docker` path) then `docker compose up -d --force-recreate hermes`.

10. **Confirm the mount source.** Run `docker inspect "$(docker compose ps -q hermes)" --format '{{range .Mounts}}{{if eq .Destination "/opt/data"}}{{.Source}} -> {{.Destination}}{{end}}{{end}}'`. Output must show the dedicated directory (e.g. `/Users/<name>/.hermes-docker -> /opt/data`).

11. **Verify sessions.** Re-run `docker compose exec -T hermes hermes sessions repair --check-only` and `docker compose exec -T hermes hermes -p <profile> sessions repair --check-only` for each profile. Check both profiles in Dashboard. Only after Dashboard is correct, reopen Desktop connected to the Docker remote gateway.

12. **Audit custom skills/plugins/scripts for hardcoded host paths.** Search the Docker copy for references to the old host path: `grep -rn -E '\.hermes|/Users/' "$HOME/.hermes-docker/skills" "$HOME/.hermes-docker/scripts" 2>/dev/null` (adjust subdirectories to what exists). Replace hardcoded `~/.hermes` or `/Users/.../.hermes` paths with `$HERMES_HOME`, `/opt/data`, or the applicable `/workspace` path — but only if your image documents `$HERMES_HOME` (check `docker compose exec -T hermes env | grep HERMES`); otherwise use `/opt/data` literally. Keep the original `~/.hermes` directory intact — it is the local Desktop installation and its recovery data.

## Outputs

- Dedicated Docker data directory (`~/.hermes-docker`) mounted at `/opt/data`
- Recreated `hermes` container with isolated SQLite state, verified via `docker inspect`
- Verified session visibility for all profiles in Dashboard and Desktop
- List of custom files containing hardcoded host paths needing updates

## Failure modes

- `$HOME/.hermes-docker` already exists — the copy aborts; do not merge, escalate to the operator
- Running `docker compose run` repair/check commands while the normal container is up starts a second runtime on the same SQLite dir and causes disk I/O errors
- Desktop app auto-restarts a local backend against the shared directory during migration — re-check `ps ax ... | grep "[H]ermes.app"` before and after the copy
- Copying while the container is still running produces a torn copy (WAL/SHM mismatch) — always verify `docker compose ps hermes` shows stopped before `rsync`
- Custom plugins/scripts with hardcoded host paths break after the split
- Deleting the original `~/.hermes` removes the local Desktop installation and its recovery data — never delete it
- `hermes debug share --nous` uploads diagnostics off-machine — requires explicit operator consent; prefer local `docker compose logs` grep
- Subcommands like `sessions repair --check-only` may differ across image versions — verify with `hermes --help` first; if absent, fall back to log inspection

## Source

Discord thread /1485307775444844625/1541579913256108172 (2026-08-26), support guidance from Gille; attachments `update-check-hermes-output.txt`, `sessions-output_copy.txt`. CLI subcommands are as quoted in that thread and should be verified against the installed image with `hermes --help`.