# Tests — Manual Checklist

1. **Key has no passphrase.** On the controller, run `ssh-keygen -y -P "" -f ~/.ssh/hermes_pi` — it must print the public key with no passphrase prompt.

2. **Tailscale peers see each other.** `tailscale status` on the controller lists the remote host with a `100.x.x.x` address and status "idle" or "active" (not "offline", not absent).

3. **SSH connects without password.** `ssh -i ~/.ssh/hermes_pi PI_USERNAME@100.x.x.x "echo ok"` prints `ok` with no password prompt and exit code 0.

4. **sshd persistence is configured (non-destructive check).** On the remote host, run `systemctl is-enabled ssh` (or `sshd`) — must print `enabled`. On Windows, `powershell -Command "(Get-Service sshd).StartType"` must print `Automatic`. Do not reboot to test this; the is-enabled check is sufficient and avoids risking access to a remote machine.

5. **SCP works both ways.** Push a file with `scp -i <key> ./testfile user@host:/tmp/`, pull it back to a different name, and `diff` the two — they must be identical.

6. **authorized_keys is correct (read-only check).** On the remote host, `ls -l ~/.ssh/authorized_keys` shows the remote user as owner and mode `600`. On Windows with an admin user, `icacls "C:\ProgramData\ssh\administrators_authorized_keys"` lists only SYSTEM and Administrators. Do not move or modify keys to test the redirect behavior — verify by reading `sshd_config` for a `Match Group administrators` block instead.