# Examples

## Example 1: Hermes container cannot verify Home Assistant's Let's Encrypt cert

**Input:** service `hermes-agent`, endpoint `https://ha.home.abc.xyz:8123`, TLS terminated by Home Assistant itself.

```
$ docker compose exec hermes-agent curl -Iv https://ha.home.abc.xyz:8123/
...
* SSL certificate problem: unable to get local issuer certificate
curl: (60) SSL certificate problem: unable to get local issuer certificate
```

Host curl also exits 60 with the same message. Count the served certificates:

```
$ openssl s_client -connect ha.home.abc.xyz:8123 -servername ha.home.abc.xyz -showcerts </dev/null | grep -c 'BEGIN CERTIFICATE'
1
```

One certificate = leaf only, no intermediates. Root cause: server-side incomplete chain. Fix in Home Assistant `configuration.yaml`:

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

Restart Home Assistant Core. Rerun the in-container curl — exit 0 — and confirm the Hermes adapter log shows a successful connection.

## Example 2: curl missing inside the container

**Input:** service `hermes`, endpoint `https://ha.home.abc.xyz:8123`.

```
$ docker compose exec hermes curl -Iv https://ha.home.abc.xyz:8123/
OCI runtime exec failed: exec: "curl": executable file not found — exit 127
```

This is not a TLS result. Fallback via sidecar sharing the container's network namespace:

```
$ docker run --rm --network container:hermes curlimages/curl:latest -Iv https://ha.home.abc.xyz:8123/
```

Output shows `unable to get local issuer certificate`, exit 60. Proceed with the chain-count check from the host and the server-side fix as in Example 1.

## Example 3: host curl succeeds, container fails — still a server-side chain problem

**Input:** service `hermes-agent`, endpoint `https://nvr.home.abc.xyz:8123`.

Container curl exits 60; host curl exits 0 and the browser validates fine. Naively this looks like a container trust-store problem, but the host may have cached or AIA-fetched the intermediate. Verify what the server actually sends:

```
$ openssl s_client -connect nvr.home.abc.xyz:8123 -servername nvr.home.abc.xyz -showcerts </dev/null | grep -c 'BEGIN CERTIFICATE'
1
```

One certificate means the server is not sending intermediates. Fix the TLS terminator to use the fullchain file, restart, and confirm the count is now 2+ and the in-container curl exits 0.