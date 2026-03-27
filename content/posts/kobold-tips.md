---
title: "[Tips] Kobold - HTB Easy"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Tips and hints to solve this machine — no spoilers!"
summary: "Easy |  Linux | Tips Only"
tags:
  - "HTB"
  - "Linux"
  - "Easy"
  - "HackTheBox"
categories:
  - "HackTheBox"
series:
  - "HackTheBox"
weight: 15
ShowToc: true
TocOpen: false

cover:
  image: "/images/covers/machine-kobold.svg"
  alt: "easy linux writeup"
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

- Don't forget to check for **virtual hosts** and add entries to `/etc/hosts`
- Try **subdomain enumeration** — there may be hidden services
- Look carefully at the **API endpoints**

## Exploitation Tips

Key techniques involved in this machine:

- API enumeration / exploitation
- CVE exploitation
- Docker / Container exploitation
- Exploitation
- Local File Inclusion
- Port scanning / Service enumeration
- Privilege Escalation
- Remote Code Execution
- Reverse Shell
- SSH access
- Subdomain enumeration
- Sudo misconfiguration
- Virtual host discovery

> **Hint:** Research known vulnerabilities for the services you find. Public CVEs are relevant here.

## Privilege Escalation Tips

- Check what you can run with `sudo -l`
- Enumerate **configuration files** for hardcoded credentials
- Pay attention to **Docker/containers** on the system

---

> The **full writeup** with detailed commands and walkthrough will be published when this machine retires.
> Until then, try to solve it yourself using these hints!
