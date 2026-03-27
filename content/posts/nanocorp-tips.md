---
title: "[Tips] NanoCorp - HTB Medium"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Tips and hints to solve this machine — no spoilers!"
summary: "Medium |  Linux | Tips Only"
tags:
  - "HTB"
  - "Linux"
  - "Medium"
  - "HackTheBox"
categories:
  - "HackTheBox"
series:
  - "HackTheBox"
weight: 5
ShowToc: true
TocOpen: false

cover:
  image: "/images/covers/machine-nanocorp.svg"
  alt: "medium linux writeup"
  relative: false
---


---

## Approach

This is a **tips-only** guide — no flags, no copy-paste commands.
The full writeup will be published once the machine retires on HackTheBox.

---

## Reconnaissance Tips

Start with a comprehensive port scan. Key services to investigate:

- Port **53** → DNS
- Port **88** → Kerberos
- Port **135** → MSRPC
- Port **389** → LDAP
- Port **445** → SMB
- Port **464** → kpasswd5

## Enumeration Tips

- Don't forget to check for **virtual hosts** and add entries to `/etc/hosts`
- Look carefully at the **API endpoints**

## Exploitation Tips

Key techniques involved in this machine:

- API enumeration / exploitation
- Active Directory enumeration (BloodHound)
- CVE exploitation
- Credential hunting
- Exploitation
- Kerberos attacks
- LDAP enumeration
- Password cracking
- Port scanning / Service enumeration
- Privilege Escalation
- Remote Code Execution
- Reverse Shell
- SMB enumeration
- Sudo misconfiguration

> **Hint:** Research known vulnerabilities for the services you find. Public CVEs are relevant here.

## Privilege Escalation Tips

- Check what you can run with `sudo -l`
- Enumerate **configuration files** for hardcoded credentials
- This is an **Active Directory** environment — enumerate thoroughly

---

> The **full writeup** with detailed commands and walkthrough will be published when this machine retires.
> Until then, try to solve it yourself using these hints!
