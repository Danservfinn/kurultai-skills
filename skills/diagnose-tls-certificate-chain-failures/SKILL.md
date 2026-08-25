---
name: diagnose-tls-certificate-chain-failures
description: Diagnose and fix SSL "unable to get local issuer certificate" errors when a client inside a Docker container fails to connect to a TLS-terminating service such as Home Assistant with Let's Encrypt certificates
category: ops-automation
---

# Diagnose TLS Certificate Chain Failures in Docker

## Goal

Determine whether an `SSLCertVerificationError: unable to get local issuer certificate` from a containerized client is caused by (a) the TLS endpoint serving an incomplete certificate chain (leaf only, missing intermediates) or (b) a missing CA in the container's trust store, then fix the actual root cause and verify the client connects.

## Inputs

- Docker Compose service name or container name of the failing client (e.g., `hermes`, `hermes-agent`)
- URL of the TLS endpoint (e.g., `https://ha.home.abc.xyz:8123`)
- Knowledge of what terminates TLS for the endpoint (the service itself, nginx, Traefik, Caddy, etc.)
- Shell access on the Docker host; `docker` and `docker compose` installed
- If the fix requires editing the TLS-terminating service's config (e.g., Home Assistant `configuration.yaml`), access to that config and the ability to restart the service

## Steps

1. Reproduce the error inside the container. From the directory containing the Compose file, run `docker compose exec <service> curl -Iv https://<host>:<port>/`. If curl is not installed in the container (exit code 126 or 127), use the fallback: `docker compose exec <service> openssl s_client -connect <host>:<port> -servername <host> -showcerts </dev/null` if openssl exists, or `docker run --rm --network container:<container> curlimages/curl:latest -Iv https://<host>:<port>/` to run curl in a sidecar sharing the container's network namespace. Record the exit code and the certificate chain presented.

2. Run the same check from the host shell: `curl -Iv https://<host>:<port>/`. Compare results, but do not treat "host succeeds, container fails" as proof of a container trust-store problem: the host's curl or browser may have cached the intermediate or fetched it via AIA, while the container cannot. The authoritative test is the number of certificates the server actually presents. Count them with `openssl s_client -connect <host>:<port> -servername <host> -showcerts </dev/null | grep -c 'BEGIN CERTIFICATE'`. A Let's Encrypt endpoint presenting only 1 certificate is serving the leaf without intermediates — that is a server-side incomplete chain regardless of whether the host curl happened to succeed. Also note that curl prints certificate details before verification completes; a printed certificate with exit code 60 still means verification failed.

3. Inspect the issuer line in the output (`issuer: C=US; O=Let's Encrypt; CN=...`) and confirm the chain requirements at https://letsencrypt.org/certificates/. Serving the full intermediate chain is a baseline TLS requirement for any publicly trusted CA, not something specific to one intermediate; any endpoint presenting only the leaf cert will fail verification in clients that do not fetch intermediates out-of-band.

4. Fix the TLS endpoint to serve the full chain. For Home Assistant terminating TLS itself, the SSL certificate paths are `configuration.yaml` settings under the `http:` integration — there is no UI field for this. Set:
   ```yaml
   http:
     ssl_certificate: /ssl/fullchain.pem
     ssl_key: /ssl/privkey.pem
   ```
   Point `ssl_certificate` at the full-chain file produced by the ACME client (leaf + intermediates), not the leaf-only `cert.pem`. For other terminators (nginx, Traefik, Caddy), set the equivalent full-chain directive (e.g., nginx `ssl_certificate` with the fullchain file). Restart the TLS-terminating service (for Home Assistant Core, a full restart is required for `http:` changes).

5. Rerun the in-container check from step 1 (`docker compose exec <service> curl -Iv https://<host>:<port>/` or the fallback). Confirm verification succeeds: no `unable to get local issuer certificate`, curl exit code 0, and `openssl s_client -showcerts` now shows the leaf plus intermediate(s).

6. Confirm the original client (e.g., the Hermes Home Assistant adapter) reconnects without certificate errors in its logs.

## Outputs

- curl/openssl verbose TLS diagnostics from inside and outside the container
- Certificate count from `openssl s_client -showcerts` establishing root cause (incomplete chain vs. missing CA in container)
- Working TLS connection between client and service

## Failure modes

- Server serves only the leaf certificate instead of the full chain — fix is server-side (step 4), not client-side.
- `curl` (or `openssl`) not present in the container image (common for slim/distroless/alpine bases): `docker compose exec` exits 126/127. This is not a TLS result; use the sidecar fallback before drawing conclusions.
- Host curl succeeds while container fails due to cached/AIA-fetched intermediates on the host — do not conclude the container trust store is broken without counting the served certificates.
- Wrong docker service/container name in the exec command; check with `docker compose ps` or `docker ps`.
- Mistaking curl's printed certificate details for successful verification — exit code 60 is the authoritative failure signal.
- Attempting to fix via client-side cert settings (e.g., MCP `ssl_verify`/`client_cert` config) — these do not apply to the Home Assistant integration, which uses the container's normal CA trust.
- Home Assistant `http:` SSL settings are YAML-only; searching the UI (Settings > System > Network) for certificate fields will not find them.

## Source

Discord thread "SSL Problems with Home Assistant" (discord / 1485307775444844625 / 1539762449043955777), 2026-08-25. Home Assistant HTTP integration docs: https://www.home-assistant.io/integrations/http/. Let's Encrypt chain docs: https://letsencrypt.org/certificates/.