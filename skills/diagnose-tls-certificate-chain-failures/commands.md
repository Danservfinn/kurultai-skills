# Commands

Placeholders:
- `<container>` — container name or Compose service name
- `<host>` — TLS endpoint hostname
- `<port>` — TLS endpoint port (e.g. `8123`, `443`)

## Step 1 — curl from inside the client container

```sh
docker exec <container> curl -Iv https://<host>:<port>/
```

Or, from the Compose project directory when using a service name:

```sh
docker compose exec <container> curl -Iv https://<host>:<port>/
```

## Step 2 — same curl from the host shell

```sh
curl -Iv https://<host>:<port>/
```

## Step 3 — inspect issuer / chain (optional confirmation)

```sh
openssl s_client -connect <host>:<port> -servername <host> </dev/null 2>/dev/null | grep -E '^(subject|issuer|Verify return code)'
```

## Step 4 — fix and restart the TLS terminator (Home Assistant example)

UI path: Settings > System > Network > HTTP server → SSL certificate `/ssl/fullchain.pem`, SSL key `/ssl/privkey.pem`.

YAML equivalent (`configuration.yaml`):

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

```sh
docker restart <home-assistant-container>
```

## Step 5 — verify from the container

```sh
docker exec <container> curl -Iv https://<host>:<port>/
echo "curl exit: $?"