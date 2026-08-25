# Commands

Placeholders:

- `<image>` — container image used by the failing command (e.g. `hermes-sandbox:0.20.5`)
- `<repo>` — path to the repository that constructs the docker run command (do NOT assume `tools/`; discover with the greps below)
- `<host-workspace>` — root directory of host-side sandbox paths
- `<session-id>` — example session identifier (use `t1` in tests)
- `<health-cmd>` — the application's health-check command, if it exists (e.g. `hermes doctor` for Hermes; skip if the app has none)

## Step 1 — rule out infrastructure

```bash
docker version
docker info
docker image inspect <image> >/dev/null && echo "image present"
# only if the application provides a health check:
<health-cmd>
```

## Step 2 — capture the signature error from the failing command's stderr

```bash
# rerun the failing docker run, capturing stderr; the signature is
# "Error response from daemon: invalid mode: <path>"
<the-failing-docker-run-command> 2>err.log; echo "exit=$?"
grep -i "invalid mode" err.log || echo "signature not found — investigate other exit-125 causes"
# journald usually does NOT contain this error; check only as a fallback:
journalctl -u docker --since "1 hour ago" | grep -i "invalid mode" || true
```

## Step 3 — locate mount construction (repo-agnostic)

```bash
# find where -v / --volume args are generated; run from the repo root
grep -rn -- '-v' <repo> --include='*.py' | grep -iv test
grep -rnE -- '--volume|--mount|volume=' <repo> --include='*.py'
# find the identifier scheme used in host paths (adjust the prefix to what step 2/your config shows)
grep -rn 'session:' <repo> --include='*.py'
grep -rn 'sandboxes' <repo> --include='*.py'
```

## Step 4 — minimal reproduction

```bash
mkdir -p "/tmp/session:t1" "/tmp/session-t1"
docker run --rm -v "/tmp/session:t1":/root <image> true; echo "colon exit=$?"
docker run --rm -v "/tmp/session-t1":/root <image> true; echo "colon-free exit=$?"
# expected: colon exit=125 with "invalid mode: /root"; colon-free exit=0
```

## Step 5 — verify the fix

```bash
# option (b): --mount handles colons, but does NOT auto-create the source — mkdir first
mkdir -p "/tmp/session:t1"
docker run --rm --mount type=bind,source="/tmp/session:t1",target=/root <image> true; echo "mount exit=$?"
# expected: exit=0
# option (a): slugified path
docker run --rm -v "/tmp/session-t1":/root <image> true; echo "slug exit=$?"
```

## Step 6 — regression test

```bash
# run the project's test runner, e.g.:
cd <repo> && python -m pytest -k colon -x