# Tests

1. **Container curl reproduces the failure.** Run `docker exec <container> curl -Iv https://<host>:<port>/`; before the fix, output contains `unable to get local issuer certificate` and curl exits 60 (`echo $?` returns 60).
2. **Host curl disambiguates.** Run the same curl on the host. If it also exits 60, the skill's root-cause determination must be "incomplete server chain"; if it exits 0, "container CA trust".
3. **Issuer line is captured.** The verbose output includes an `issuer:` line (e.g. `C=US; O=Let's Encrypt; CN=YR2`) consistent with the CA's published chains at https://letsencrypt.org/certificates/.
4. **Fix targets the fullchain file.** Confirm the TLS terminator's certificate config points at a file containing leaf + intermediates (`openssl x509 -in fullchain.pem` shows the leaf; `grep -c 'BEGIN CERTIFICATE' fullchain.pem` returns ≥ 2).
5. **Post-fix verification passes.** Re-run `docker exec <container> curl -Iv https://<host>:<port>/`; curl exits 0 and reports successful verification.
6. **Client recovers.** The original client's logs (e.g. Hermes Home Assistant adapter) show a successful connection with no `SSLCertVerificationError`, and no TLS verification was disabled anywhere (`ssl_verify: false` absent from config).