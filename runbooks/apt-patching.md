# Runbook: apt patching

Patching procedure for the Ubuntu (WSL) hosts that run [market-tracker](https://github.com/finley-matthew/market-tracker). Record each patch window in the [patch log](../README.md#patching).

## 1. Check

```bash
sudo apt update
apt list --upgradable 2>/dev/null
apt-cache policy | grep security             # security repository configured?
apt-get -s upgrade | grep -i security        # outstanding security updates
apt-get -s upgrade | grep "upgraded,"        # expect "0 to remove"
```

Use the dry run (`-s`) to find security updates: `apt list` shows only one repository per package.

## 2. Record the before state

```bash
set -o noclobber
dpkg-query -W > ~/patch-backups/pkgs_before_$(date +%F).txt
df -h /
```

## 3. Prepare the rollback

**Patch window:** snapshot the distro from PowerShell, after a scheduled run has logged:

```powershell
wsl --shutdown
wsl --export Ubuntu C:\wsl-backups\ubuntu-YYYY-MM-DD.tar
```

Restore with `wsl --import`.

**Single package:** save the installed version first, because the repository keeps only the latest version in each channel:

```bash
apt-get download <package>=<installed-version>
```

Roll back with `sudo apt install ./<file>.deb`, then `sudo apt-mark hold <package>` while investigating.

## 4. Apply

```bash
sudo apt upgrade
```

Before confirming, check the summary matches the dry run. Stop if it removes packages or asks about a configuration file.

## 5. Verify

```bash
grep -A4 "Start-Date: $(date +%F)" /var/log/apt/history.log
apt list --upgradable 2>/dev/null            # held back (often phased updates)
ls /var/run/reboot-required 2>/dev/null      # present: restart with wsl --shutdown
systemctl is-active cron
```

Run `live_price.py` by hand, confirm the next scheduled run logs, and run `gap_check.py`: the only gap should be the maintenance window.

## 6. Record

Add a row to the [patch log](../README.md#patching): date, host, change, held back, result and maintenance window.
