# Tests — forge-agent-workspace-setup

Manual checklist. Run each assertion on a machine that has followed the skill.

1. `node --version` prints v22.0.0 or newer before `npx forge-memory` is run.
2. After the installer completes, its output contains both `Forge Memory configured and checked` and `Doctor: passed`.
3. `npx forge-memory doctor` exits reporting passed status, and `npx forge-memory status` shows the runtime as running.
4. `http://127.0.0.1:4317/forge/` loads the Forge web app in a browser.
5. `~/.forge/forge.sqlite` exists; a copy `forge.sqlite.bak` exists after the backup step and before `npx forge-memory update`.
6. A remote client that has not paired is denied access even when network-reachable; after `npx forge-memory pairing` approval, its credential appears in Settings → Agents and can be revoked there.