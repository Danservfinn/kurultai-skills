# Commands

Placeholders:
- `PI_USERNAME` — remote username from `whoami`
- `100.x.x.x` — remote Tailscale IPv4 from `tailscale ip -4`
- `~/.ssh/hermes_pi` — on Windows PowerShell use `"$env:USERPROFILE\.ssh\hermes_pi"`
- `REMOTE_PUBKEY` — the full copied line from `hermes_pi.pub`

## Step 1 — Tailscale on controller

```
tailscale status
```

## Step 2 — Generate key (controller)

```
ssh-keygen -t ed25519 -f ~/.ssh/hermes_pi
cat ~/.ssh/hermes_pi.pub        # macOS/Linux
Get-Content "$env:USERPROFILE\.ssh\hermes_pi.pub"   # Windows PowerShell
```

## Step 3 — Remote host setup (run on the remote host)

```
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
systemctl list-unit-files | grep -E '^ssh(d)?\.service'
sudo apt-get install -y openssh-server   # only if no ssh/sshd unit found
sudo systemctl enable --now ssh           # or 'sshd' per the unit name found above
whoami
tailscale ip -4
```

## Step 4 — Install public key (run on the remote host)

```
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "REMOTE_PUBKEY" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chown "$USER":"$USER" ~/.ssh/authorized_keys
ls -l ~/.ssh/authorized_keys   # must show remote user as owner, mode -rw-------
```

## Step 5 — Test from controller

```
ssh -i ~/.ssh/hermes_pi PI_USERNAME@100.x.x.x
```

## Step 6 — Windows remote host (elevated PowerShell)

```
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
# fallback if capability unavailable: extract OpenSSH zip to C:\Program Files\OpenSSH, then:
# cd "C:\Program Files\OpenSSH"; .\install-sshd.ps1
Set-Service sshd -StartupType Automatic
Start-Service sshd
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
# admin users: key goes here, ACLs = SYSTEM + Administrators only, inheritance removed:
# C:\ProgramData\ssh\administrators_authorized_keys
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "SYSTEM:F" /grant "Administrators:F"
```

## Step 7 — Verify remote execution and SCP

```
ssh -i ~/.ssh/hermes_pi PI_USERNAME@100.x.x.x "uname -a"
scp -i ~/.ssh/hermes_pi ./localfile PI_USERNAME@100.x.x.x:/tmp/
scp -i ~/.ssh/hermes_pi PI_USERNAME@100.x.x.x:/tmp/localfile ./copied-back