# Tests

Manual checklist. Replace placeholders per commands.md conventions.

1. **Key auth works non-interactively.** Run the Step 4 command; it must print `200` with no password prompt. If it hangs or prints `Permission denied`, check Step 3 permissions (`ls -ld ~/.ssh ~/.ssh/authorized_keys` shows `drwx------` / `-rw-------` owned by `<user>`).

2. **Tunnel forwards to the remote agent.** With the Step 5 tunnel running, `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:<localPort>/health` returns `200`; kill the tunnel (`pkill -f "ssh -N -L <localPort>"`) and the same curl fails — proving the tunnel, not a local agent, is serving.

3. **Management endpoints return remote data, not just 200.** Run the Step 6 loop. Every endpoint must report `HTTP 200` with a non-empty body. Additionally, create a session on the remote host (`ssh <user>@<host> 'ls ~/.hermes/state.db'` exists) and confirm `/sessions` through the tunnel lists session IDs matching the remote `state.db` — not an empty array.

4. **Wrong-user failure is detectable.** Temporarily SSH as a different user with shell access and repeat the Step 6 loop against that user's tunnel: `/sessions` returns empty/404. This confirms the Step 6 check catches the "empty management screens" failure mode.

5. **Docker guards fire.** On a remote host where `~/bin/remote-hermes` already exists, re-run the Step 7 block: it must print `refusing: ~/bin/remote-hermes already exists` and exit non-zero, and your SSH session must survive (the guard runs inside `bash -s`, not the login shell).

6. **Port parameters are honored.** Run the tunnel with `<agentPort>` and `<localPort>` set to non-default values (e.g., 8642 remote, 18642 local); the Step 6 checks against `http://127.0.0.1:18642` still pass, confirming no hardcoded 8642.