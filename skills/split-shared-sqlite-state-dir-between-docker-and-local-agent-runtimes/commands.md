# Commands

Placeholders:
- `<profile>` — Hermes profile name, e.g. `iris`
- `<project-dir>` — directory containing `docker-compose.yml`, e.g. `~/my-agent-os`
- All commands run on the host from `<project-dir>` unless prefixed with `docker compose exec` (runs inside the container)

## Step 1 — verify DB (inside container)
```bash
cd <project-dir>
docker compose exec -T hermes hermes sessions repair --check-only
docker compose exec -T hermes hermes -p <profile> sessions repair --check-only
```

## Step 2 — confirm CLI surface (inside container)
```bash
docker compose exec -T hermes hermes --help
docker compose exec -T hermes hermes sessions --help
```

## Step 3 — local diagnostics (host; optional upload requires consent)
```bash
docker compose logs --tail 200 hermes | grep -i "disk I/O error"
# optional, uploads off-machine — only with operator consent:
docker compose exec -T hermes hermes debug share --nous
```

## Step 4 — inspect volume config (host)
```bash
docker compose config
```

## Step 5 — close Desktop, restart container (host)
```bash
ps ax -o pid,ppid,command | grep -i "[H]ermes.app"
docker compose restart hermes
```

## Step 6 — stop and verify stopped (host)
```bash
docker compose stop hermes
docker compose ps hermes
```

## Step 7 — copy to dedicated dir, verify sidecars (host)
```bash
test ! -e "$HOME/.hermes-docker" && mkdir "$HOME/.hermes-docker" && rsync -a "$HOME/.hermes/" "$HOME/.hermes-docker/"
ls -la "$HOME/.hermes-docker" | grep -E "state.db"
```

## Step 8 — edit compose file (host, manual edit)
```bash
# change:  - ~/.hermes:/opt/data
# to:      - ${HOME}/.hermes-docker:/opt/data
```

## Step 9 — validate and recreate (host)
```bash
docker compose config
docker compose up -d --force-recreate hermes
```

## Step 10 — confirm mount source (host)
```bash
docker inspect "$(docker compose ps -q hermes)" --format '{{range .Mounts}}{{if eq .Destination "/opt/data"}}{{.Source}} -> {{.Destination}}{{end}}{{end}}'
```

## Step 11 — verify sessions (inside container)
```bash
docker compose exec -T hermes hermes sessions repair --check-only
docker compose exec -T hermes hermes -p <profile> sessions repair --check-only
```

## Step 12 — audit hardcoded paths (host)
```bash
grep -rn -E '\.hermes|/Users/' "$HOME/.hermes-docker/skills" "$HOME/.hermes-docker/scripts" 2>/dev/null
docker compose exec -T hermes env | grep HERMES