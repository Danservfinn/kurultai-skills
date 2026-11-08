# Commands

Placeholders:
- `<PATTERN>` — grep pattern derived from the task (component name, function, endpoint).
- `<DIR>` — source directory, e.g. `src/` or `api/`.
- `<FILE>` — a file being read or edited.
- `<TESTCMD>` — the project's test command, e.g. `pytest -q`, `npm test --silent`, `go test ./...`.

## Step 1 — Read and trace the affected code

```bash
rg -n "<PATTERN>" <DIR>          # or: grep -rn "<PATTERN>" <DIR>
sed -n '1,200p' <FILE>           # or open in editor; read whole small files with cat
cat package.json requirements.txt go.mod 2>/dev/null   # know the stack and installed deps
```

## Step 2 — Check each ladder rung

```bash
rg -ni "<verb|util|helper name>" <DIR>          # rung 2: already in codebase?
rg -n "\"dependencies\"|\"devDependencies\"" package.json   # rung 5: installed deps (adapt per stack)
```

(Rungs 1, 3, 4, 6 are judgment calls against stdlib docs, platform docs, and the traced flow — no shell command.)

## Step 3 — Implement the minimal change

```bash
# edit <FILE> with the editor; show the diff for the report:
git diff <FILE>
```

## Step 4 — Write and run the test for risky logic (if applicable)

```bash
# add one small test to the existing test file, then:
<TESTCMD>                       # e.g. pytest api/test_reports.py -q
```

## Step 5 — Report and mark shortcuts

```bash
# find deferred work for the ledger:
rg -n "shortcut:" <DIR>