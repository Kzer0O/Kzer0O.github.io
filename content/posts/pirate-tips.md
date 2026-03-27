---
title: "[Tips] Pirate - HTB Hard"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Tips and hints to solve this machine — no spoilers!"
summary: "Hard |  Windows | Active Directory chain: RBCD, gMSA, SPN Hijacking, Constrained Delegation | Tips Only"
tags:
  - "HTB"
  - "Windows"
  - "Hard"
  - "Active Directory"
  - "Kerberos"
  - "NTLM Relay"
  - "RBCD"
  - "gMSA"
  - "SPN Hijacking"
  - "HackTheBox"
categories:
  - "HackTheBox"
series:
  - "HackTheBox"
weight: 1
ShowToc: true
TocOpen: false

cover:
  image: "/images/covers/machine-pirate.svg"
  alt: "hard windows writeup"
  relative: false
---
> **OS:** Windows Server 2019 | **Difficulté:** Hard | **IP:** 10.10.XX.XX | **Domain:** pirate.htb

---

## Approach

This is a **tips-only** guide — no flags, no copy-paste commands.
The full writeup will be published once the machine retires on HackTheBox.

---

## Reconnaissance Tips

Start with a comprehensive port scan. Key services to investigate:

- Port **53** → DNS
- Port **80** → HTTP
- Port **88** → Kerberos
- Port **445** → SMB
- Port **5985** → WinRM
- Port **2179** → vmrdp

## Enumeration Tips

- Don't forget to check for **virtual hosts** and add entries to `/etc/hosts`
- Look carefully at the **API endpoints**

## Exploitation Tips

Key techniques involved in this machine:

- API enumeration / exploitation
- Active Directory enumeration (BloodHound)
- Credential hunting
- Kerberos attacks
- LDAP enumeration
- Pivoting / Tunneling
- Port scanning / Service enumeration
- Remote Code Execution
- SMB enumeration
- SSH Tunneling / Port Forwarding
- Sudo misconfiguration

## Privilege Escalation Tips

- Check what you can run with `sudo -l`
- Some services may only be accessible **locally** — think tunneling
- Enumerate **configuration files** for hardcoded credentials
- This is an **Active Directory** environment — enumerate thoroughly

---

> The **full writeup** with detailed commands and walkthrough will be published when this machine retires.
> Until then, try to solve it yourself using these hints!
