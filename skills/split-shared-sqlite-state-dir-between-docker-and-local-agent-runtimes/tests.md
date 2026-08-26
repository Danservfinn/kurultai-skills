# Tests — manual checklist

Run from the directory containing `docker-compose.yml` after completing the skill.

1. **Mount isolation.** `docker inspect "$(docker compose ps -q hermes)" --format '{{range .Mounts}}{{if eq .Destination "/opt/data"}}{{.Source}}{{end}}{{end}}'` prints a host path ending in `.hermes-docker`, and does NOT print a path ending in `/.hermes` (compare with `echo $HOME/.hermes` to confirm they differ).

2. **Compose config resolves the new source.** `docker compose config` output, in the hermes service's volumes list, contains a source/target pair where target is `/opt/data` and source contains `.hermes-docker`. (Note: `config` renders long-form syntax with expanded absolute paths — do not grep for the literal string `~/.hermes:/opt/data`.)

3. **Original directory preserved.** `test -d "$HOME/.hermes" && echo intact` prints `intact`, and `ls "$HOME/.hermes"` still shows the local installation contents (e.g. `state.db`, `skills/`).

4. **Copy completeness.** `ls "$HOME/.hermes-docker" | grep -c state.db` is ≥ 1, and for every `state.db-wal` / `state.db-shm` present in `$HOME/.hermes`, the same-named file exists in `$HOME/.hermes-docker` (check with `ls "$HOME/.hermes" | grep state.db` vs `ls "$HOME/.hermes-docker" | grep state.db`).

5. **No second runtime during checks.** `docker compose ps` shows exactly one running container whose name/compose service is `hermes` (no `hermes-run-*` containers from `docker compose run`).

6. **Session check exits successfully.** `docker compose exec -T hermes hermes sessions repair --check-only` exits with status 0 (verify with `echo $?` immediately after). Do not assert on the exact output string — wording varies by image version; the exit status plus visible sessions in Dashboard is the verification.