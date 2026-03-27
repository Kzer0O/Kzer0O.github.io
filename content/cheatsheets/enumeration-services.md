---
title: "Service Enumeration Cheatsheet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Service Enumeration Cheatsheet"
summary: "Enumeration | Service Enumeration Cheatsheet"
tags:
  - "Enumeration"
  - "Recon"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "Enumeration"
ShowToc: true
TocOpen: false

cover:
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## SMB (445/139)
```bash
smbclient -L //<IP> -N                    # Liste shares (anonymous)
smbclient //<IP>/<share> -N               # Connexion anonymous
smbmap -H <IP>                             # Permissions
enum4linux -a <IP>                         # Enum complète
crackmapexec smb <IP> --shares             # Shares
crackmapexec smb <IP> --users              # Users
```

## FTP (21)
```bash
ftp <IP>                                   # anonymous/anonymous
wget -r ftp://anonymous:@<IP>/             # Download récursif
```

## SSH (22)
```bash
ssh <user>@<IP>
ssh -i id_rsa <user>@<IP>
hydra -l <user> -P rockyou.txt ssh://<IP>
```

## DNS (53)
```bash
dig axfr @<IP> <domain>                    # Zone transfer
dig any <domain> @<IP>
dnsrecon -d <domain> -n <IP>
```

## SNMP (161)
```bash
snmpwalk -v2c -c public <IP>
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt <IP>
```

## LDAP (389/636)
```bash
ldapsearch -x -H ldap://<IP> -b "dc=domain,dc=com"
ldapsearch -x -H ldap://<IP> -s base namingcontexts
```

## NFS (2049)
```bash
showmount -e <IP>
mount -t nfs <IP>:/<share> /mnt/nfs
```

## RPC (111)
```bash
rpcclient -U "" -N <IP>
rpcinfo -p <IP>
```
