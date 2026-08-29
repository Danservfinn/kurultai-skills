# Examples — forge-agent-workspace-setup

## Example 1: Fresh install with Hermes only

Input: macOS machine, Hermes agent host installed, Node version unknown.

```
node --version        # v22.11.0 — OK
npm --version         # 10.9.0 — OK
npx forge-memory      # guided installer
```

Installer flow:
- Data folder: keep default `~/.forge`
- Adapter menu: Hermes row detected and enabled (Space); OpenClaw, Codex, Claude Code rows disabled (not installed)
- Forge-to-Forge sharing: off
- iPhone pairing: skip

Expected output ends with `Forge Memory configured and checked` and `Doctor: passed`. Then:

```
npx forge-memory status
npx forge-memory doctor
```

Open `http://127.0.0.1:4317/forge/` — web app loads. Output: running runtime, Hermes adapter configured, data in `~/.forge`.

## Example 2: Node too old, then multi-agent setup

Input: `node --version` returns `v18.20.4`.

```
nvm install --lts
nvm use --lts
# reopen terminal
node --version        # v22.x — OK
npx forge-memory
```

Adapter menu: OpenClaw, Hermes, and Claude Code detected — toggle all three on with Space. Codex row disabled. Confirm data folder, sharing off. Verify with `npx forge-memory doctor` → `Doctor: passed`.

## Example 3: Pairing a remote Codex client and updating

Input: Forge already installed; a remote Codex client tries to reach Forge over Tailscale and is denied (default-deny).

```
npx forge-memory pairing
# pending request shown; enter the client's short code once; approve scoped renewable credential
```

Credential appears in Settings → Agents and can be revoked there.

Before updating Forge:

```
cp ~/.forge/forge.sqlite ~/.forge/forge.sqlite.bak
npx forge-memory update
npx forge-memory doctor