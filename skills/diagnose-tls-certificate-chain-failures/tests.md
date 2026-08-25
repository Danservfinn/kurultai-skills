# Tests

Manual checklist. Replace `<service>`, `<container>`, `<host>`, `<port>` with real values for a test deployment.

1. **In-container reproduction works or falls back cleanly.** Run `docker compose exec <service> curl -Iv https://<host>:<port>/`. If it exits 0 or 60, record the code. If it exits 126/127 (curl missing), run `docker run --rm --network container:<container> curlimages/curl:latest -Iv https://<host>:<port>/` and confirm it produces TLS output. Assert: a TLS diagnostic was obtained from inside the container's network namespace by one of the two methods.

2. **Chain count distinguishes root cause.** Run `openssl s_client -connect <host>:<port> -servername <host> -showcerts </dev/null | grep -c 'BEGIN CERTIFICATE'`. Against a deliberately leaf-only endpoint, assert the count is 1. After applying the step-4 fix, assert the count is 2 or more.

3. **Exit code 60 is treated as failure even when cert details print.** Run `curl -Iv https://<host>:<port>/` against the broken endpoint; assert the output contains certificate subject/issuer lines AND the process exits 60 (`echo $?`). Confirm the skill's guidance flags this as failed verification.

4. **Host-succeeds/container-fails is not auto-diagnosed as a container problem.** Reproduce the case (host curl cached intermediate). Assert the procedure's next action is the `openssl s_client -showcerts` count from step 2, not a trust-store fix.

5. **Home Assistant fix path is YAML, not UI.** Open Home Assistant Settings > System > Network and confirm no SSL certificate/key fields exist there; confirm the skill's step 4 directs the operator to `configuration.yaml` under `http:` with `ssl_certificate`/`ssl_key`, and that a Core restart is required.

6. **End-to-end verification.** After the fix and restart, run `docker compose exec <service> curl -Iv https://<host>:<port>/` (or sidecar fallback) and assert exit code 0 with no `unable to get local issuer certificate`; then check `docker compose logs --tail 50 <service>` and assert the client adapter logs a successful connection with no SSL errors.