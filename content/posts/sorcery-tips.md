---
title: "[Tips] Sorcery - HTB Insane"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Tips and hints to solve this machine — no spoilers!"
summary: "Insane |  Linux | 13 steps from web to root through 9 Docker containers and FreeIPA | Tips Only"
tags:
  - "HTB"
  - "Linux"
  - "Insane"
  - "Cypher Injection"
  - "WebAuthn"
  - "Kafka RCE"
  - "FreeIPA"
  - "Docker"
  - "Phishing"
  - "SSSD"
  - "HackTheBox"
categories:
  - "HackTheBox"
series:
  - "HackTheBox"
weight: 0
ShowToc: true
TocOpen: false

cover:
  image: "/images/covers/machine-sorcery.svg"
  alt: "insane linux writeup"
  relative: false
---


---

## Approach

This is a **tips-only** guide — no flags, no copy-paste commands.
The full writeup will be published once the machine retires on HackTheBox.

---

## Reconnaissance Tips

Start with a comprehensive port scan to identify all exposed services.

## Enumeration Tips

- Look carefully at the **API endpoints**

## Exploitation Tips

Key techniques involved in this machine:

- API enumeration / exploitation
- Credential hunting
- Cross-Site Scripting (XSS)
- Docker / Container exploitation
- Exploitation
- FTP enumeration
- JWT token manipulation
- Kerberos attacks
- LDAP enumeration
- Password reuse
- Pivoting / Tunneling
- Port scanning / Service enumeration
- Privilege Escalation
- Remote Code Execution
- Reverse Shell
- SSH Tunneling / Port Forwarding
- SSH access
- SUID binary exploitation
- Server-Side Request Forgery
- Sudo misconfiguration

## Privilege Escalation Tips

- Check what you can run with `sudo -l`
- Look for **SUID binaries**
- Monitor **cron jobs** and scheduled tasks
- Think about **password reuse** across services
- Some services may only be accessible **locally** — think tunneling
- Enumerate **configuration files** for hardcoded credentials
- Pay attention to **Docker/containers** on the system

---

> The **full writeup** with detailed commands and walkthrough will be published when this machine retires.
> Until then, try to solve it yourself using these hints!
