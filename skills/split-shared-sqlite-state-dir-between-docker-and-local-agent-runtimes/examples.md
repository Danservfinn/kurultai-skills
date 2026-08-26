# Examples

## Example 1 — Docker + Desktop sharing `~/.hermes` (the canonical case)

**Input:**
- Symptom: "Sessions missing for Default profile in Dashboard and Desktop after Desktop update; `sessions repair --check-only` passes."
- `docker-compose.yml` in `~/my-agent-os` with volumes:
  ```yaml
  volumes:
    - ~/.hermes:/opt/data
    - ./obsidian/vault:/workspace/vault:rw
  ```
- Operator also ran `docker compose run --rm --no-deps -e HERMES_DASHBOARD=0 hermes hermes sessions repair --check-only` while the container was up.

**Execution:**
1. `docker compose exec -T hermes hermes sessions repair --check-only` → passes; no recovery run.
2. `docker compose logs --tail 200 hermes | grep -i "disk I/O error"` → hits on `sqlite3.OperationalError: disk I/O error`.
3. `docker compose config` shows `/Users/mrfretless/.hermes` bound to `/opt/data`; Desktop uses the same dir. Diagnosis confirmed.
4. Close Desktop, verify with `ps ax -o pid,ppid,command | grep -i "[H]ermes.app"` (empty), `docker compose restart hermes` → sessions reappear in Dashboard.
5. `docker compose stop hermes`; `docker compose ps hermes` confirms stopped.
6. `test ! -e "$HOME/.hermes-docker" && mkdir "$HOME/.hermes-docker" && rsync -a "$HOME/.hermes/" "$HOME/.hermes-docker/"` → succeeds; `state.db` (and `-wal`/`-shm` if present) copied.
7. Edit volumes line to `- ${HOME}/.hermes-docker:/opt/data`; `docker compose config`; `docker compose up -d --force-recreate hermes`.
8. `docker inspect` shows `/Users/mrfretless/.hermes-docker -> /opt/data`.
9. `--check-only` passes for default and `-p iris`; Dashboard shows both profiles; Desktop reopened on remote gateway.

**Output:** dedicated dir mounted, container recreated, sessions verified, no hardcoded-path hits in the audit grep.

## Example 2 — destination directory already exists

**Input:** Operator previously attempted the migration and `~/.hermes-docker` exists (possibly partial).

**Execution:** Step 7's `test ! -e "$HOME/.hermes-docker"` fails; `&&` chain short-circuits; nothing is copied or merged.

**Output:** Abort with message: destination exists; escalate — do not merge state directories.

## Example 3 — custom plugin with hardcoded path breaks after split

**Input:** After the split, a Memory plugin fails. Audit grep:
```
grep -rn -E '\.hermes|/Users/' "$HOME/.hermes-docker/skills" "$HOME/.hermes-docker/scripts"
```
finds `memory_plugin.py` containing `/Users/mrfretless/.hermes/memory.json`.

**Execution:** Replace the hardcoded path with `/opt/data/memory.json` (the in-container location; `$HERMES_HOME` only if `docker compose exec -T hermes env | grep HERMES` confirms it is set). Restart the container.

**Output:** Plugin reads its data from the Docker copy; original `~/.hermes` left untouched for Desktop.