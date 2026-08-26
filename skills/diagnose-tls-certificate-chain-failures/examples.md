# Examples

## Example 1 — Home Assistant serving leaf-only wildcard cert (Hermes client)

Inputs:
- `TARGET_URL=https://ha.home.abc.xyz:8123`
- `CLIENT_CONTAINER=hermes-agent`
- `TLS_TERMINATION=home-assistant` (HA terminates TLS itself)
- `TLS_SERVICE_CONTAINER=homeassistant`

Run:
```
docker exec hermes-agent curl -Iv https://ha.home.abc.xyz:8123/
```
Output ends with `curl: (60) SSL certificate problem: unable to get local issuer certificate` — verification failed despite the handshake and certificate printout.

Chain inspection from the host:
```
echo | openssl s_client -connect ha.home.abc.xyz:8123 -servername ha.home.abc.xyz -showcerts 2>/dev/null | grep -c 'BEGIN CERTIFICATE'
1
```
Count of 1 → server sends only the leaf. Host curl may still succeed (macOS AIA chasing) — ignore that; the count is authoritative.

Fix: in Home Assistant's `configuration.yaml`:
```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```
Confirm `/ssl/fullchain.pem` contains ≥ 2 certificates, then `docker restart homeassistant` (brief HA downtime). Rerun the container curl — exit 0. Hermes Home Assistant adapter reconnects without `SSLCertVerificationError`.

## Example 2 — Client container has no curl

Inputs:
- `TARGET_URL=https://ha.home.abc.xyz:8123`
- `CLIENT_CONTAINER=hermes-agent` (minimal image, no curl/openssl)

`docker exec hermes-agent sh -c 'command -v curl; command -v openssl'` returns nothing. Skip in-container probing; run from the host:
```
echo | openssl s_client -connect ha.home.abc.xyz:8123 -servername ha.home.abc.xyz -showcerts 2>/dev/null | grep -c 'BEGIN CERTIFICATE'
```
Count 1 → same incomplete-chain root cause; fix the server as in Example 1. After the fix, verify from the host with `curl -Iv https://ha.home.abc.xyz:8123/` (exit 0) and check the Hermes logs for a successful adapter connection.

## Example 3 — Complete chain, stale container CA store

Inputs:
- `TARGET_URL=https://api.internal.corp:443`
- `CLIENT_CONTAINER=worker`
- `TLS_TERMINATION=nginx reverse proxy`

In-container curl exits 60. Host-side chain count:
```
echo | openssl s_client -connect api.internal.corp:443 -servername api.internal.corp -showcerts 2>/dev/null | grep -c 'BEGIN CERTIFICATE'
3
```
Count ≥ 2 → chain is complete; the container's CA store is the problem. Fix the client, not the server:
```
docker compose pull worker && docker compose up -d worker
```
Rerun in-container curl — exit 0. No server restart needed.