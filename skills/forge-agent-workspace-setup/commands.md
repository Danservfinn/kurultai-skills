# Commands — forge-agent-workspace-setup

Placeholders: none required; all commands are literal. `~/.forge` is the default data folder — substitute your folder if you changed it during install.

## Step 1 — verify Node.js

```bash
node --version
npm --version
```

If older than 22 (example via nvm; any LTS install method works):

```bash
nvm install --lts
nvm use --lts
```

Reopen the terminal, then re-run `node --version`.

## Step 2 — run the guided installer

```bash
npx forge-memory
```

Interactive: choose data folder (default `~/.forge`).

## Step 4 — optional iPhone pairing

```bash
npx forge-memory pair-ios
```

## Step 5 — verify runtime

```bash
npx forge-memory ui
npx forge-memory status
npx forge-memory doctor
```

## Step 6 — open the web app

```bash
open http://127.0.0.1:4317/forge/
```

## Step 7 — review pairing requests

```bash
npx forge-memory pairing
```

## Step 8 — back up and update

```bash
cp ~/.forge/forge.sqlite ~/.forge/forge.sqlite.bak
npx forge-memory update