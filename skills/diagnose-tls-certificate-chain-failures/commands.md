# Commands

Placeholders:
- `<service>` — Docker Compose service name (find with `docker compose ps`)
- `<container>` — container name or ID (find with `docker ps`)
- `<host>` — hostname of the TLS endpoint without scheme
- `<port>` — port of the TLS endpoint (e.g., `8123`)

## Step 1 — reproduce inside the container

```bash
docker compose exec <service> curl -Iv https://<host>:<port>/
```

Fallback if curl is absent (exit 126/127):

```bash
docker compose exec <service> openssl s_client -connect <host>:<port> -servername <host> -showcerts </dev/null
```

Sidecar fallback (shares the container's network namespace; needs Docker Hub access):

```bash
docker run --rm --network container:<container> curlimages/curl:latest -Iv https://<host>:<port>/
```

## Step 2 — compare from the host and count served certificates

```bash
curl -Iv https://<host>:<port>/
openssl s_client -connect <host>:<port> -servername <host> -showcerts </dev/null | grep -c 'BEGIN CERTIFICATE'
```

## Step 3 — identify the issuer

```bash
openssl s_client -connect <host>:<port> -servername <host> </dev/null 2>/dev/null | openssl x509 -noout -issuer
```

Then check https://letsencrypt.org/certificates/ in a browser.

## Step 4 — fix the endpoint (Home Assistant example)

Edit `configuration.yaml` on the Home Assistant host:

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

Verify the file actually contains the chain:

```bash
grep -c 'BEGIN CERTIFICATE' /ssl/fullchain.pem
```

## Step 5 — restart and re-verify

```bash
docker compose restart <tls-service>
docker compose exec <service> curl -Iv https://<host>:<port>/
openssl s_client -connect <host>:<port> -servername <host> -showcerts </dev/null | grep -c 'BEGIN CERTIFICATE'
```

## Step 6 — confirm the client connects

```bash
docker compose logs --tail 50 <service> | grep -i -e ssl -e connect