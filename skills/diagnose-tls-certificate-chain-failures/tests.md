# Tests

Reviewer-runnable checks against a test TLS endpoint and container.

1. **`-showcerts` distinguishes chains.** Against a server serving a fullchain file, run `echo | openssl s_client -connect <HOST>:<PORT> -servername <HOST> -showcerts 2>/dev/null | grep -c 'BEGIN CERTIFICATE'` and the same command without `-showcerts`. With `-showcerts` the count is ≥ 2; without it the count is exactly 1. This proves the skill's diagnostic can actually detect the difference.

2. **Leaf-only server reproduces error 60 in a Linux container.** Configure a test endpoint (e.g. nginx with only the leaf `cert.pem`) and run `docker exec <CLIENT_CONTAINER> curl -Iv https://<HOST>:<PORT>/`; assert exit code 60 and `unable to get local issuer certificate` in output. Then switch the endpoint to `fullchain.pem`, restart it, and assert the same command exits 0. This is the end-to-end fix verification.

3. **Host curl is not trusted as the chain oracle.** On a macOS host against the leaf-only endpoint from test 2, record whether host `curl -Iv` succeeds or fails. Either result is acceptable; the assertion is that the skill's decision in step 3/4 uses the `openssl s_client -showcerts` count, not host curl. Confirm by reading commands.md: the count command appears as the authoritative check and host curl is labeled non-authoritative.

4. **Missing-tooling path works.** Run `docker exec <CLIENT_CONTAINER> sh -c 'command -v curl; command -v openssl'` against a container with neither (e.g. `docker run --rm alpine sh -c 'command -v curl; command -v openssl'` returns nothing). Confirm the skill's step 1–2 fallback routes diagnosis to host-side `openssl s_client` and does not report a shell "not found" error as a TLS failure.

5. **Fix instruction matches real Home Assistant configuration surface.** Check Home Assistant's `http` integration documentation (https://www.home-assistant.io/integrations/http/): `ssl_certificate`/`ssl_key` are documented as YAML configuration keys. Confirm the skill contains no UI navigation path for certificate settings.

6. **No insecure workaround shipped.** `grep -n -e '--insecure' -e 'ssl_verify: false' -e 'verify=False' SKILL.md commands.md` returns no match inside any fix step (only the failure-modes prohibition). Restart commands in commands.md step 6 include a downtime warning and `<TLS_SERVICE_CONTAINER>` is defined in the placeholder list at the top of commands.md.