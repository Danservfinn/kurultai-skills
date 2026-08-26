# Commands

Placeholders:
- `<TARGET_URL>` — full HTTPS URL, e.g. `https://ha.home.abc.xyz:8123`
- `<HOST>` / `<PORT>` — hostname and port parsed from `TARGET_URL`
- `<CLIENT_CONTAINER>` — Docker container or Compose service name of the failing client
- `<TLS_SERVICE_CONTAINER>` — container that terminates TLS and must be restarted to apply a cert fix (Home Assistant container, or the reverse-proxy container). Restarting it interrupts the service briefly.
- `<SERVICE>` — Compose service name equivalent of `<CLIENT_CONTAINER>` or `<TLS_SERVICE_CONTAINER>`

## Step 1 — check tooling inside the client container

```sh
docker exec <CLIENT_CONTAINER> sh -c 'command -v curl; command -v openssl'
```

## Step 2 — verbose TLS probe from inside the container

```sh
docker exec <CLIENT_CONTAINER> curl -Iv <TARGET_URL>/
# fallback if curl is absent but openssl exists:
docker exec <CLIENT_CONTAINER> openssl s_client -connect <HOST>:<PORT> -servername <HOST> < /dev/null
# if neither exists, probe only from the host (step 3)
```

## Step 3 — count certificates the server actually sends (authoritative)

```sh
echo | openssl s_client -connect <HOST>:<PORT> -servername <HOST> -showcerts 2>/dev/null | grep -c 'BEGIN CERTIFICATE'
```

`-showcerts` is required. Without it only the leaf is printed and the count is always 1.

## Step 4 — optional host curl comparison (not authoritative on macOS)

```sh
curl -Iv <TARGET_URL>/
```

## Step 5a — fix incomplete chain (Home Assistant example)

Edit `configuration.yaml` inside the HA config volume (no UI setting exists):

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

Verify the fullchain file contains the intermediates:

```sh
grep -c 'BEGIN CERTIFICATE' /path/to/config/ssl/fullchain.pem   # expect >= 2
```

## Step 5b — fix stale container CA store

```sh
docker compose pull <SERVICE> && docker compose up -d <SERVICE>
```

## Step 6 — restart the TLS-terminating service (brief downtime)

```sh
docker restart <TLS_SERVICE_CONTAINER>
# or, with Compose:
docker compose restart <SERVICE>
```

## Step 7 — re-verify

```sh
docker exec <CLIENT_CONTAINER> curl -Iv <TARGET_URL>/; echo "exit=$?"
echo | openssl s_client -connect <HOST>:<PORT> -servername <HOST> -showcerts 2>/dev/null | grep -c 'BEGIN CERTIFICATE'
```

## Step 8 — confirm client logs

```sh
docker logs --since 5m <CLIENT_CONTAINER> 2>&1 | grep -i -e SSLCertVerificationError -e "Failed to connect"
# expect no new SSLCertVerificationError lines