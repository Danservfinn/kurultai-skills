# Tests — Manual Checklist

## 1. Non-interactive SSH health check returns a success code

Run the step-3 command with real values (e.g. `REMOTE_USER=hermes REMOTE_HOST=203.0.113.10 REMOTE_SSH_PORT=22 AGENT_PORT=8642`). Assert it prints a 2xx HTTP code and never prompts. If `/health` returns non-200 or connection-refused, run the documented fallback (`ss -tlnp` + root-path curl) and confirm the actual port/endpoint; pass if a working endpoint is identified, fail only if no listener exists for the agent user.

## 2. Tunnel forwards the loopback API

Start the step-4 tunnel with `LOCAL_PORT=18642`. Assert `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18642/health` returns a 2xx code (or the endpoint found in test 1's fallback). Also assert the port is NOT reachable from another machine — confirming the API is not publicly exposed.

## 3. Authorized key lands in the agent user's home

Run step 2, then `ssh -p <port> <user>@<host> 'ls -ld ~/.ssh ~/.ssh/authorized_keys'`. Assert the path is `~/.ssh/authorized_keys` (the SSH user's home, not an app data directory), `.ssh` is mode 700, `authorized_keys` is mode 600, and both are owned by the agent user.

## 4. Home-directory data is visible over SSH as the agent user

Run `ssh -o BatchMode=yes <user>@<host> 'ls ~/.hermes'` as the agent's runtime user. Assert it lists agent data (e.g. `config.yaml`, `profiles/`, `state.db`). Run the same command as a different user to reproduce the empty-`~` failure mode and confirm the skill's diagnosis applies.

## 5. Wrong-user failure is detected

Repeat the step-3 verification with a user that does not run the agent. Assert SSH auth may succeed but `ls ~/.hermes` is empty or missing — the skill must instruct switching to the agent's runtime user rather than proceeding.

## 6. Teardown closes the tunnel

After `pkill -f "ssh -N -L LOCAL_PORT"`, assert `curl --max-time 3 http://127.0.0.1:LOCAL_PORT/health` now fails with connection refused.