---
name: forge-agent-workspace-setup
description: Install and verify the Forge local-first structured workspace (goals, tasks, habits, notes, psyche records) shared between a human and Hermes/OpenClaw/Codex/Claude Code agents
category: product-building
---

# Forge Agent Workspace Setup

## Goal

Install the Forge local-first runtime on macOS, configure agent-host adapters (OpenClaw, Hermes, Codex, Claude Code), verify the runtime and web app, pair remote clients with scoped credentials, and know the safe update path.

## Inputs

- Node.js 22+ environment (check with `node --version`; install an LTS release if older)
- At least one agent host installed or to be configured: OpenClaw, Hermes, Codex, or Claude Code
- No API key required for core install. Google Calendar sync requires your own Google app credentials until Forge's Google verification completes (~4-5 weeks).

## Steps

1. Confirm Node.js 22 or newer: run `node --version` and `npm --version`. If the major version is below 22, install the current LTS (e.g. via `nvm install --lts` or a nodejs.org installer), reopen the terminal, and re-check.
2. Run `npx forge-memory` to start the guided installer. It sets up the local Forge runtime, discovers installed agent hosts in the background, and prompts for the data folder (default `~/.forge`). Keep the default or change it.
3. In the adapter menu, toggle with Space which detected hosts to configure: OpenClaw, Hermes, Codex, Claude Code. Hosts not detected appear as disabled rows and cannot be selected.
4. Confirm the Forge data folder. Leave optional Forge-to-Forge sharing off unless you need it. Optionally pair an iPhone now, or later with `npx forge-memory pair-ios`.
5. Wait for the installer to print `Forge Memory configured and checked` and `Doctor: passed`. Then verify with `npx forge-memory ui`, `npx forge-memory status`, and `npx forge-memory doctor`.
6. Open `http://127.0.0.1:4317/forge/` in a browser and confirm the web app loads.
7. For remote/agent clients: run `npx forge-memory pairing` to review pending pairing requests. Enter the client's short code once and approve scoped renewable credentials. Access is default-deny: network reachability alone grants nothing. Credentials can be reviewed and revoked in Settings → Agents.
8. To update: back up `~/.forge/forge.sqlite` first, then run `npx forge-memory update`.

## Outputs

- Running local Forge runtime at `http://127.0.0.1:4317/forge/` with SQLite-backed data in `~/.forge`
- Configured agent adapters sharing the Forge runtime and API
- Paired scoped credentials for remote clients, reviewable/revocable in Settings

## Failure modes

- Node version older than 22 causes installer failure — re-check `node --version` after any Node upgrade and terminal reopen.
- iPhone pairing over Iroh/Tailscale can be finicky: the QR code may fail to load on the phone and manual setup may break. Try Iroh (slower, easier), Tailscale, or a fixed/private IP.
- Updates may lose data if `forge.sqlite` is not backed up first. Always copy it before `npx forge-memory update`.
- Google Calendar OAuth requires your own Google app credentials until Forge's Google verification completes (~4-5 weeks).

## Source

- Website guide: https://albertbuchard.github.io/forge/ — installer steps, `npx forge-memory ui/status/doctor`, `http://127.0.0.1:4317/forge/`
- Discord thread "Forge — A plugin for project management and mental health tracking" (discord / 1316137596535177246 / 1489815577676746954, 2026-08-29): `npx forge-memory pairing` default-deny credentials, `npx forge-memory update` with `forge.sqlite` backup, Iroh/Tailscale/fixed-IP pairing.