# Examples

## Example 1 — Home Assistant serving only the leaf (YR2 chain)

**Input:**
- Container: `hermes-agent`
- Endpoint: `ha.home.abc.xyz:8123`
- TLS terminator: Home Assistant itself, wildcard Let's Encrypt cert `*.home.abc.xyz`

**Steps:**
1. `docker exec hermes-agent curl -Iv https://ha.home.abc.xyz:8123/` → handshake reaches `Certificate (11)`, then `TLS alert, unknown CA (560)`, `curl: (60) SSL certificate problem: unable to get local issuer certificate`.
2. Host shell `curl -Iv https://ha.home.abc.xyz:8123` → also exits 60 with `OpenSSL verify result: unable to get local issuer certificate (20)`, despite printing cert details (`issuer: C=US; O=Let's Encrypt; CN=YR2`).
3. Both fail → server chain is the problem. YR2 requires the full intermediate chain.
4. In Home Assistant: Settings > System > Network > HTTP server → SSL certificate `/ssl/fullchain.pem`, key `/ssl/privkey.pem`. Restart Home Assistant.
5. Re-run container curl → exit 0; Hermes Home Assistant adapter connects.

**Output:** Root cause = leaf-only chain; fixed by serving fullchain.pem.

## Example 2 — Compose service name instead of container name

**Input:**
- Compose service: `hermes` (container name differs)
- Endpoint: `home.internal.example:443`
- TLS terminator: nginx reverse proxy

**Steps:**
1. From the Compose project directory: `docker compose exec hermes curl -Iv https://home.internal.example:443/` → error 60.
2. Host `curl -Iv https://home.internal.example:443/` → succeeds.
3. Divergent results → container CA trust issue, not the server chain. Inspect `issuer:` from host output; if it is a custom internal CA, add it to the container's `/usr/local/share/ca-certificates/` and run `update-ca-certificates`.

**Output:** Root cause = internal CA missing from container bundle.

## Example 3 — Three-cert chain required

**Input:**
- Container: `hermes-agent`, endpoint `ha.home.abc.xyz:8123`, Home Assistant terminates TLS with a Let's Encrypt cert.

**Steps:**
1–3. Same diagnosis as Example 1: both container and host curl exit 60; issuer is Let's Encrypt.
4. Operator's ACME client produced separate `cert.pem` and `chain.pem`; concatenating leaf + both intermediates into a 3-cert `fullchain.pem` and pointing Home Assistant at it resolved the failure.

**Output:** "Since I was using Lets Encrypt, I needed a 3 cert chain for it to work." — resolved.