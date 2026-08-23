---
name: cross-country-ssh-tailscale-agent-remote-control
description: Establish key-based SSH remote shell and file control of a machine in another network using Tailscale, with no port forwarding, and verify remote command execution and SCP transfer
category: infrastructure
---

# Cross-Country SSH Remote Control via Tailscale

## Goal

Establish secure, key-based SSH access from a controller machine to a remote host on a different network (e.g., a Raspberry Pi in another country) using Tailscale as a private overlay network, with no router port forwarding. Verify remote command execution and SCP file transfer, and record the connection details for reuse.

## Inputs

- SSH username on the remote host (obtain via `whoami` in step 3)
- Tailscale IPv4 address of the remote host (`100.x.x.x`, obtain via `tailscale ip -4` in step 3)
- A Tailscale account that both devices will sign into (must be the same account on both)
- Shell access to the remote host during setup (existing agent connection, local console, or any working channel)
- On the controller: ability to run `ssh-keygen` and `ssh` (OpenSSH client; built into Windows 10+ and macOS)

## Steps

1. Install Tailscale on the controller machine from https://tailscale.com/download and sign in. Confirm it is up with `tailscale status`.

2. Generate a dedicated SSH key with no passphrase (required for automated connections):
   `ssh-keygen -t ed25519 -f ~/.ssh/hermes_pi` — press Enter twice at the passphrase prompts. Display and copy the contents of `~/.ssh/hermes_pi.pub`. Never share the private key `hermes_pi`.

3. On the remote host (via existing agent connection or shell), install Tailscale and enable SSH:
   - `curl -fsSL https://tailscale.com/install.sh | sh`
   - `sudo tailscale up` — open the sign-in link it prints and use the same account as the controller
   - Verify the SSH server is installed and enabled. Check which service unit exists (`systemctl list-unit-files | grep -E '^ssh(d)?\.service'`); on minimal images install openssh-server first (`sudo apt-get install -y openssh-server` on Debian/Ubuntu). Then enable it: `sudo systemctl enable --now ssh` (or `sshd` if that is the unit name on this host)
   - `whoami` and `tailscale ip -4` — record the username and the `100.x.x.x` address

4. Add the controller's public key to the remote user's `~/.ssh/authorized_keys` with correct permissions and ownership:
   - `mkdir -p ~/.ssh && chmod 700 ~/.ssh`
   - Append the copied public key line to `~/.ssh/authorized_keys`
   - `chmod 600 ~/.ssh/authorized_keys && chown "$USER":"$USER" ~/.ssh/authorized_keys`
   - Verify: `ls -l ~/.ssh/authorized_keys` shows the remote user as owner and `-rw-------`

5. Test from the controller:
   `ssh -i ~/.ssh/hermes_pi PI_USERNAME@100.x.x.x`
   If it connects without a password, key-based SSH over Tailscale works. If any client application needs to use this connection, configure it with host `PI_USERNAME@100.x.x.x`, the default port (22), and the identity file path — the SSH command above is the canonical invocation and the source of truth.

6. For Windows remote hosts, install and start the OpenSSH server:
   - Preferred (supported) install: `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` in an elevated PowerShell
   - Fallback (manual GitHub zip, used when the capability is unavailable): extract OpenSSH to `C:\Program Files\OpenSSH`, then run `.\install-sshd.ps1` from that directory in an elevated PowerShell
   - In both cases: `Set-Service sshd -StartupType Automatic; Start-Service sshd`
   - Create the inbound firewall rule if missing: `New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22`
   - Note: for users in the Administrators group, sshd_config's `Match Group administrators` block redirects authorized keys to `C:\ProgramData\ssh\administrators_authorized_keys`, not `~/.ssh/authorized_keys`. Put the key there and fix ACLs so only SYSTEM and Administrators have access, with inheritance removed.

7. Verify bidirectional capability and save the connection details as a reusable note: the SSH invocation (`ssh -i <key> user@100.x.x.x`), how to run a remote command (`ssh -i <key> user@host "command"`), and how to push/pull files (`scp -i <key> local user@host:remote` and `scp -i <key> user@host:remote local`).

## Outputs

- Working key-based SSH from controller to remote host over Tailscale (no public exposure, no port forwarding)
- Verified remote command execution and SCP file transfer capability
- A saved note/skill documenting the SSH invocation, key path, and remote host addressing

## Failure modes

- Windows admin-group users redirect authorized_keys to `C:\ProgramData\ssh\administrators_authorized_keys`, causing key auth to fail against `~/.ssh/authorized_keys`
- ACL/inheritance issues on the Windows authorized_keys file (must be SYSTEM + Administrators only, no inherited permissions)
- SSH key generated with a passphrase, blocking automated connections
- Tailscale sign-in uses different accounts on the two devices — they will not see each other
- sshd not enabled/persisted across reboots on the remote host (`systemctl enable` skipped, or on Windows `Set-Service sshd -StartupType Automatic` skipped)
- Missing inbound firewall rule on Windows (port 22) — sshd runs but connections time out
- Remote host has no sshd installed (minimal images) — `systemctl enable --now ssh` fails; install openssh-server first
- `authorized_keys` owned by root or wrong user, or permissions too open — sshd silently refuses the key

## Source

Discord thread "Hermes agent desktop not connecting to the backend on Linux raspberry pi", channel 1485307775444844625, message 1539759268201496616, 2026-08-23. URL: https://discord.com/channels/1053877538082538074/1485307775444844625/1539759268201496616