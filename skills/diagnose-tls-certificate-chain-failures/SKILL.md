---
name: diagnose-tls-certificate-chain-failures
description: Diagnose and fix curl error 60 "unable to get local issuer certificate" when a containerized client fails TLS verification against a TLS-terminating service such as Home Assistant with an ACME certificate
category: ops-automation
---
```

# Diagnose TLS Certificate Chain Failures from Containerized Clients

## Goal

Determine whether an `SSLCertVerificationError: unable to get local issuer certificate` (curl exit 60) from a client inside a Docker container is caused by (a) the server serving an incomplete certificate chain, or (b) the container's CA trust store — and fix the actual cause.

## Inputs

- `TARGET_URL` — full HTTPS URL of the TLS-terminating service, e.g. `https://ha.home.abc.xyz:8123`
- `CLIENT_CONTAINER` — Docker container name or Compose service name of the failing client (e.g. `hermes-agent`)
- `TLS_TERMINATION` — what terminates TLS: the service itself (e.g. Home Assistant), or a reverse proxy (nginx, Traefik, Caddy, Nginx Proxy Manager)
- `TLS_SERVICE_CONTAINER` — the Docker container that must be restarted to apply a certificate fix (for Home Assistant in Docker, this is the Home Assistant container; for a reverse proxy, the proxy container). Only needed if a fix is applied.

No API keys required. Requires Docker access on the host.

## Steps

1. Check that the client container has `curl` or `openssl`. Run `docker exec <CLIENT_CONTAINER> sh -c 'command -v curl; command -v openssl'`. If neither exists, skip to step 2 and run the chain inspection from the host instead — the served chain is identical regardless of where you connect from.
2. Run `docker exec <CLIENT_CONTAINER> curl -Iv <TARGET_URL>/` (or `docker exec <CLIENT_CONTAINER> openssl s_client -connect ...` if curl is absent). Capture the full output. Note the exit code: curl error 60 means verification failed even if certificate details were printed first — printing the subject/issuer is not success.
3. Inspect the chain the server actually sends, from the host: `echo | openssl s_client -connect <host>:<port> -servername <hostname> -showcerts 2>/dev/null | grep -c 'BEGIN CERTIFICATE'`. The `-showcerts` flag is mandatory; without it only the leaf is printed and the count is always 1. A count of 1 means the server sends only the leaf certificate (root cause: incomplete chain). A count of 2 or more means the chain is complete and the problem is the client's trust store.
4. Optionally compare with host `curl -Iv <TARGET_URL>/`, but do not treat host success as proof the chain is complete: macOS host curl uses the system trust store and may fetch missing intermediates via AIA chasing, succeeding against a leaf-only chain that a Linux container rejects. The `openssl s_client -showcerts` count from step 3 is authoritative.
5. Fix the actual cause:
   - **Incomplete chain (count = 1):** point the TLS terminator at the full-chain file from the ACME client. For Home Assistant, this is configured only via the `http:` integration in `configuration.yaml` — set `ssl_certificate: /ssl/fullchain.pem` and `ssl_key: /ssl/privkey.pem` (paths as mounted in your HA container). There is no UI page for this. For a reverse proxy, update its certificate path to the fullchain file. Verify the file itself contains multiple certificates: `grep -c 'BEGIN CERTIFICATE' /ssl/fullchain.pem` should be ≥ 2.
   - **Complete chain but container rejects (count ≥ 2):** the container's CA store is stale or missing the root. Rebuild/update the client image (`docker compose pull <service> && docker compose up -d <service>`), or mount a current CA bundle.
   - Do **not** disable TLS verification (`ssl_verify: false`, `--insecure`, `verify=False`) as a workaround.
6. Restart the TLS-terminating service to load the new certificate. **Warning: this interrupts the service briefly.** Run `docker restart <TLS_SERVICE_CONTAINER>` (or `docker compose restart <service>`). For Home Assistant configured via `configuration.yaml`, a restart is required for `http:` changes.
7. Rerun the step 2 command from inside the client container. Confirm curl exits 0 with no error 60, and that `openssl s_client -showcerts` now reports a chain count ≥ 2.
8. Confirm the original client (e.g. the Hermes Home Assistant adapter) reconnects without `SSLCertVerificationError` in its logs.

## Outputs

- Verbose TLS diagnostics from inside the container and from the host
- Certificate chain count from `openssl s_client -showcerts` (authoritative root-cause evidence)
- Root cause determination: incomplete served chain vs. container trust store
- Working TLS connection from the containerized client

## Failure modes

- Server serves only the leaf certificate; clients cannot build a path to a trusted root. Fix is the fullchain file, not client-side changes.
- Interpreting curl printing certificate details as successful verification — exit code 60 still means verification failed.
- Trusting host curl success on macOS: AIA chasing can mask a leaf-only chain. Always use `openssl s_client -showcerts` for the chain count.
- Assuming the client product has a certificate setting when it uses the container's system CA store (e.g., Hermes MCP `ssl_verify`/`client_cert` settings do not apply to the Home Assistant integration).
- Client container lacking `curl`/`openssl` — a shell "not found" error is not a TLS failure; fall back to host-side `openssl s_client`.
- Disabling TLS verification as a workaround — insecure; do not ship this as a fix.

## Source

Discord thread "SSL Problems with Home Assistant" (discord / 1485307775444844625 / 1539762449043955777, 2026-08-26); Hermes Agent MCP Config Reference (hermes-agent.nousresearch.com/docs/reference/mcp-config-reference); Home Assistant `http` integration docs (home-assistant.io/integrations/http).