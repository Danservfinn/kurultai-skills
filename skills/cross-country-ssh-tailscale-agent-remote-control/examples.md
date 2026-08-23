# Examples

## Example 1: Windows laptop → Raspberry Pi in another country

Controller: Windows 11 laptop. Remote: Raspberry Pi running Hermes, physically in another country.

```
# PowerShell on Windows
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\hermes_pi"     # empty passphrase
Get-Content "$env:USERPROFILE\.ssh\hermes_pi.pub"
```

On the Pi (via existing Hermes chat connection):

```
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
systemctl list-unit-files | grep -E '^ssh(d)?\.service'   # -> ssh.service
sudo systemctl enable --now ssh
whoami          # nas_kashif
tailscale ip -4 # 100.96.160.71
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAA... hermes_pi" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys && chown nas_kashif:nas_kashif ~/.ssh/authorized_keys
```

Test from Windows:

```
ssh -i "$env:USERPROFILE\.ssh\hermes_pi" nas_kashif@100.96.160.71
```

Saves a reusable note: `ssh -i C:\Users\Itsa\.ssh\hermes_pi nas_kashif@100.96.160.71`.

## Example 2: Pi → Windows laptop (reverse direction)

Remote is a Windows 10 laptop where the user is in the Administrators group.

```
# Elevated PowerShell on Windows
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Set-Service sshd -StartupType Automatic
Start-Service sshd
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

Key goes to `C:\ProgramData\ssh\administrators_authorized_keys` (not `~/.ssh/authorized_keys`) because of the `Match Group administrators` block. Fix ACLs: Properties → Security → disable inheritance, keep SYSTEM and Administrators only.

From the Pi:

```
ssh -i ~/.ssh/hermes_to_windows Itsa@100.98.118.64 "powershell -Command Get-Date"
scp -i ~/.ssh/hermes_to_windows Itsa@100.98.118.64:C:/Users/Itsa/report.txt ./
```

## Example 3: macOS controller → remote Linux server

```
ssh-keygen -t ed25519 -f ~/.ssh/hermes_pi
ssh -i ~/.ssh/hermes_pi deploy@100.101.50.12 "uptime"
scp -i ~/.ssh/hermes_pi ./app.tar.gz deploy@100.101.50.12:/tmp/
```

If `systemctl enable --now ssh` fails with "unit not found", the host is a minimal image: `sudo apt-get install -y openssh-server`, then retry.