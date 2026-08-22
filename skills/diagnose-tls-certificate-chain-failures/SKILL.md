---
name: diagnose-tls-certificate-chain-failures
description: Diagnose and fix SSL "unable to get local issuer certificate" errors when a client inside a Docker container fails to connect to a TLS-terminating service with a Let's Encrypt certificate
category: ops-automation
---

# Diagnose TLS Certificate Chain Failures

## Goal

Determine whether an `unable to get local issuer certificate` / curl error 60 failure is caused by (a) the server serving only the leaf certificate instead of the full chain, or (b) a missing CA in the container's trust store — then fix the actual cause and verify the client connects.

## Inputs

- Container name or Compose service name of the failing client (e.g. `hermes-agent` / `hermes`)
- URL of the TLS endpoint as `host:port` (e.g. `ha.home.abc.xyz:8123`)
- Knowledge of what terminates TLS: the service itself (e.g. Home Assistant), nginx, Traefik, Caddy, Nginx Proxy Manager, etc.
- Shell access on the Docker host with `docker` / `docker compose`
- If the fix is on the server: admin access to the TLS-terminating service and its ACME client output files (`fullchain.pem`, `privkey.pem`)

## Steps

1. Run the failing request from inside the client container and capture the TLS handshake:
   `docker exec <container> curl -Iv https://<host>:<port>/`
   Note the `CAfile:`/`CApath:` lines, the `issuer:` line, and whether curl exits with error 60 (`unable to get local issuer certificate`).
2. Run the identical `curl -Iv https://<host>:<port>/` from the host shell. Compare results:
   - Both fail with `unable to get local issuer certificate` → the server's served chain is incomplete; the container trust store is not the problem.
   - Host succeeds but container fails → the container's CA bundle is missing the issuer (custom/internal CA case).
3. Read the `issuer:` line from the curl output (e.g. `issuer: C=US; O=Let's Encrypt; CN=YR2`). Check the CA's documented chain requirements (Let's Encrypt: https://letsencrypt.org/certificates/) to confirm whether the server must serve the complete intermediate chain. Note: curl can print certificate details before verification finishes — a printed cert does not mean verification passed; only the final verify result and exit code matter.
4. Fix the TLS endpoint to serve the full-chain file from the ACME client, then restart the service:
   - Home Assistant UI: Settings > System > Network > HTTP server — set the SSL certificate to `/ssl/fullchain.pem` and key to `/ssl/privkey.pem`.
   - Home Assistant YAML: point `ssl_certificate:` in the `http:` integration at the fullchain file.
   - Other terminators (nginx/Traefik/Caddy): configure them to serve the fullchain PEM (leaf + intermediates) instead of the leaf alone.
5. Re-run `docker exec <container> curl -Iv https://<host>:<port>/` and confirm the handshake completes with no curl error 60. Then verify the original client (e.g. the Hermes Home Assistant adapter) connects normally in its logs.

## Outputs

- Verbose curl TLS diagnostics from inside the container and from the host
- Root-cause determination: incomplete server chain vs. container CA trust
- Working TLS connection from the client container (curl exit 0, client connects)

## Failure modes

- Server serves only the leaf certificate instead of the full chain — common with newer Let's Encrypt chains such as YR2, which require the server to provide the complete intermediate chain (a 3-cert chain was needed in the source case).
- Misattributing the failure to the container's CA trust store when the server chain is the actual problem — always run curl from the host to disambiguate.
- Custom internal CA not present in the container's system CA bundle — host curl succeeds, container curl fails; fix by adding the CA to the container bundle, not by touching the server.
- Do not disable TLS verification (`ssl_verify: false` or equivalent) instead of fixing the chain. For Hermes specifically, MCP `ssl_verify`/`client_cert` settings do not apply to the Home Assistant integration; it uses the container's normal CA trust.

## Source

Discord thread `1485307775444844625/1539762449043955777` — "SSL Problems with Home Assistant" (2026-08-22). Key references: https://letsencrypt.org/certificates/, https://www.home-assistant.io/integrations/http/#http-server-settings